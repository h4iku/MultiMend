"""Finding the buggy lines in BugAID dataset by comparing buggy and correct versions"""

import csv
import difflib
import json
import string
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pygments
import tree_sitter_javascript as tsjs
from pygments.lexers import JavascriptLexer
from pygments.token import Comment, String
from tree_sitter import Language, Parser
from unidiff import PatchSet

from .. import rag_utils
from ..configs import bugaid_data_dir, bugaid_gen_dir

javascript_language = Language(tsjs.language())
parser = Parser(javascript_language)
query = javascript_language.query(
    """
    (function_declaration) @function-declaration
    (function_expression) @function-expression
    (method_definition) @method-definition
    """
)

javascript_lexer = JavascriptLexer(stripnl=False)


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

    lexed_code = pygments.lex(code, javascript_lexer)

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


def get_diff_lines(
    bug_id: str, fromfile: Path, tofile: Path, context_size: int = 0
) -> Iterable[str]:
    with (
        open(fromfile, encoding="cp1256") as source_file,
        open(tofile, encoding="cp1256") as target_file,
    ):
        source = remove_comments(source_file.read())
        target = remove_comments(target_file.read())

        source, target = cleanup(bug_id, source, target)

        source_lines = [line.strip() + "\n" for line in source.splitlines()]
        target_lines = [line.strip() + "\n" for line in target.splitlines()]

    diff_lines = difflib.unified_diff(
        source_lines,
        target_lines,
        fromfile="/".join(fromfile.parts[-2:]),
        tofile="/".join(tofile.parts[-2:]),
        n=context_size,
    )

    return diff_lines


def process_hunks(diff_lines: Iterable[str]) -> list[DiffHunk]:
    patch_set = PatchSet(diff_lines)

    # My diffs should only contain one file since I process each file separately
    assert len(patch_set) == 1
    patched_file = patch_set[0]

    diff_hunks = []

    for hunk in patched_file:
        hunk_source = "".join(x[1:] for x in hunk.source)
        hunk_target = "".join(x[1:] for x in hunk.target)

        # Ignore if hunks only differ in whitespaces
        if "".join(hunk_source.split()) == "".join(hunk_target.split()):
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

    bugaid_gen_dir.mkdir(parents=True, exist_ok=True)
    with (
        open(bugaid_gen_dir / "BugAID.jsonl", "w") as file,
        open(bugaid_gen_dir / "rem.txt", "w") as remfile,
        open(bugaid_gen_dir / "add.txt", "w") as addfile,
        open(bugaid_gen_dir / "context.txt", "w") as ctxfile,
    ):
        for program, hunks in bug_hunks.items():
            file.write(json.dumps({program: [asdict(h) for h in hunks]}) + "\n")
            remfile.writelines(prepare(h.removed_lines) + "\n" for h in hunks)
            addfile.writelines(prepare(h.added_lines) + "\n" for h in hunks)
            ctxfile.writelines(prepare(h.source_context[0]) + "\n" for h in hunks)


def cleanup(program: str, source: str, target: str) -> tuple[str, str]:
    """Clean up inconsistencies in some files to detect changes more accurately"""

    if program == "IncorrectComparison1":
        source = source.replace(
            "if (typeof opt.default!='undefined') self.default(key, opt.default);",
            """if (typeof opt.default!='undefined') {
                self.default(key, opt.default);
            }""",
        )

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
    bug_hunks: dict[str, list[DiffHunk]] = {}

    with open(bugaid_data_dir.parent / "metadata.txt", newline="") as metafile:
        reader = csv.reader(metafile)
        bug_ids, file_names = zip(*[row for row in reader])

    for bug_id, file_name in zip(bug_ids, file_names):
        hunks: list[DiffHunk] = []

        buggy_file_path = bugaid_data_dir / bug_id / "buggy" / file_name
        fixed_file_path = bugaid_data_dir / bug_id / "fixed" / file_name

        diff_lines = list(get_diff_lines(bug_id, buggy_file_path, fixed_file_path))
        hunks = process_hunks(diff_lines)

        for hunk in hunks:
            line_number = hunk.removed_line_numbers_range[0]
            lines_range = hunk.removed_line_numbers_range[1]
            hunk.source_context = get_context(buggy_file_path, line_number, lines_range)
            remove_context_from_source(hunk, buggy_file_path)

        bug_hunks[bug_id] = hunks

    generate_data(bug_hunks)

    # Embedding for RAG
    print("Embedding...")
    rag = rag_utils.RAG("BugAID")
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
