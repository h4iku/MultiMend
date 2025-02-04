import contextlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
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

from ..configs import codeflaws_data_dir, codeflaws_gen_dir

gen_dir = codeflaws_gen_dir
bugs_metadata_file = "Codeflaws.jsonl"
model = "multimend"
output_dir = gen_dir / f"outputs-{model}"
temp_dir = output_dir / "temp"
save_state_dir = output_dir / "save-state"
output_size = 100

rem_file_path = gen_dir / "rem.txt"
add_file_path = gen_dir / "add.txt"

if platform.system() == "Windows":
    make_bin = "mingw32-make"
else:
    make_bin = "make"

with (
    open(rem_file_path) as rem_file,
    open(add_file_path) as add_file,
):
    sources = [src.strip() for src in rem_file]
    targets = [tgt.strip() for tgt in add_file]


@contextlib.contextmanager
def change_directory(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


@contextlib.contextmanager
def working_environment(bugid: str):
    # Split the bugid to get file names
    project_dir = codeflaws_data_dir / bugid
    metadata = bugid.split("-")
    buggy_file_name = f"{metadata[0]}-{metadata[1]}-{metadata[-2]}.c"

    # Copy files to a working directory
    project_copy_dir = temp_dir / bugid
    copy_dataset_files(project_dir, project_copy_dir)

    target_file_path = project_copy_dir / buggy_file_name

    # Copy initial file to a temp directory
    source_file_path = temp_dir / "sources" / bugid / buggy_file_name
    source_file_path.parent.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(target_file_path, source_file_path)

    try:
        yield project_copy_dir, source_file_path, target_file_path
    finally:
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


def check_gcc_version():
    # Check GCC installation
    try:
        gcc_version_string = subprocess.run(
            ["gcc", "--version"], capture_output=True, text=True, check=True
        ).stdout
    except subprocess.CalledProcessError as e:
        print("Can't find `gcc`")
        raise e

    gcc_pattern = r"\) (\d+)\.\d+.*"
    gcc_version = re.search(gcc_pattern, gcc_version_string).groups()[0]

    # Any gcc version can be used, but I used gcc 7.5. There are some flaky tests in the
    # dataset that cause different gcc versions to trigger different behaviors.
    assert gcc_version == "7", "Wrong GCC version, needs GCC 7"


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
        lines.insert(bug_line, indent + patch + "\n")
    else:
        lines[bug_line - 1 : (bug_line - 1) + bug_len] = indent + patch + "\n"

    with open(target_file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)


def get_passing_tests(bugid: str, project_dir: Path) -> list[tuple[Path, Path]]:
    timeout = 60
    meta = bugid.split("-")
    correct_filename = f"{meta[0]}-{meta[1]}-{meta[-1]}"
    passing_tests = []

    with change_directory(project_dir):
        subprocess.run(
            [make_bin, f"FILENAME={correct_filename}"], capture_output=True, check=True
        )

        # Checking tests
        testcases = {
            file: file.with_name(file.name.replace("input", "output"))
            for file in Path(".").iterdir()
            if file.is_file() and file.name.startswith("heldout-input")
        }

        for testcase_path, testcase_output_path in testcases.items():
            with open(testcase_path) as input_file:
                try:
                    result = subprocess.run(
                        [f".{os.sep}{correct_filename}"],
                        stdin=input_file,
                        text=True,
                        capture_output=True,
                        timeout=timeout,
                        encoding="cp1256",
                    )
                except subprocess.TimeoutExpired:
                    continue

            with open(testcase_output_path) as output_file:
                if result.stdout.rstrip() == output_file.read().rstrip():
                    passing_tests.append((testcase_path, testcase_output_path))

    return passing_tests


flaky_tests = {
    ("107-B-bug-2042682-2042689", "heldout-input-pos32"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos35"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos40"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos52"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos57"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos59"),
    ("107-B-bug-2042682-2042689", "heldout-input-pos60"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos43"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos52"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos53"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos54"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos56"),
    ("107-B-bug-4234495-4234502", "heldout-input-pos57"),
    ("107-B-bug-633264-633415", "heldout-input-pos31"),
    ("107-B-bug-633264-633415", "heldout-input-pos40"),
    ("107-B-bug-633264-633415", "heldout-input-pos45"),
    ("107-B-bug-633264-633415", "heldout-input-pos56"),
    ("107-B-bug-633264-633415", "heldout-input-pos57"),
    ("107-B-bug-633264-633415", "heldout-input-pos60"),
    ("116-B-bug-2308784-2308812", "heldout-input-pos12"),
    ("116-B-bug-2308784-2308812", "heldout-input-pos23"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos14"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos15"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos17"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos18"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos19"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos22"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos29"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos37"),
    ("146-B-bug-17886329-17886431", "heldout-input-pos42"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos13"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos18"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos21"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos26"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos27"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos28"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos30"),
    ("166-A-bug-10686292-10686462", "heldout-input-pos41"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos101"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos130"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos48"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos55"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos56"),
    ("196-B-bug-1810869-1810880", "heldout-input-pos91"),
    ("197-B-bug-3726950-3726956", "heldout-input-pos30"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos12"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos13"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos17"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos2"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos20"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos21"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos22"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos24"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos26"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos27"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos30"),
    ("208-A-bug-18102368-18102377", "heldout-input-pos31"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos51"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos57"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos62"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos63"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos64"),
    ("208-A-bug-18110250-18110255", "heldout-input-pos71"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos10"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos14"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos15"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos17"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos18"),
    ("215-B-bug-1986588-1986853", "heldout-input-pos20"),
    ("22-D-bug-17896274-17896278", "heldout-input-pos22"),
    ("22-D-bug-17896274-17896278", "heldout-input-pos4"),
    ("22-D-bug-17896274-17896278", "heldout-input-pos6"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos2"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos28"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos29"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos3"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos31"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos33"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos64"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos66"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos68"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos72"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos73"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos8"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos83"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos87"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos93"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos94"),
    ("220-A-bug-8395389-8395417", "heldout-input-pos95"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos34"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos36"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos37"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos38"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos39"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos40"),
    ("222-A-bug-4475922-4475947", "heldout-input-pos42"),
    ("230-A-bug-17966959-17967012", "heldout-input-pos47"),
    ("250-A-bug-2762401-2762408", "heldout-input-pos22"),
    ("250-A-bug-2762401-2762408", "heldout-input-pos28"),
    ("293-A-bug-3825824-3825830", "heldout-input-pos43"),
    ("293-A-bug-3825824-3825830", "heldout-input-pos45"),
    ("294-B-bug-5091120-5091142", "heldout-input-pos26"),
    ("298-A-bug-15320493-15320547", "heldout-input-pos11"),
    ("298-A-bug-15320493-15320547", "heldout-input-pos12"),
    ("33-A-bug-3732590-3732618", "heldout-input-pos18"),
    ("33-A-bug-3732590-3732618", "heldout-input-pos28"),
    ("330-C-bug-4119925-4120324", "heldout-input-pos25"),
    ("330-C-bug-4119925-4120324", "heldout-input-pos32"),
    ("330-C-bug-4119925-4120324", "heldout-input-pos36"),
    ("337-A-bug-18033613-18034576", "heldout-input-pos10"),
    ("337-A-bug-18033613-18034576", "heldout-input-pos11"),
    ("337-A-bug-18033613-18034576", "heldout-input-pos16"),
    ("337-A-bug-18033613-18034576", "heldout-input-pos2"),
    ("337-A-bug-18033613-18034576", "heldout-input-pos3"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos11"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos12"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos14"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos19"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos28"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos30"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos31"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos8"),
    ("346-A-bug-5781133-5781150", "heldout-input-pos9"),
    ("359-A-bug-5624380-5624386", "heldout-input-pos11"),
    ("359-A-bug-5624380-5624386", "heldout-input-pos34"),
    ("366-B-bug-5240575-5240582", "heldout-input-pos31"),
    ("366-B-bug-5240575-5240582", "heldout-input-pos32"),
    ("366-B-bug-5240575-5240582", "heldout-input-pos33"),
    ("366-B-bug-5240575-5240582", "heldout-input-pos6"),
    ("378-B-bug-5559657-5560108", "heldout-input-pos24"),
    ("378-B-bug-5559657-5560108", "heldout-input-pos27"),
    ("378-B-bug-5559657-5560108", "heldout-input-pos30"),
    ("405-B-bug-6161287-6161316", "heldout-input-pos49"),
    ("405-B-bug-9434593-9434605", "heldout-input-pos46"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos11"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos12"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos13"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos17"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos18"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos19"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos21"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos23"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos26"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos27"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos31"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos33"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos35"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos37"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos38"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos43"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos44"),
    ("427-A-bug-17275707-17275729", "heldout-input-pos6"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos2"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos26"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos31"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos32"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos35"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos36"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos37"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos38"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos41"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos43"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos45"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos46"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos47"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos48"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos51"),
    ("441-B-bug-6979392-6979398", "heldout-input-pos8"),
    ("469-B-bug-15208335-15208369", "heldout-input-pos14"),
    ("490-C-bug-9390336-9390363", "heldout-input-pos3"),
    ("540-B-bug-11090348-11090416", "heldout-input-pos48"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos11"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos15"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos16"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos19"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos23"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos24"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos27"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos31"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos35"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos39"),
    ("548-A-bug-13402608-13402780", "heldout-input-pos43"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos11"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos15"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos16"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos19"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos23"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos24"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos27"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos31"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos35"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos39"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos43"),
    ("548-A-bug-16057870-16058252", "heldout-input-pos47"),
    ("55-A-bug-252924-252926", "heldout-input-pos16"),
    ("55-A-bug-252924-252926", "heldout-input-pos32"),
    ("55-A-bug-252924-252926", "heldout-input-pos51"),
    ("55-A-bug-252924-252926", "heldout-input-pos8"),
    ("55-A-bug-252924-252926", "heldout-input-pos82"),
    ("55-A-bug-252924-252926", "heldout-input-pos83"),
    ("618-A-bug-15693099-15693123", "heldout-input-pos3"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos10"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos15"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos19"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos25"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos7"),
    ("673-A-bug-18045973-18046099", "heldout-input-pos8"),
    ("673-A-bug-18141268-18141293", "heldout-input-pos10"),
    ("673-A-bug-18141268-18141293", "heldout-input-pos19"),
    ("673-A-bug-18141268-18141293", "heldout-input-pos25"),
    ("673-A-bug-18141268-18141293", "heldout-input-pos7"),
    ("673-A-bug-18141268-18141293", "heldout-input-pos8"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos12"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos15"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos26"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos30"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos34"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos4"),
    ("673-A-bug-18259860-18259895", "heldout-input-pos6"),
}


class Status(Enum):
    PLAUSIBLE = auto()
    COMPILABLE = auto()
    TIMEOUT = auto()
    UNCOMPILABLE = auto()


def run_tests_for_multi(
    bugid: str, project_dir: Path, passing_tests: list[tuple[Path, Path]]
) -> tuple[Status, int | None]:
    timeout = 60  # seconds

    meta = bugid.split("-")
    buggy_filename = f"{meta[0]}-{meta[1]}-{meta[-2]}"

    with change_directory(project_dir):
        # Compile
        compile_result = subprocess.run([make_bin], capture_output=True)
        if compile_result.returncode != 0:
            return Status.UNCOMPILABLE, None

        failed_count = 0
        # Running tests
        for testcase_path, testcase_output_path in passing_tests:
            if (bugid, testcase_path.name) in flaky_tests:
                continue

            with (
                open(testcase_path) as input_file,
                open("stdout", "w", encoding="cp1256") as stdout_file,
            ):
                try:
                    result = subprocess.run(
                        [f".{os.sep}{buggy_filename}"],
                        stdin=input_file,
                        text=True,
                        capture_output=False,
                        stdout=stdout_file,
                        stderr=subprocess.DEVNULL,
                        timeout=timeout,
                        encoding="cp1256",
                    )
                except subprocess.TimeoutExpired:
                    return Status.TIMEOUT, None

            if Path("stdout").stat().st_size / (1024 * 1024) > 100:
                failed_count += 1
                continue

            with (
                open(testcase_output_path) as output_file,
                open("stdout", encoding="cp1256") as stdout_file,
            ):
                if stdout_file.read().rstrip() != output_file.read().rstrip():
                    failed_count += 1

    if failed_count:
        return Status.COMPILABLE, failed_count
    else:
        return Status.PLAUSIBLE, 0


def run_tests(
    bugid: str, project_dir: Path, passing_tests: list[tuple[Path, Path]]
) -> Status:
    timeout = 60  # seconds

    meta = bugid.split("-")
    buggy_filename = f"{meta[0]}-{meta[1]}-{meta[-2]}"

    with change_directory(project_dir):
        # Compile
        compile_result = subprocess.run([make_bin], capture_output=True)
        if compile_result.returncode != 0:
            return Status.UNCOMPILABLE

        # Running tests
        for testcase_path, testcase_output_path in passing_tests:
            if (bugid, testcase_path.name) in flaky_tests:
                continue

            with (
                open(testcase_path) as input_file,
                open("stdout", "w", encoding="cp1256") as stdout_file,
            ):
                try:
                    result = subprocess.run(
                        [f".{os.sep}{buggy_filename}"],
                        stdin=input_file,
                        text=True,
                        capture_output=False,
                        stdout=stdout_file,
                        stderr=subprocess.DEVNULL,
                        timeout=timeout,
                        encoding="cp1256",
                    )
                except subprocess.TimeoutExpired:
                    return Status.TIMEOUT

            if Path("stdout").stat().st_size / (1024 * 1024) > 100:
                return Status.COMPILABLE

            with (
                open(testcase_output_path) as output_file,
                open("stdout", encoding="cp1256") as stdout_file,
            ):
                if stdout_file.read().rstrip() != output_file.read().rstrip():
                    return Status.COMPILABLE

    return Status.PLAUSIBLE


def apply_patch(cp_df: pd.DataFrame, bugid: str, hunks: list) -> Optional[pd.DataFrame]:
    # Check if already processed
    save_file_path = save_state_dir / f"{bugid}.jsonl"
    if save_file_path.exists():
        return

    if len(hunks) == 1:
        hunk = hunks[0]

        bug_line, bug_len = hunk["removed_line_numbers_range"]
        bug_hunk_subset_df = get_hunk_candidates(cp_df, 0)

        indent_size = len(hunk["added_lines"]) - len(hunk["added_lines"].lstrip(" \t"))
        indent = hunk["added_lines"][:indent_size]

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            # Get reproducible tests
            returned_tests = [
                set(get_passing_tests(bugid, project_copy_dir)) for _ in range(3)
            ]
            passing_tests = set.intersection(*returned_tests)

            for index, patch in bug_hunk_subset_df["decoded_sequences"].items():
                insert_patch(
                    patch, source_file_path, target_file_path, bug_line, bug_len, indent
                )

                # call the testing infrastructure
                start_timer = timeit.default_timer()
                passed = run_tests(bugid, project_copy_dir, passing_tests)

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

        #######################################################################

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            # Get reproducible tests
            returned_tests = [
                set(get_passing_tests(bugid, project_copy_dir)) for _ in range(3)
            ]
            passing_tests = set.intersection(*returned_tests)

            for index, patches in new_cp_df["decoded_sequences"].items():
                bugs_lens = defaultdict(list)

                for hunk, patch in reversed(list(zip(hunks, patches))):
                    bug_line, bug_len = hunk["removed_line_numbers_range"]

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
                passed = run_tests(bugid, project_copy_dir, passing_tests)
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

        #######################################################################

        # List to store extracted multi-hunk patches
        multi_patches_list = []

        running_plausible_df = None

        with working_environment(bugid) as (
            project_copy_dir,
            source_file_path,
            target_file_path,
        ):
            _, running_failed_count = run_tests_for_multi(
                bugid, project_copy_dir, passing_tests
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
                    status, failed_count = run_tests_for_multi(
                        bugid, project_copy_dir, passing_tests
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
    check_gcc_version()

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
