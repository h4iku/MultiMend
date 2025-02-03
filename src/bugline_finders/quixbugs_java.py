"""Finding the buggy lines in QuixBugs(Java) dataset by comparing buggy and correct programs"""

import difflib
import json
import string
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pygments
import tree_sitter_java as tsjava
from pygments.lexers import JavaLexer
from pygments.token import Comment, String
from tree_sitter import Language, Parser
from unidiff import PatchSet

from .. import rag_utils
from ..configs import (
    quixbugs_genjava_dir,
    quixbugs_java_buggy_dir,
    quixbugs_java_correct_dir,
    quixbugs_programs,
)

java_language = Language(tsjava.language())
parser = Parser(java_language)
query = java_language.query(
    """
    (method_declaration) @method-dec
    (constructor_declaration) @constructor-dec
    """
)

java_lexer = JavaLexer(stripnl=False)


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
        with open(program) as file:
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

    lexed_code = pygments.lex(code, java_lexer)

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


@dataclass
class DiffHunk:
    """Class to keep hunk data"""

    removed_lines: str
    added_lines: str
    removed_line_numbers_range: tuple[int, int]
    added_line_numbers_range: tuple[int, int]
    source_context: tuple[str, int, int] = ""
    source_before: str = ""
    source_after: str = ""


def get_program_path(dir_path: Path, program_name: str) -> Path:
    return dir_path / f"{program_name.upper()}.java"


def get_diff_lines(
    program: str, fromfile: Path, tofile: Path, context_size: int = 0
) -> Iterable[str]:
    with open(fromfile) as source_file, open(tofile) as target_file:
        source, target = cleanup(program, source_file.read(), target_file.read())

    source = remove_comments(source)
    target = remove_comments(target)

    diff_lines = difflib.unified_diff(
        source.splitlines(keepends=True),
        target.splitlines(keepends=True),
        fromfile="/".join(fromfile.parts[-2:]),
        tofile="/".join(tofile.parts[-2:]),
        n=context_size,
    )

    return diff_lines


def process_hunks(diff_lines: Iterable[str]) -> list[DiffHunk]:
    patch_set = PatchSet(diff_lines)
    assert len(patch_set) == 1
    patched_file = patch_set[0]

    diff_hunks = []

    for hunk in patched_file:
        hunk_source = "".join(x[1:] for x in hunk.source)
        hunk_target = "".join(x[1:] for x in hunk.target)

        # Ignore if hunks only differ in whitespaces
        if "".join(hunk_source.split()) == "".join(hunk_target.split()):
            continue

        # Ignore if the difference is only in the package name
        if hunk_source.strip().startswith("package") and hunk_target.strip().startswith(
            "package"
        ):
            continue

        # Ignore if the difference is only in the imports
        if hunk_source.strip().startswith("import") or hunk_target.strip().startswith(
            "import"
        ):
            continue

        diff_hunk = DiffHunk(
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


def generate_data(programs_hunks: dict[str, list[DiffHunk]]) -> None:
    """Generates input data for model evaluation"""

    quixbugs_genjava_dir.mkdir(parents=True, exist_ok=True)
    with (
        open(quixbugs_genjava_dir / "QuixBugs_Java.jsonl", "w") as file,
        open(quixbugs_genjava_dir / "rem.txt", "w") as remfile,
        open(quixbugs_genjava_dir / "add.txt", "w") as addfile,
        open(quixbugs_genjava_dir / "context.txt", "w") as ctxfile,
    ):
        for program, hunks in programs_hunks.items():
            file.write(json.dumps({program: [asdict(h) for h in hunks]}) + "\n")
            remfile.writelines(prepare(h.removed_lines) + "\n" for h in hunks)
            addfile.writelines(prepare(h.added_lines) + "\n" for h in hunks)
            ctxfile.writelines(prepare(h.source_context[0]) + "\n" for h in hunks)


def cleanup(program: str, source: str, target: str) -> tuple[str, str]:
    """Clean up inconsistencies in some files to detect changes more accurately"""

    if program == "breadth_first_search":
        source = source.replace("// return false;", "return false;")
    elif program == "shortest_paths":
        source_lines = source.splitlines(keepends=True)
        source = "".join(source_lines[:36] + source_lines[62:])
    elif program == "shunting_yard":
        source_lines = source.splitlines(keepends=True)
        del source_lines[41]
        source = "".join(source_lines)

    elif program == "flatten":
        source_lines = source.splitlines(keepends=True)
        source_lines[21:25] = [" " + line for line in source_lines[21:25]]
        source = "".join(source_lines)
    elif program == "lcs_length":
        source_lines = source.splitlines(keepends=True)
        source_lines[35] = " " + source_lines[35]
        source = "".join(source_lines)
    elif program == "powerset":
        source_lines = source.splitlines(keepends=True)
        source_lines[23:28] = [" " + line for line in source_lines[23:28]]
        source = "".join(source_lines)

    return source, target


def remove_context_from_source(
    hunk: DiffHunk, buggy_source_file: Path
) -> tuple[str, str]:
    """Remove context from the full source file"""

    with open(buggy_source_file) as file:
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


def main():
    programs_hunks: dict[str, list[DiffHunk]] = {}

    for program in quixbugs_programs:
        buggy_java_program = get_program_path(quixbugs_java_buggy_dir, program)
        correct_java_program = get_program_path(quixbugs_java_correct_dir, program)

        diff_lines = list(
            get_diff_lines(program, buggy_java_program, correct_java_program)
        )
        hunks = process_hunks(diff_lines)

        for hunk in hunks:
            line_number = hunk.removed_line_numbers_range[0]
            lines_range = hunk.removed_line_numbers_range[1]
            hunk.source_context = get_context(
                buggy_java_program, line_number, lines_range
            )
            remove_context_from_source(hunk, buggy_java_program)

        programs_hunks[program] = hunks

    generate_data(programs_hunks)

    # Embedding for RAG
    print("Embedding...")
    rag = rag_utils.RAG("QuixBugs-Java")
    rag.create_collection()
    for bugid, hunks in programs_hunks.items():
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
