"""Finding the buggy lines in BugsInPy dataset by comparing buggy and correct versions"""

import difflib
import json
import pickle
import string
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pygments
import tree_sitter_python as tspython
from pygments.lexers import PythonLexer
from pygments.token import Comment, String
from tqdm import tqdm
from tree_sitter import Language, Parser
from unidiff import PatchSet

from .. import rag_utils
from ..configs import (
    bugsinpy_bin_dir,
    bugsinpy_gen_dir,
    bugsinpy_projects_dir,
    bugsinpy_tmp_dir,
)

python_language = Language(tspython.language())
parser = Parser(python_language)
query = python_language.query(
    """(function_definition) @func-def
    """
)

python_lexer = PythonLexer(stripnl=False)


@dataclass
class DiffHunk:
    """Class to keep hunk data"""

    source_path: str
    removed_lines: str
    added_lines: str
    removed_line_numbers_range: tuple[int, int]
    added_line_numbers_range: tuple[int, int]
    source_context: tuple[str, int, int] = ""
    source_before: str = ""
    source_after: str = ""


def get_context(
    program: Path, line_number: int, lines_range: int
) -> tuple[str, int, int]:
    with open(program, "rb") as file:
        content = file.read()

    tree = parser.parse(content)

    captures = query.captures(tree.root_node)

    for capture, _ in captures:
        # start_point and end_point are zero-based
        if capture.start_point[0] <= (line_number - 1) <= capture.end_point[0]:
            context = capture.text.decode()
            # splitlines and join are to handle Python's universal newlines
            # conversion on Windows to avoid getting \r\r\n
            return (
                "\n".join(context.splitlines()),
                capture.start_point[0] + 1,
                capture.end_point[0] + 1,
            )
    else:
        with open(program, encoding="cp1256") as file:
            source_lines = file.readlines()

        cw = 3
        if lines_range:
            start_line = max(1, line_number - cw)
            end_line = min(len(source_lines), line_number + lines_range + cw - 1)
        else:
            start_line = max(1, line_number - cw + 1)
            end_line = min(len(source_lines), line_number + cw)
        return (
            "".join(source_lines[start_line - 1 : end_line]),
            start_line,
            end_line,
        )


def remove_comments(code: str) -> str:
    """Remove comments and keep the line numbers intact
    so we can replace patched lines in the original file.
    """

    lexed_code = pygments.lex(code, python_lexer)

    comment_stripped_code = []
    for ttype, tvalue in lexed_code:
        if (
            ttype in Comment
            and ttype not in [Comment.Preproc, Comment.PreprocFile]
            or ttype in String.Doc
        ):
            comment_lines = tvalue.splitlines(keepends=True)

            # Check if the last newline token is attached to the comment or is a separate token
            if comment_lines[-1].endswith("\n"):
                newlines_count = len(comment_lines)
            else:
                # -1 is because there is a separate newline token at the end of comment tokens
                newlines_count = len(comment_lines) - 1

            comment_stripped_code.append("\n" * newlines_count)
        else:
            comment_stripped_code.append(tvalue)

    return "".join(comment_stripped_code)


def cleanup(
    project_bug_id: str, filename: str, source: str, target: str
) -> tuple[str, str]:
    """Clean up inconsistencies in some files to detect changes more accurately"""

    source_lines = source.splitlines()

    if project_bug_id == "thefuck 1":
        source_lines[15] += " "
    elif project_bug_id == "thefuck 3":
        source_lines[108] += " "
    elif project_bug_id == "youtube-dl 20":
        source_lines[368] += " "

    source = "\n".join(source_lines)
    return source, target


def get_diff_lines(
    project_bug_id: str, fromfile: Path, tofile: Path, context_size: int = 0
) -> Iterable[str]:
    with (
        open(fromfile, encoding="cp1256") as source_file,
        open(tofile, encoding="cp1256") as target_file,
    ):
        source = remove_comments(source_file.read())
        target = remove_comments(target_file.read())

    if project_bug_id in ["thefuck 1", "thefuck 3", "youtube-dl 20"]:
        source, target = cleanup(project_bug_id, fromfile.stem, source, target)

    diff_lines = difflib.unified_diff(
        source.splitlines(keepends=True),
        target.splitlines(keepends=True),
        fromfile=str(
            fromfile.relative_to(
                bugsinpy_tmp_dir / f"{project_bug_id.split()[0]}-buggy"
            )
        ),
        tofile=str(
            tofile.relative_to(bugsinpy_tmp_dir / f"{project_bug_id.split()[0]}-fixed")
        ),
        n=context_size,
    )

    return list(diff_lines)


def process_hunks(diff_lines: list[str]) -> list[DiffHunk]:
    patch_set = PatchSet(diff_lines)

    # My diffs should only contain one file since I process each file separately
    assert len(patch_set) == 1, patch_set
    patched_file = patch_set[0]

    diff_hunks = []

    for hunk in patched_file:
        hunk_source = "".join(x[1:] for x in hunk.source)
        hunk_target = "".join(x[1:] for x in hunk.target)

        # Ignore hunks where both source and target are empty
        if not (hunk_source.strip() or hunk_target.strip()):
            continue

        # Ignore if hunks only differ in trailing whitespaces
        if hunk_source.strip() == hunk_target.strip():
            continue

        diff_hunk = DiffHunk(
            patched_file.source_file,
            hunk_source,
            hunk_target,
            (hunk.source_start, hunk.source_length),
            (hunk.target_start, hunk.target_length),
        )
        diff_hunks.append(diff_hunk)

    return diff_hunks


def prepare(hunk: str) -> str:
    lines_concat = " ".join([line.strip() for line in hunk.splitlines()])
    return lines_concat.strip()


def generate_data(bug_hunks: dict[str, list[DiffHunk]]) -> None:
    """Generates input data for model evaluation"""

    bugsinpy_gen_dir.mkdir(parents=True, exist_ok=True)
    with (
        open(bugsinpy_gen_dir / "BugsInPy.jsonl", "w") as file,
        open(bugsinpy_gen_dir / "rem.txt", "w") as remfile,
        open(bugsinpy_gen_dir / "add.txt", "w") as addfile,
        open(bugsinpy_gen_dir / "context.txt", "w") as ctxfile,
    ):
        for program, hunks in bug_hunks.items():
            file.write(json.dumps({program: [asdict(h) for h in hunks]}) + "\n")
            remfile.writelines(prepare(h.removed_lines) + "\n" for h in hunks)
            addfile.writelines(prepare(h.added_lines) + "\n" for h in hunks)
            ctxfile.writelines(prepare(h.source_context[0]) + "\n" for h in hunks)


def get_file_path(dir_path: Path, project_id: str, file_path: str) -> Path:
    return dir_path / f"{project_id}/{file_path}"


def checkout_source(
    project_id: str, bug_id: str, buggy_version: bool, checkout_dir: Path
) -> None:
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


def remove_context_from_source(
    hunk: DiffHunk, buggy_source_file: Path
) -> tuple[str, str]:
    """Remove context from the full source file"""

    with open(buggy_source_file, encoding="cp1256") as file:
        source_lines = file.readlines()

    if hunk.source_context[0]:
        context_start = hunk.source_context[1]
        context_end = hunk.source_context[2]
        source_before = "".join(source_lines[: context_start - 1])
        source_after = "".join(source_lines[context_end:])
    else:
        buggy_lines_start = hunk.removed_line_numbers_range[0]
        buggy_lines_end = buggy_lines_start + hunk.removed_line_numbers_range[1]
        source_before = "".join(
            source_lines[
                : buggy_lines_start - (1 if hunk.removed_line_numbers_range[1] else 0)
            ]
        )
        source_after = "".join(
            source_lines[
                buggy_lines_end - (1 if hunk.removed_line_numbers_range[1] else 0) :
            ]
        )

    hunk.source_before = source_before
    hunk.source_after = source_after

    return source_before, source_after


def clean_embed_input(chunks: list[str], query: str) -> list[str]:
    """Remove chunks that are empty, only contain punctuations, identical to source lines,
    and are duplicates"""

    cleaned = [
        ch
        for ch in chunks
        if ch.strip(string.punctuation + string.whitespace) and ch != query
    ]
    return list(set(cleaned))


def get_modified_files(project_id: str, bug_id: str) -> list[str]:
    patch_path = bugsinpy_projects_dir / f"{project_id}/bugs/{bug_id}/bug_patch.txt"

    with open(patch_path) as file:
        patch_lines = file.readlines()
    patch_set = PatchSet(patch_lines)

    modified_sources = [patched_file.source_file[2:] for patched_file in patch_set]
    modified_targets = [patched_file.source_file[2:] for patched_file in patch_set]

    assert modified_sources == modified_targets, (
        "Modified sources and targets are different"
    )

    return modified_sources


def worker_func(project_id: str, bug_id: str) -> tuple[str, list[DiffHunk]]:
    """Worker function to process each project bugs"""

    buggy_checkout_dir = bugsinpy_tmp_dir / f"{project_id}-buggy"
    fixed_checkout_dir = bugsinpy_tmp_dir / f"{project_id}-fixed"

    # Checkout buggy and fixed versions of the source code
    checkout_source(project_id, bug_id, True, buggy_checkout_dir)
    checkout_source(project_id, bug_id, False, fixed_checkout_dir)

    modified_sources = get_modified_files(project_id, bug_id)

    hunks: list[DiffHunk] = []

    for modified_source in modified_sources:
        buggy_file_path = get_file_path(buggy_checkout_dir, project_id, modified_source)
        fixed_file_path = get_file_path(fixed_checkout_dir, project_id, modified_source)

        # if source or target doesn't exist, patch needs creation or deletion of a file
        if buggy_file_path.exists() and fixed_file_path.exists():
            diff_lines = get_diff_lines(
                f"{project_id} {bug_id}", buggy_file_path, fixed_file_path
            )

            # File is listed in the modified files but there isn't anything changed in it
            # or it is just a comment change.
            if not diff_lines:
                continue

            file_hunks = process_hunks(diff_lines)

            for hunk in file_hunks:
                line_number = hunk.removed_line_numbers_range[0]
                lines_range = hunk.removed_line_numbers_range[1]
                hunk.source_context = get_context(
                    buggy_file_path, line_number, lines_range
                )
                source_before, source_after = remove_context_from_source(
                    hunk, buggy_file_path
                )

            hunks += file_hunks

    return bug_id, hunks


def extract_bug_projects() -> dict[str, list[str]]:
    """Extract project names and their bug ids"""

    projects = {
        project.name: [
            bug.name
            for bug in sorted((project / "bugs").iterdir(), key=lambda x: int(x.name))
        ]
        for project in sorted(bugsinpy_projects_dir.iterdir())
    }

    return projects


def main():
    bug_hunks: dict[str, list[DiffHunk]] = {}

    save_state_file = bugsinpy_tmp_dir / "save-state.pkl"
    if save_state_file.exists():
        with open(save_state_file, "rb") as file:
            bug_hunks = pickle.load(file)

    projects = extract_bug_projects()

    for project_id, bug_ids in projects.items():
        print(project_id)

        result = [worker_func(project_id, bug_id) for bug_id in tqdm(bug_ids)]

        for bug_id, hunks in result:
            bug_hunks[f"{project_id} {bug_id}"] = hunks

        # Save intermediate results dictionary
        with open(save_state_file, "wb") as file:
            pickle.dump(bug_hunks, file)

    generate_data(bug_hunks)

    # Embedding for RAG
    print("Embedding...")
    rag = rag_utils.RAG("BugsInPy")
    rag.create_collection()
    for bugid, hunks in bug_hunks.items():
        for h, hunk in enumerate(hunks):
            chunks = rag.split(hunk.source_before + "\n" + hunk.source_after)
            src = prepare(hunk.removed_lines)
            cleaned_chunks = clean_embed_input(chunks, src)
            if cleaned_chunks:
                metadata = {"bugid": bugid, "hunk": h}
                rag.embed(cleaned_chunks, [metadata] * len(cleaned_chunks))
            print(bugid, h)


if __name__ == "__main__":
    main()
