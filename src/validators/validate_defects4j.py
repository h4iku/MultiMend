import contextlib
import json
import multiprocessing as mp
import re
import shlex
import shutil
import subprocess
import threading
import timeit
from collections import ChainMap, defaultdict
from copy import deepcopy
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import psutil
from joblib import Parallel, delayed
from tqdm import tqdm

from ..configs import d4j_bin, d4j_gen_dir

gen_dir = d4j_gen_dir
gen_dir = gen_dir.parent / "Defects4J"
bugs_metadata_file = "Defects4J.jsonl"
model = "multimend"
output_dir = gen_dir / f"outputs-{model}"
d4j_tmp_dir = output_dir / "temp"
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


def check_java_version():
    try:
        java_version_string = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, check=True
        ).stderr
    except subprocess.CalledProcessError as e:
        print("Can't find `java`")
        raise e

    pattern = r'"(\d+\.\d+).*"'
    java_version = re.search(pattern, java_version_string).groups()[0]

    assert java_version == "1.8", "Wrong Java version, needs Java 8"


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
        lines.insert(bug_line, indent + patch + "\n")
    else:
        lines[bug_line - 1 : (bug_line - 1) + bug_len] = indent + patch + "\n"

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


def run_tests_for_multi(bugid: str, project_dir: Path) -> tuple[Status, int | None]:
    timeout = 300  # seconds

    compile_result = run_d4j_cmd(f"compile -w {project_dir}")
    if compile_result.returncode != 0:
        return Status.UNCOMPILABLE, None

    # Run relevant tests
    result = run_d4j_cmd(f"test -r -w {project_dir}", timeout=timeout)
    if result.returncode == 124:
        return Status.TIMEOUT, None
    elif result.stdout.strip() != "Failing tests: 0":
        if result.stdout:
            failed_count = int(result.stdout.splitlines()[0].split(": ")[1])
        else:
            failed_count = None
        return Status.COMPILABLE, failed_count

    return Status.PLAUSIBLE, 0


def run_tests(bugid: str, project_dir: Path, trigger_tests: list[str]) -> Status:
    timeout = 300  # seconds

    compile_result = run_d4j_cmd(f"compile -w {project_dir}")
    if compile_result.returncode != 0:
        return Status.UNCOMPILABLE

    # Run triggering tests
    for trigger_test in trigger_tests:
        result = run_d4j_cmd(
            f"test -t {trigger_test} -w {project_dir}", timeout=timeout
        )

        if result.returncode == 124:
            return Status.TIMEOUT
        elif result.stdout.strip() != "Failing tests: 0":
            return Status.COMPILABLE

    # Run relevant tests
    result = run_d4j_cmd(f"test -r -w {project_dir}", timeout=timeout)
    if result.returncode == 124:
        return Status.TIMEOUT
    elif result.stdout.strip() != "Failing tests: 0":
        return Status.COMPILABLE

    return Status.PLAUSIBLE


def apply_patch(cp_df: pd.DataFrame, bugid: str, hunks: list) -> Optional[pd.DataFrame]:
    # Load if already processed
    save_file_path = save_state_dir / f"{bugid}.jsonl"
    if save_file_path.exists():
        return

    pid = threading.get_ident()
    project_name, bug_number = bugid.split()

    bugs_list = [
        "Chart 4",
        "Chart 26",
        "Closure 2",
        "Closure 19",
        "Closure 40",
        "Closure 66",
        "Closure 102",
        "Closure 124",
        "Lang 4",
        "Lang 7",
        "Lang 28",
        "Lang 46",
        "Lang 55",
        "Lang 63",
        "Math 3",
        "Math 25",
        "Math 89",
        "Time 7",
        "Cli 18",
        "Codec 15",
        "Csv 5",
        "Csv 6",
        "Gson 6",
        "Gson 12",
        "Gson 16",
        "JacksonCore 21",
        "JacksonDatabind 5",
        "JacksonDatabind 24",
        "JacksonDatabind 39",
        "JacksonDatabind 49",
        "JacksonDatabind 51",
        "JacksonDatabind 58",
        "JacksonDatabind 101",
        "Jsoup 59",
        "Jsoup 85",
        "JxPath 20",
        "JxPath 22",
    ]

    if (
        len(hunks) == 1
        or bugid in ["Lang 10", "Math 65", "Math 81"]
        or bugid in bugs_list
    ):
        # Checkout the buggy version
        checkout_dir = d4j_tmp_dir / f"{pid}/checkout"
        checkout_dir.mkdir(parents=True, exist_ok=True)
        checkout_source(project_name, bug_number, True, checkout_dir)

        if bugid in ["Lang 10", "Math 65"]:
            hunk = hunks[1]
            bug_hunk_subset_df = get_hunk_candidates(cp_df, 1)
            cp_df = bug_hunk_subset_df.copy()
        elif bugid in ["Math 81", "Lang 4"]:
            hunk = hunks[2]
            bug_hunk_subset_df = get_hunk_candidates(cp_df, 2)
            cp_df = bug_hunk_subset_df.copy()
        elif bugid in ["Lang 63", "Time 7", "Cli 18"]:
            hunk = hunks[-1]
            bug_hunk_subset_df = get_hunk_candidates(cp_df, len(hunks) - 1)
            cp_df = bug_hunk_subset_df.copy()
        elif bugid in ["Lang 46"]:
            hunk = hunks[-2]
            bug_hunk_subset_df = get_hunk_candidates(cp_df, len(hunks) - 2)
            cp_df = bug_hunk_subset_df.copy()
        else:
            hunk = hunks[0]
            bug_hunk_subset_df = get_hunk_candidates(cp_df, 0)
            cp_df = bug_hunk_subset_df.copy()

        target_file_path = checkout_dir / hunk["source_path"]
        bug_line, bug_len = hunk["removed_line_numbers_range"]

        # Copy initial file to a temp directory
        source_file_path = (
            d4j_tmp_dir / str(pid) / "sources" / bugid / hunk["source_path"]
        )
        source_file_path.parent.mkdir(parents=True, exist_ok=False)
        shutil.copyfile(target_file_path, source_file_path)

        trigger_tests = run_d4j_cmd(
            f"export -p tests.trigger -w {checkout_dir}"
        ).stdout.splitlines()

        indent_size = len(hunk["added_lines"]) - len(hunk["added_lines"].lstrip(" \t"))
        indent = hunk["added_lines"][:indent_size]

        classes_target_dir = run_d4j_cmd(
            f"export -p dir.bin.classes -w {checkout_dir}"
        ).stdout
        tests_target_dir = run_d4j_cmd(
            f"export -p dir.bin.tests -w {checkout_dir}"
        ).stdout

        for index, patch in bug_hunk_subset_df["decoded_sequences"].items():
            insert_patch(
                patch, source_file_path, target_file_path, bug_line, bug_len, indent
            )

            start_timer = timeit.default_timer()
            passed = run_tests(bugid, checkout_dir, trigger_tests)
            end_timer = timeit.default_timer()
            cp_df.at[index, "validation_time"] = end_timer - start_timer

            if passed is Status.PLAUSIBLE:
                cp_df.at[index, "plausible"] = True
                cp_df.at[index, "compilable"] = True
                break
            elif passed is Status.COMPILABLE:
                cp_df.at[index, "compilable"] = True
            elif passed is Status.TIMEOUT:
                cp_df.at[index, "timeout"] = True
                cp_df.at[index, "compilable"] = True

            # Clean target directories
            shutil.rmtree(checkout_dir / classes_target_dir, ignore_errors=True)
            shutil.rmtree(checkout_dir / tests_target_dir, ignore_errors=True)

        cp_df.to_json(save_state_dir / f"{bugid}.jsonl", orient="records", lines=True)

    else:
        if bugid in ["Gson 14"]:
            hunks = hunks[0:1] + hunks[2:3]
            cp_df = cp_df.loc[cp_df["hunk"].isin([0, 2])]
        elif bugid in ["Closure 128"]:
            hunks[0]["removed_line_numbers_range"][0] = 790

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

        ###################################################################
        checkout_dir = d4j_tmp_dir / f"{pid}/checkout"
        checkout_dir.mkdir(parents=True, exist_ok=True)
        checkout_source(project_name, bug_number, True, checkout_dir)

        trigger_tests = run_d4j_cmd(
            f"export -p tests.trigger -w {checkout_dir}"
        ).stdout.splitlines()

        classes_target_dir = run_d4j_cmd(
            f"export -p dir.bin.classes -w {checkout_dir}"
        ).stdout
        tests_target_dir = run_d4j_cmd(
            f"export -p dir.bin.tests -w {checkout_dir}"
        ).stdout

        for hunk in hunks:
            target_file_path = checkout_dir / hunk["source_path"]
            source_file_path = (
                d4j_tmp_dir / str(pid) / "sources" / bugid / hunk["source_path"]
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
                target_file_path = checkout_dir / hunk["source_path"]
                bug_line, bug_len = hunk["removed_line_numbers_range"]

                source_file_path = (
                    d4j_tmp_dir / str(pid) / "sources" / bugid / hunk["source_path"]
                )

                indent_size = len(hunk["added_lines"]) - len(
                    hunk["added_lines"].lstrip(" \t")
                )
                indent = hunk["added_lines"][:indent_size]

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
            passed = run_tests(bugid, checkout_dir, trigger_tests)
            end_timer = timeit.default_timer()
            new_cp_df.at[index, "validation_time"] = end_timer - start_timer

            if passed is Status.PLAUSIBLE:
                new_cp_df.at[index, "plausible"] = True
                new_cp_df.at[index, "compilable"] = True
                break
            elif passed is Status.COMPILABLE:
                new_cp_df.at[index, "compilable"] = True
            elif passed is Status.TIMEOUT:
                new_cp_df.at[index, "timeout"] = True
                new_cp_df.at[index, "compilable"] = True

            # Clean target directories
            shutil.rmtree(checkout_dir / classes_target_dir, ignore_errors=True)
            shutil.rmtree(checkout_dir / tests_target_dir, ignore_errors=True)

        if not new_cp_df.empty and new_cp_df["plausible"].any():
            new_cp_df.to_json(
                save_state_dir / f"{bugid}.jsonl", orient="records", lines=True
            )
            return

        ###################################################################

        # Cleanup checkout dir
        shutil.rmtree(checkout_dir, ignore_errors=True)

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

        ##########################
        checkout_dir = d4j_tmp_dir / f"{pid}/checkout"
        checkout_dir.mkdir(parents=True, exist_ok=True)
        checkout_source(project_name, bug_number, True, checkout_dir)

        classes_target_dir = run_d4j_cmd(
            f"export -p dir.bin.classes -w {checkout_dir}"
        ).stdout
        tests_target_dir = run_d4j_cmd(
            f"export -p dir.bin.tests -w {checkout_dir}"
        ).stdout

        for hunk in hunks:
            target_file_path = checkout_dir / hunk["source_path"]
            source_file_path = (
                d4j_tmp_dir / str(pid) / "sources" / bugid / hunk["source_path"]
            )
            source_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target_file_path, source_file_path)

        ##########################

        # List to store extracted multi-hunk patches
        multi_patches_list = []

        _, running_failed_count = run_tests_for_multi(bugid, checkout_dir)

        running_plausible_df = None

        for i in range(len(hunks)):
            if running_failed_count == 0:
                break

            hunk_cp_df = get_hunk_candidates(cp_df, i)
            if bugid in ["Gson 14"] and i == 1:
                hunk_cp_df = get_hunk_candidates(cp_df, i + 1)

            for row in hunk_cp_df.itertuples():
                # Clean target directories
                shutil.rmtree(checkout_dir / classes_target_dir, ignore_errors=True)
                shutil.rmtree(checkout_dir / tests_target_dir, ignore_errors=True)

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
                    target_file_path = checkout_dir / hunk["source_path"]
                    bug_line, bug_len = hunk["removed_line_numbers_range"]

                    source_file_path = (
                        d4j_tmp_dir / str(pid) / "sources" / bugid / hunk["source_path"]
                    )

                    indent_size = len(hunk["added_lines"]) - len(
                        hunk["added_lines"].lstrip(" \t")
                    )
                    indent = hunk["added_lines"][:indent_size]

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

        #######################################################


def get_file_path(dir_path: Path, class_name: str) -> Path:
    return dir_path / f"{class_name.replace('.', '/')}.java"


def run_d4j_cmd(
    cmd: str, check: bool = False, timeout: Optional[int] = None
) -> subprocess.CompletedProcess[str]:
    def kill(proc_pid):
        parent_proc = psutil.Process(proc_pid)
        for proc in parent_proc.children(recursive=True):
            proc.terminate()
        parent_proc.terminate()

    d4j_cmd = f"perl {d4j_bin} {cmd}"
    args = shlex.split(d4j_cmd)

    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        output, error = process.communicate(timeout=timeout)

    except subprocess.TimeoutExpired:
        kill(process.pid)
        output, error = process.communicate()
        process.returncode = 124

    if check and process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, process.args)

    return subprocess.CompletedProcess(args, process.returncode, output, error)


def checkout_source(
    project_id: str, bug_id: str, buggy: bool, checkout_dir: Path
) -> None:
    cmd = (
        f"checkout -p {project_id} -v {bug_id}{'b' if buggy else 'f'} -w {checkout_dir}"
    )
    run_d4j_cmd(cmd, check=True)


def main():
    check_java_version()
    n_jobs = 2
    mp.set_start_method("spawn")

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

    shutil.rmtree(d4j_tmp_dir, ignore_errors=True)
    save_state_dir.mkdir(exist_ok=True)

    with tqdm_joblib(tqdm(total=len(bugs_metadata), disable=False)):
        Parallel(n_jobs=n_jobs, backend="multiprocessing")(
            delayed(apply_patch)(
                deepcopy(get_candidates(candidate_patches_df, bugid)), bugid, hunks
            )
            for bugid, hunks in bugs_metadata.items()
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
