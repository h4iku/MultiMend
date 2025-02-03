"""Finding the buggy lines in Codeflaws dataset by comparing buggy and correct versions"""

import csv
import difflib
import json
import string
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pygments
import tree_sitter_c as tsc
from pygments.lexers import CLexer
from pygments.token import Comment, String
from tqdm import tqdm
from tree_sitter import Language, Parser
from unidiff import PatchSet

from .. import rag_utils
from ..configs import codeflaws_data_dir, codeflaws_gen_dir

c_language = Language(tsc.language())
parser = Parser(c_language)
query = c_language.query(
    """
    (function_definition) @function-definition
    """
)

c_lexer = CLexer(stripnl=False)


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
    file_path: Path, line_number: int, lines_range: int
) -> tuple[str, int, int]:
    with open(file_path, "rb") as file:
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
        with open(file_path, encoding="cp1256") as file:
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

    lexed_code = pygments.lex(code, c_lexer)

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


def cleanup(bug_id: str, source: str, target: str) -> tuple[str, str]:
    """Clean up inconsistencies in some files to detect changes more accurately"""

    source_lines = [line.strip() for line in source.splitlines()]
    target_lines = [line.strip() for line in target.splitlines()]

    if bug_id == "53-C-bug-10604869-10605014":
        source_lines[1] = target_lines[1]
    elif bug_id == "9-A-bug-13906641-13906656":
        source_lines[9] = ""
    elif bug_id == "236-A-bug-18003726-18007529":
        source_lines[9:11] = [line + " " for line in source_lines[9:11]]
    elif bug_id == "545-D-bug-12632036-12632228":
        source_lines[21:23] = [line + " " for line in source_lines[21:23]]
    elif bug_id == "673-A-bug-18141268-18141293":
        source_lines[12:14] = [line + " " for line in source_lines[12:14]]
    elif bug_id == "315-A-bug-6149995-6150754":
        source_lines[16:18] = [line + " " for line in source_lines[16:18]]
    elif bug_id == "83-D-bug-488986-488987":
        source_lines[65:67] = [line + " " for line in source_lines[65:67]]
    elif bug_id == "139-A-bug-13580676-13581003":
        source_lines[13:15] = [line + " " for line in source_lines[13:15]]
    elif bug_id == "625-B-bug-17924767-17924788":
        source_lines[55:57] = [line + " " for line in source_lines[55:57]]
    elif bug_id == "515-A-bug-16019620-16019646":
        source_lines[5:8] = [line + " " for line in source_lines[5:8]]
    elif bug_id == "353-D-bug-6175754-6175760":
        source_lines[43:46] = [line + " " for line in source_lines[43:46]]
    elif bug_id == "11-A-bug-18158296-18158311":
        if not source_lines[16].strip():
            source_lines[16] = target_lines[16]
    elif bug_id == "230-B-bug-16820314-16820335":
        source_lines[28] = target_lines[29]
    elif bug_id == "474-A-bug-18022668-18022684":
        source_lines[3] = target_lines[3]

    source = "\n".join(source_lines)
    target = "\n".join(target_lines)
    return source, target


def get_diff_lines(
    bug_id: str, fromfile: Path, tofile: Path, context_size: int = 0
) -> Iterable[str]:
    with (
        open(fromfile, encoding="utf-8") as source_file,
        open(tofile, encoding="utf-8") as target_file,
    ):
        source = remove_comments(source_file.read())
        target = remove_comments(target_file.read())

    source, target = cleanup(bug_id, source, target)

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

    # My diffs should only contain one file since I process each file separately
    assert len(patch_set) == 1
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

    codeflaws_gen_dir.mkdir(parents=True, exist_ok=True)
    with (
        open(codeflaws_gen_dir / "Codeflaws.jsonl", "w", encoding="utf-8") as file,
        open(codeflaws_gen_dir / "rem.txt", "w", encoding="utf-8") as remfile,
        open(codeflaws_gen_dir / "add.txt", "w", encoding="utf-8") as addfile,
        open(codeflaws_gen_dir / "context.txt", "w", encoding="utf-8") as ctxfile,
    ):
        for program, hunks in bug_hunks.items():
            file.write(json.dumps({program: [asdict(h) for h in hunks]}) + "\n")
            remfile.writelines(prepare(h.removed_lines) + "\n" for h in hunks)
            addfile.writelines(prepare(h.added_lines) + "\n" for h in hunks)
            ctxfile.writelines(prepare(h.source_context[0]) + "\n" for h in hunks)


def get_file_path(dir_path: Path, file_name: str) -> Path:
    return dir_path / f"{file_name}.c"


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


def main():
    bug_hunks: dict[str, list[DiffHunk]] = {}

    # Some bugs in Codeflaws have same buggy and fixed programs
    identical_bug_ids = [
        "71-A-bug-18359456-18359477",
        "558-B-bug-12585906-12585920",
        "382-A-bug-8368809-8368827",
        "569-C-bug-12481867-12481905",
        "289-D-bug-3473596-3473601",
        "289-D-bug-3473592-3473601",
        "431-C-bug-15194556-15194577",
        "6-C-bug-12776326-12776346",
    ]

    with open(
        codeflaws_data_dir / "codeflaws-defect-detail-info.txt", newline=""
    ) as metafile:
        reader = csv.reader(metafile, delimiter="\t")

        for row in tqdm(reader):
            bug_id = row[0]

            if bug_id in identical_bug_ids:
                continue

            metadata = row[0].split("-")
            buggy_file_name = f"{metadata[0]}-{metadata[1]}-{metadata[-2]}"
            fixed_file_name = f"{metadata[0]}-{metadata[1]}-{metadata[-1]}"

            hunks: list[DiffHunk] = []

            buggy_file_path = get_file_path(
                codeflaws_data_dir / bug_id, buggy_file_name
            )
            fixed_file_path = get_file_path(
                codeflaws_data_dir / bug_id, fixed_file_name
            )

            diff_lines = list(get_diff_lines(bug_id, buggy_file_path, fixed_file_path))
            hunks = process_hunks(diff_lines)

            for hunk in hunks:
                line_number = hunk.removed_line_numbers_range[0]
                lines_range = hunk.removed_line_numbers_range[1]
                hunk.source_context = get_context(
                    buggy_file_path, line_number, lines_range
                )
                remove_context_from_source(hunk, buggy_file_path)

            bug_hunks[bug_id] = hunks

    generate_data(bug_hunks)

    # Embedding for RAG
    print("Embedding...")
    rag = rag_utils.RAG("Codeflaws")
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
