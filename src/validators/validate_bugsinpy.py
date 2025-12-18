import configparser
import contextlib
import itertools
import json
import os
import re
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

from ..configs import (
    bugsinpy_bin_dir,
    bugsinpy_gen_dir,
    bugsinpy_tmp_dir,
)
from .check_python_syntax import get_valid_python

gen_dir = bugsinpy_gen_dir
bugs_metadata_file = "BugsInPy.jsonl"
model = "multimend"
output_dir = gen_dir / f"outputs-{model}"
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


def get_hunk_candidates(df: pd.DataFrame, hunk: int) -> pd.DataFrame:
    """Returns the subset of `df` containing candidate patches for a specific hunk of a bug"""
    return df.loc[df["hunk"] == hunk]


def get_candidates(df: pd.DataFrame, bugid: str) -> pd.DataFrame:
    """Returns the subset of `df` containing candidate patches for a specific bugid and all its hunks"""
    return df.loc[df["bugid"] == bugid]


def insert_patch(patch, source_file_path, target_file_path, bug_line, bug_len, indent):
    with open(source_file_path, encoding="cp1256") as file:
        lines = file.readlines()
    if bug_len == 0:
        lines.insert(bug_line, textwrap.indent(patch, indent) + "\n")
    else:
        lines[bug_line - 1 : (bug_line - 1) + bug_len] = (
            textwrap.indent(patch, indent) + "\n"
        )

    try:
        with open(target_file_path, "w", encoding="cp1256") as file:
            file.writelines(lines)
    except UnicodeEncodeError:
        with open(target_file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)


class Status(Enum):
    PLAUSIBLE = auto()
    COMPILABLE = auto()
    TIMEOUT = auto()
    UNCOMPILABLE = auto()


def parse_test_output(output: str) -> int | None:
    def parse_single_session(session_text: str):
        error_patterns = [
            r"= ERRORS =",
            r"ERROR collecting",
            r"ERROR:",
            r"ImportError while",
            r"SyntaxError:",
            r"NameError:",
            r": command not found",
        ]

        for pat in error_patterns:
            if pat in session_text:
                return None

        # Extract number of failing tests
        # Pytest: "2 failed"
        match = re.search(r"(\d+)\s+failed", session_text)
        if match:
            return int(match.group(1))

        # Unittest: "failures=2"
        match = re.search(r"failures=(\d+)", session_text)
        if match:
            return int(match.group(1))

        if re.search(r"\b(?:passed|OK)\b", session_text, re.IGNORECASE):
            return 0
        else:
            return None

    failed_count = 0

    # Split output by "RUN EVERY COMMAND" markers to separate test sessions
    sessions = re.split(r"RUN EVERY COMMAND\s+\d+", output)[1:]

    for session in sessions:
        result = parse_single_session(session)
        if result is None:
            return None
        else:
            failed_count += result

    return failed_count


def run_tests(
    project_name: str, work_dir: Path, timeout=int | None
) -> subprocess.CompletedProcess[str]:
    work_dir /= project_name
    cmd = [bugsinpy_bin_dir / "bugsinpy-test", "-w", work_dir]
    result = subprocess.run(
        cmd,
        text=True,
        timeout=timeout,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result


def run_tests_for_multi(bugid: str, project_dir: Path) -> tuple[Status, int | None]:
    timeout = 120  # seconds

    try:
        result = run_tests(bugid.split()[0], project_dir, timeout=timeout)
    except subprocess.TimeoutExpired:
        return Status.TIMEOUT, None

    failed_tests = parse_test_output(result.stdout)

    if failed_tests == 0:
        return Status.PLAUSIBLE, 0
    elif failed_tests is None:
        return Status.UNCOMPILABLE, None
    else:
        return Status.COMPILABLE, failed_tests


def apply_patch(cp_df: pd.DataFrame, bugid: str, hunks: list) -> Optional[pd.DataFrame]:
    # Load if already processed
    save_file_path = save_state_dir / f"{bugid}.jsonl"
    if save_file_path.exists():
        return

    project_name, bug_number = bugid.split()

    # Checkout the buggy version
    checkout_dir = bugsinpy_tmp_dir / f"{project_name}-buggy"
    checkout_source(project_name, bug_number, True, checkout_dir)
    compile_project(project_name, checkout_dir)
    fix_environment(project_name, checkout_dir)

    if len(hunks) == 1:
        hunk = hunks[0]
        bug_hunk_subset_df = get_hunk_candidates(cp_df, 0)
        cp_df = bug_hunk_subset_df.copy()

        target_file_path = checkout_dir / hunk["source_path"]
        bug_line, bug_len = hunk["removed_line_numbers_range"]

        # Copy initial file to a temp directory
        source_file_path = bugsinpy_tmp_dir / "sources" / bugid / hunk["source_path"]
        source_file_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target_file_path, source_file_path)

        indent_hunk = "\n".join(
            [line for line in hunk["added_lines"].splitlines() if line.strip()]
        )
        indent_size = len(indent_hunk) - len(indent_hunk.lstrip(" \t"))
        indent = indent_hunk[:indent_size]

        for index, patch in bug_hunk_subset_df["decoded_sequences"].items():
            patch = get_valid_python(patch)

            insert_patch(
                patch, source_file_path, target_file_path, bug_line, bug_len, indent
            )

            start_timer = timeit.default_timer()
            status, failed_count = run_tests_for_multi(bugid, checkout_dir)
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

        for hunk in hunks:
            target_file_path = checkout_dir / hunk["source_path"]
            source_file_path = (
                bugsinpy_tmp_dir / "sources" / bugid / hunk["source_path"]
            )
            source_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target_file_path, source_file_path)

        # Loop to iterate on dataframe rows
        for index, patches in new_cp_df["decoded_sequences"].items():
            bugs_lens = defaultdict(list)
            # Loop to apply patches to each hunk
            for hunk_num, (hunk, patch) in enumerate(
                reversed(list(zip(hunks, patches)))
            ):
                patch = get_valid_python(patch)

                target_file_path = checkout_dir / hunk["source_path"]
                bug_line, bug_len = hunk["removed_line_numbers_range"]
                source_file_path = (
                    bugsinpy_tmp_dir / "sources" / bugid / hunk["source_path"]
                )

                indent_hunk = "\n".join(
                    [line for line in hunk["added_lines"].splitlines() if line.strip()]
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

            # call the testing infrastructure
            start_timer = timeit.default_timer()
            status, failed_count = run_tests_for_multi(bugid, checkout_dir)
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

        ###################################################################

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
                agg_mapping[col] = list  # lambda x: list(x.unique())

        template_df = cp_df.groupby("hunk").agg("first").reset_index()
        template_df = template_df.groupby("bugid").agg(agg_mapping).reset_index()
        assert (
            template_df["source"].apply(len).item()
            == template_df["target"].apply(len).item()
            == template_df["hunk"].apply(len).item()
        )

        # Revert modified files to their original state
        for hunk in hunks:
            target_file_path = checkout_dir / hunk["source_path"]
            source_file_path = (
                bugsinpy_tmp_dir / "sources" / bugid / hunk["source_path"]
            )
            shutil.copyfile(source_file_path, target_file_path)

        # List to store extracted multi-hunk patches
        multi_patches_list = []

        # Compute the number of initial failing tests
        _, running_failed_count = run_tests_for_multi(bugid, checkout_dir)
        if not running_failed_count:
            running_failed_count = sys.maxsize

        running_plausible_df = None

        for i in range(len(hunks)):
            if running_failed_count == 0:
                break
            hunk_cp_df = get_hunk_candidates(cp_df, i)

            for row in hunk_cp_df.itertuples():
                if i == 0:
                    row_df = pd.DataFrame(
                        columns=template_df.columns, data=deepcopy(template_df.values)
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
                    patch = get_valid_python(patch)

                    target_file_path = checkout_dir / hunk["source_path"]
                    bug_line, bug_len = hunk["removed_line_numbers_range"]

                    source_file_path = (
                        bugsinpy_tmp_dir / "sources" / bugid / hunk["source_path"]
                    )

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
                status, failed_count = run_tests_for_multi(bugid, checkout_dir)
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


def compile_project(project_name: str, work_dir: Path):
    work_dir /= project_name

    # Extract Python version
    with open(work_dir / "bugsinpy_bug.info") as file:
        python_version = ".".join(next(file).split("=")[1].strip('"').split(".")[:2])

    full_python_version = max(
        v
        for v in subprocess.check_output(
            ["pyenv", "versions", "--bare"], text=True
        ).splitlines()
        if v.startswith(f"{python_version}.")
    )
    env = os.environ.copy()
    env["PATH"] = (
        f"{os.environ['PYENV_ROOT']}/versions/{full_python_version}/bin:" + env["PATH"]
    )

    assert (
        f"{python_version}."
        in subprocess.run(
            ["python", "-V"], env=env, capture_output=True, text=True, check=True
        ).stdout
    ), f"Python version not set correctly: {work_dir.name}, {python_version}"

    cmd = [bugsinpy_bin_dir / "bugsinpy-setupenv", "-w", work_dir]
    subprocess.run(
        cmd, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


def fix_environment(project_name: str, work_dir: Path):
    work_dir /= project_name

    if project_name == "cookiecutter":
        if not (work_dir / "tox.ini").exists():
            return
        config = configparser.ConfigParser()
        config.read(work_dir / "tox.ini")
        if "tox" in config:
            config["tox"]["envlist"] = "\n    py36"

            with open(work_dir / "tox.ini", "w") as file:
                config.write(file)


def checkout_source(
    project_id: str, bug_id: str, buggy_version: bool, checkout_dir: Path
) -> None:
    lock_file = checkout_dir / project_id / ".git/index.lock"
    if lock_file.exists():
        lock_file.unlink()

    cmd = [
        bugsinpy_bin_dir / "bugsinpy-checkout",
        "-p",
        project_id,
        "-i",
        bug_id,
        "-v",
        str(0) if buggy_version else str(1),
        "-w",
        checkout_dir,
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def partition_bugs(bugs_metadata: dict) -> list[dict]:
    """Parition bugs for multiprocessing so no two bugs from a projects
    are in a same partition to avoid conflict in Docker containers.
    """

    project_groups = defaultdict(list)
    for key, value in bugs_metadata.items():
        project_groups[key.split()[0]].append(key)

    partitions = [
        {key: bugs_metadata[key] for key in grouped_keys if key is not None}
        for grouped_keys in itertools.zip_longest(*project_groups.values())
    ]

    return partitions


def main():
    n_jobs = 4

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

    save_state_dir.mkdir(exist_ok=True)

    for partition in partition_bugs(bugs_metadata):
        with tqdm_joblib(tqdm(total=len(partition), disable=False)):
            Parallel(n_jobs=n_jobs, backend="multiprocessing")(
                delayed(apply_patch)(
                    deepcopy(get_candidates(candidate_patches_df, bugid)), bugid, hunks
                )
                for bugid, hunks in partition.items()
            )

    cp_dfs = [
        pd.read_json(cp, orient="records", lines=True)
        for cp in sorted(save_state_dir.iterdir())
    ]
    concatenated_cp_df = pd.concat(cp_dfs)

    concatenated_cp_df.to_json(
        output_dir / f"plausible_candidates_{output_size}.jsonl",
        orient="records",
        lines=True,
    )

    bugs_with_plausible_patch = (
        concatenated_cp_df.groupby("bugid")["plausible"].any().groupby("bugid").any()
    )
    print(bugs_with_plausible_patch)
    print(bugs_with_plausible_patch.value_counts())


if __name__ == "__main__":
    main()
