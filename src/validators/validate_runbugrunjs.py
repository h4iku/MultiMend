import contextlib
import json
import shutil
import subprocess
import sys
import textwrap
import timeit
from collections import ChainMap, defaultdict
from copy import deepcopy
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm

from ..configs import runbugrun_data_dir, runbugrunjs_gen_dir

gen_dir = runbugrunjs_gen_dir
bugs_metadata_file = "RunBugRun-JS.jsonl"
model = "multimend"
output_dir = gen_dir / f"outputs-{model}"
temp_dir = output_dir / "temp"
save_state_dir = output_dir / "save-state"
output_size = 100

rem_file_path = gen_dir / "rem.txt"
add_file_path = gen_dir / "add.txt"

with (
    open(rem_file_path) as rem_file,
    open(add_file_path) as add_file,
):
    sources = [src.strip() for src in rem_file]
    targets = [tgt.strip() for tgt in add_file]


@contextlib.contextmanager
def working_environment(bugid: str):
    # Split the bugid to get file names
    project_dir = runbugrun_data_dir / "jsbugs" / bugid

    # Copy files to a working directory
    project_copy_dir = temp_dir / bugid
    copy_dataset_files(project_dir, project_copy_dir)

    target_file_path = project_copy_dir / "buggy.js"

    # Copy initial file to a temp directory
    source_file_path = temp_dir / "sources" / bugid / "buggy.js"
    source_file_path.parent.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(target_file_path, source_file_path)

    try:
        yield project_copy_dir, source_file_path, target_file_path
    finally:
        pass
        shutil.rmtree(project_copy_dir)
        shutil.rmtree(source_file_path.parent)


@contextlib.contextmanager
def tqdm_joblib(tqdm_object):
    """Context manager to patch joblib to report into tqdm progress bar given as argument"""

    def tqdm_print_progress(self):
        if self.n_completed_tasks > tqdm_object.n:
            n_completed = self.n_completed_tasks - tqdm_object.n
            tqdm_object.update(n=n_completed)

    original_print_progress = joblib.parallel.Parallel.print_progress
    joblib.parallel.Parallel.print_progress = tqdm_print_progress

    try:
        yield tqdm_object
    finally:
        joblib.parallel.Parallel.print_progress = original_print_progress
        tqdm_object.close()


def check_node_version():
    # Check Node.js installation
    try:
        node_version_string = subprocess.run(
            ["node", "-v"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Can't find `node`")
        raise e

    # I guess any newer version can also be used, but this is the version that is mentioned in the RunBugRun paper.
    assert node_version_string.startswith("v12.22."), (
        "Wrong Node.js version, needs node v12.22"
    )


def get_hunk_candidates(df: pd.DataFrame, hunk: int) -> pd.DataFrame:
    """Returns the subset of `df` containing candidate patches for a specific hunk of a bug"""
    return df.loc[df["hunk"] == hunk]


def get_candidates(df: pd.DataFrame, bugid: str) -> pd.DataFrame:
    """Returns the subset of `df` containing candidate patches for a specific bugid and all its hunks"""
    return df.loc[df["bugid"] == bugid]


def insert_patch(patch, source_file_path, target_file_path, bug_line, bug_len, indent):
    with open(source_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    if bug_len == 0:
        lines.insert(bug_line, textwrap.indent(patch, indent) + "\n")
    else:
        lines[bug_line - 1 : (bug_line - 1) + bug_len] = (
            textwrap.indent(patch, indent) + "\n"
        )

    try:
        with open(target_file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)
    except UnicodeEncodeError:
        with open(target_file_path, "w", encoding="cp1256") as file:
            file.writelines(lines)


class Status(Enum):
    PLAUSIBLE = auto()
    COMPILABLE = auto()
    TIMEOUT = auto()
    UNCOMPILABLE = auto()


def compare_output_expected(bugid: str, output: str, expected: str) -> bool:
    output = output.strip()
    expected = expected.strip()

    if bugid in ["p00100-25761", "p02729-309475", "p03059-514118"]:
        output = " ".join(
            [
                str(int(x)) if x.lstrip("+-").isdigit() else x
                for x in output.splitlines()
            ]
        )
        expected = " ".join(
            [
                str(int(x)) if x.lstrip("+-").isdigit() else x
                for x in expected.splitlines()
            ]
        )
    elif bugid == "p02380-90030":
        try:
            output_array = np.array([float(x) for x in output.splitlines()])
            expected_array = np.array([float(x) for x in expected.splitlines()])
            return np.allclose(output_array, expected_array, rtol=0, atol=1e-10)
        except Exception:
            return False

    return output == expected


def run_tests_for_multi(
    bugid: str, project_dir: Path, tests: list[tuple[Path, Path]]
) -> tuple[Status, int | None]:
    timeout = 60  # seconds

    cmd = ["node", project_dir / "buggy.js"]

    failed_count = 0

    for testcase, testcase_output in tests:
        try:
            result = subprocess.run(
                cmd,
                input=testcase,
                text=True,
                capture_output=True,
                timeout=timeout,
                encoding="utf-8",
            )
        except subprocess.TimeoutExpired:
            return Status.TIMEOUT, None

        if result.returncode != 0:
            return Status.UNCOMPILABLE, None

        if not compare_output_expected(bugid, result.stdout, testcase_output):
            failed_count += 1

    if failed_count:
        return Status.COMPILABLE, failed_count
    else:
        return Status.PLAUSIBLE, 0


def get_tests(bugid: str, project_dir: Path) -> list[tuple[str, str]]:
    tests = []
    for i in project_dir.iterdir():
        if i.name.startswith("input"):
            if bugid == "p02778-348266" and i.name in {
                f"input{x}" for x in range(103, 117)
            }:
                continue
            o = i.with_name(i.name.replace("input", "output"))
            tests.append((i.read_text(), o.read_text()))
    return tests


def apply_patch(cp_df: pd.DataFrame, bugid: str, hunks: list) -> Optional[pd.DataFrame]:
    # Check if already processed
    save_file_path = save_state_dir / f"{bugid}.jsonl"
    if save_file_path.exists():
        return

    if len(hunks) == 1:
        hunk = hunks[0]

        bug_line, bug_len = hunk["removed_line_numbers_range"]
        bug_hunk_subset_df = get_hunk_candidates(cp_df, 0)

        indent_hunk = "\n".join(
            [line for line in hunk["added_lines"].splitlines() if line.strip()]
        )
        indent_size = len(indent_hunk) - len(indent_hunk.lstrip(" \t"))
        indent = indent_hunk[:indent_size]

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            # Get tests
            tests = get_tests(bugid, project_copy_dir)

            for index, patch in bug_hunk_subset_df["decoded_sequences"].items():
                insert_patch(
                    patch, source_file_path, target_file_path, bug_line, bug_len, indent
                )

                # call the testing infrastructure
                start_timer = timeit.default_timer()
                status, failed_count = run_tests_for_multi(
                    bugid, project_copy_dir, tests
                )
                end_timer = timeit.default_timer()
                cp_df.at[index, "validation_time"] = end_timer - start_timer

                if status is Status.PLAUSIBLE:
                    cp_df.at[index, "plausible"] = True
                    cp_df.at[index, "compilable"] = True
                    break
                elif status is Status.COMPILABLE:
                    cp_df.at[index, "compilable"] = True
                elif status is Status.TIMEOUT:
                    cp_df.at[index, "timeout"] = True
                    cp_df.at[index, "compilable"] = True

        # Save intermediate state
        cp_df.to_json(save_state_dir / f"{bugid}.jsonl", orient="records", lines=True)

    else:
        agg_mapping = {
            col: "first"
            if col
            in [
                "bugid",
                "normalized_patch",
                "correct",
                "plausible",
                "compilable",
                "timeout",
                "validation_time",
            ]
            else list
            for col in cp_df.columns
        }

        new_cp_df = cp_df.groupby("normalized_patch").agg(agg_mapping)
        new_cp_df = new_cp_df[new_cp_df["hunk"].apply(len) == len(hunks)]
        new_cp_df["rank"] = new_cp_df["rank"].apply(sum)
        new_cp_df["sequences_scores"] = new_cp_df["sequences_scores"].apply(max)

        new_cp_df.sort_values(
            by=["rank", "sequences_scores"], ascending=[True, False], inplace=True
        )

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            # Get tests
            tests = get_tests(bugid, project_copy_dir)

            for index, patches in new_cp_df["decoded_sequences"].items():
                bugs_lens = defaultdict(list)

                for hunk, patch in reversed(list(zip(hunks, patches))):
                    bug_line, bug_len = hunk["removed_line_numbers_range"]

                    indent_hunk = "\n".join(
                        [
                            line
                            for line in hunk["added_lines"].splitlines()
                            if line.strip()
                        ]
                    )
                    indent_size = len(indent_hunk) - len(indent_hunk.lstrip(" \t"))
                    indent = indent_hunk[:indent_size]

                    insert_patch(
                        patch,
                        target_file_path
                        if target_file_path in bugs_lens
                        else source_file_path,
                        target_file_path,
                        bug_line,
                        bug_len,
                        indent,
                    )

                    bugs_lens[target_file_path].append(bug_len)

                # Call the testing infrastructure
                start_timer = timeit.default_timer()
                status, failed_count = run_tests_for_multi(
                    bugid, project_copy_dir, tests
                )
                end_timer = timeit.default_timer()
                new_cp_df.at[index, "validation_time"] = end_timer - start_timer

                if status is Status.PLAUSIBLE:
                    new_cp_df.at[index, "plausible"] = True
                    new_cp_df.at[index, "compilable"] = True
                    break
                elif status is Status.COMPILABLE:
                    new_cp_df.at[index, "compilable"] = True
                elif status is Status.TIMEOUT:
                    new_cp_df.at[index, "timeout"] = True
                    new_cp_df.at[index, "compilable"] = True

        if not new_cp_df.empty and new_cp_df["plausible"].any():
            new_cp_df.to_json(
                save_state_dir / f"{bugid}.jsonl", orient="records", lines=True
            )
            return

        #######################################################################

        agg_mapping = {}
        for col in cp_df.columns:
            if col in [
                "correct",
                "plausible",
                "compilable",
                "timeout",
                "validation_time",
            ]:
                agg_mapping[col] = "first"
            elif col in [
                "checkpoint",
                "decoded_sequences",
                "normalized_patch",
                "sequences_scores",
                "rank",
                "exact_match",
            ]:
                agg_mapping[col] = lambda x: []
            elif col != "bugid":
                agg_mapping[col] = list

        template_df = cp_df.groupby("hunk").agg("first").reset_index()
        template_df = template_df.groupby("bugid").agg(agg_mapping).reset_index()
        assert (
            template_df["source"].apply(len).item()
            == template_df["target"].apply(len).item()
            == template_df["hunk"].apply(len).item()
        )

        # List to store extracted multi-hunk patches
        multi_patches_list = []

        running_plausible_df = None

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            _, running_failed_count = run_tests_for_multi(
                bugid, project_copy_dir, tests
            )
            if not running_failed_count:
                running_failed_count = sys.maxsize

            for i in range(len(hunks)):
                if running_failed_count == 0:
                    break
                hunk_cp_df = get_hunk_candidates(cp_df, i)

                for row in hunk_cp_df.itertuples():
                    if i == 0:
                        row_df = pd.DataFrame(
                            columns=template_df.columns,
                            data=deepcopy(template_df.values),
                        )
                    else:
                        row_df = pd.DataFrame(
                            columns=running_plausible_df.columns,
                            data=deepcopy(running_plausible_df.values),
                        )
                    row_df.at[0, "checkpoint"].append(row.checkpoint)
                    row_df.at[0, "decoded_sequences"].append(row.decoded_sequences)
                    row_df.at[0, "normalized_patch"].append(row.normalized_patch)
                    row_df.at[0, "sequences_scores"].append(row.sequences_scores)
                    row_df.at[0, "rank"].append(row.rank)
                    row_df.at[0, "exact_match"].append(row.exact_match)

                    assert (v := len(row_df.at[0, "decoded_sequences"])) == i + 1, (
                        f"Hunk and patch count mismatch: {i + 1}, {v}"
                    )

                    bugs_lens = defaultdict(list)

                    # When we are iterating over previous hunks, we don't have to change later hunks
                    for hunk, patch in reversed(
                        list(zip(hunks, row_df["decoded_sequences"].item()))
                    ):
                        bug_line, bug_len = hunk["removed_line_numbers_range"]

                        indent_hunk = "\n".join(
                            [
                                line
                                for line in hunk["added_lines"].splitlines()
                                if line.strip()
                            ]
                        )
                        indent_size = len(indent_hunk) - len(indent_hunk.lstrip(" \t"))
                        indent = indent_hunk[:indent_size]

                        insert_patch(
                            patch,
                            target_file_path
                            if target_file_path in bugs_lens
                            else source_file_path,
                            target_file_path,
                            bug_line,
                            bug_len,
                            indent,
                        )

                        bugs_lens[target_file_path].append(bug_len)

                    # Call the testing infrastructure
                    start_timer = timeit.default_timer()
                    status, failed_count = run_tests_for_multi(
                        bugid, project_copy_dir, tests
                    )
                    end_timer = timeit.default_timer()
                    row_df.at[0, "validation_time"] = end_timer - start_timer

                    if status is Status.PLAUSIBLE:
                        row_df.at[0, "plausible"] = True
                        row_df.at[0, "compilable"] = True
                        running_failed_count = 0
                        multi_patches_list.append(row_df)
                        break
                    elif status is Status.COMPILABLE:
                        row_df.at[0, "compilable"] = True
                        if failed_count and failed_count < running_failed_count:
                            running_failed_count = failed_count
                            running_plausible_df = pd.DataFrame(
                                columns=row_df.columns, data=deepcopy(row_df.values)
                            )
                            multi_patches_list.append(row_df)
                            break
                    elif status is Status.TIMEOUT:
                        row_df.at[0, "timeout"] = True
                        row_df.at[0, "compilable"] = True

                    multi_patches_list.append(row_df)

                else:
                    row_df.at[0, "checkpoint"][-1] = "manual"
                    row_df.at[0, "decoded_sequences"][-1] = row.source
                    row_df.at[0, "normalized_patch"][-1] = row.normalized_source
                    row_df.at[0, "sequences_scores"][-1] = None
                    row_df.at[0, "rank"][-1] = None
                    row_df.at[0, "exact_match"][-1] = False
                    running_plausible_df = pd.DataFrame(
                        columns=row_df.columns, data=deepcopy(row_df.values)
                    )

        # Merge and save to disk
        new_cp_df = pd.concat(
            [
                new_cp_df if not new_cp_df.empty else None,
                *multi_patches_list,
            ]
        )

        if not new_cp_df.empty:
            new_cp_df.to_json(
                save_state_dir / f"{bugid}.jsonl", orient="records", lines=True
            )


def copy_dataset_files(dataset_dir, temp_dataset_dir):
    shutil.copytree(
        dataset_dir,
        temp_dataset_dir,
        dirs_exist_ok=False,
        ignore=shutil.ignore_patterns(".*"),
    )


def main():
    check_node_version()

    n_jobs = 6

    with open(gen_dir / bugs_metadata_file) as meta_file:
        bugs_metadata = ChainMap(*[json.loads(line) for line in meta_file][::-1])

    candidate_patches_df = pd.read_json(
        output_dir / f"final_candidates_{output_size}.jsonl",
        orient="records",
        lines=True,
    )
    candidate_patches_df["plausible"] = False
    candidate_patches_df["compilable"] = False
    candidate_patches_df["timeout"] = False
    candidate_patches_df["validation_time"] = np.nan

    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True)
    save_state_dir.mkdir(parents=True, exist_ok=True)

    with tqdm_joblib(tqdm(total=len(bugs_metadata), disable=False)):
        Parallel(n_jobs=n_jobs, backend="loky")(
            delayed(apply_patch)(
                deepcopy(get_candidates(candidate_patches_df, bugid)), bugid, hunks
            )
            for bugid, hunks in bugs_metadata.items()
        )

    cp_dfs = [
        pd.read_json(cp, orient="records", lines=True)
        for cp in sorted(save_state_dir.iterdir())
    ]
    concatenated_cp_df = pd.concat(cp_dfs, ignore_index=True)

    bugs_with_plausible_patch = (
        concatenated_cp_df.groupby("bugid")["plausible"].any().groupby("bugid").any()
    )
    print(bugs_with_plausible_patch)
    print(bugs_with_plausible_patch.value_counts())
    concatenated_cp_df.to_json(
        output_dir / f"plausible_candidates_{output_size}.jsonl",
        orient="records",
        lines=True,
    )


if __name__ == "__main__":
    main()
