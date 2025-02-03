"""Finding the buggy lines in Defects4J dataset by comparing buggy and correct versions"""

import contextlib
import difflib
import json
import re
import shlex
import shutil
import string
import subprocess
import threading
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import joblib
import pygments
import tree_sitter_java as tsjava
from joblib import Parallel, delayed
from pygments.lexers import JavaLexer
from pygments.token import Comment, String
from tqdm import tqdm
from tree_sitter import Language, Parser
from unidiff import PatchSet

from .. import rag_utils
from ..configs import d4j_bin, d4j_gen_dir, d4j_tmp_dir

java_language = Language(tsjava.language())
parser = Parser(java_language)
query = java_language.query(
    """
    (method_declaration) @method-dec
    (constructor_declaration) @constructor-dec
    """
)

java_lexer = JavaLexer(stripnl=False)


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


def cleanup(
    project_bug_id: str, filename: str, source: str, target: str
) -> tuple[str, str]:
    """Clean up inconsistencies in some files to detect changes more accurately"""

    source_lines = source.splitlines()

    if project_bug_id == "Chart 7":
        source_lines[300:303] = [line + " " for line in source_lines[300:303]]
    elif project_bug_id == "Chart 14":
        target_lines = target.splitlines()
        if filename == "CategoryPlot":
            target_lines[2452] += " "
        elif filename == "XYPlot":
            target_lines[2533] += " "
        target = "\n".join(target_lines)

    elif project_bug_id == "Closure 7":
        source_lines[613:615] = [line + " " for line in source_lines[613:615]]
    elif project_bug_id == "Closure 19":
        source_lines[171] += " "
    elif project_bug_id == "Closure 22":
        source_lines[104] += " "
        source_lines[125] += " "
    elif project_bug_id == "Closure 32":
        source_lines[1388] += " "
    elif project_bug_id == "Closure 56":
        source_lines[241] += " "
    elif project_bug_id == "Closure 66":
        source_lines[515] += " "
    elif project_bug_id == "Closure 106" and filename == "JSDocInfoBuilder":
        source_lines[189] += " "
    elif project_bug_id == "Closure 136" and filename == "RenameVars":
        source_lines[202] += " "
    elif project_bug_id == "Closure 170":
        source_lines[489] += " "
        source_lines[490] += " "

    elif project_bug_id == "Cli 13" and filename == "WriteableCommandLineImpl":
        source_lines[131:134] = [line + " " for line in source_lines[131:134]]
    elif project_bug_id == "Cli 15":
        source_lines[124:128] = [line + " " for line in source_lines[124:128]]
    elif project_bug_id == "Cli 27":
        source_lines[98] += " "
    elif project_bug_id == "Cli 29":
        source_lines[64:68] = [line + " " for line in source_lines[64:68]]
        source_lines[70] += " "

    elif project_bug_id == "Codec 12":
        source_lines[141:144] = [line + " " for line in source_lines[141:144]]
        source_lines[151:158] = [line + " " for line in source_lines[151:158]]

    elif project_bug_id == "Csv 2":
        source_lines[84] += " "
    elif project_bug_id == "Csv 3":
        source_lines[110] += " "
        source_lines[111] += " "

    elif project_bug_id == "Gson 16":
        source_lines[341] += " "

    elif project_bug_id == "JacksonDatabind 4":
        source_lines[74] += " "
        source_lines[101] += " "
    elif project_bug_id == "JacksonDatabind 14":
        source_lines[1576] += " "
    elif project_bug_id == "JacksonDatabind 21":
        source_lines[63:68] = [line + " " for line in source_lines[63:68]]
    elif project_bug_id == "JacksonDatabind 36":
        source_lines[249] += " "
    elif project_bug_id == "JacksonDatabind 52" and filename == "ExternalTypeHandler":
        source_lines[309] += " "
    elif project_bug_id == "JacksonDatabind 81":
        source_lines[763] += " "
        source_lines[796] += " "
        source_lines[830] += " "
    elif project_bug_id == "JacksonDatabind 88":
        source_lines[57] += " "

    elif project_bug_id == "Jsoup 6":
        source_lines[70] += " "
    elif project_bug_id == "Jsoup 36":
        source_lines[163] += " "
    elif project_bug_id == "Jsoup 78":
        source_lines[150:152] = [line + " " for line in source_lines[150:152]]
    elif project_bug_id == "Jsoup 82":
        source_lines[170] += " "

    elif project_bug_id == "Lang 13":
        source_lines[267] += " "
    elif project_bug_id == "Lang 31":
        source_lines[1449] += " "
    elif project_bug_id == "Lang 37":
        source_lines[2961:2963] = [line + " " for line in source_lines[2961:2963]]
    elif project_bug_id == "Lang 64":
        source_lines[191:194] = [line + " " for line in source_lines[191:194]]

    elif project_bug_id == "Math 3":
        source_lines[820] += " "
    elif project_bug_id == "Math 64":
        source_lines[422] += " "
    elif project_bug_id == "Math 79":
        source_lines[1624] += " "
    elif project_bug_id == "Math 34":
        source_lines[210] += "\n"

    elif project_bug_id == "Time 12":
        if filename == "LocalDate":
            source_lines[242] += " "
        elif filename == "LocalDateTime":
            source_lines[235] += " "
    elif project_bug_id == "Time 17":
        source_lines[1177:1179] = [line + " " for line in source_lines[1177:1179]]

    source = "\n".join(source_lines)
    return source, target


def get_diff_lines(
    project_bug_id: str, pid: int, fromfile: Path, tofile: Path, context_size: int = 0
) -> Iterable[str]:
    with (
        open(fromfile, encoding="cp1256") as source_file,
        open(tofile, encoding="cp1256") as target_file,
    ):
        source = remove_comments(source_file.read())
        target = remove_comments(target_file.read())

    source, target = cleanup(project_bug_id, fromfile.stem, source, target)

    diff_lines = difflib.unified_diff(
        source.splitlines(keepends=True),
        target.splitlines(keepends=True),
        fromfile=str(fromfile.relative_to(d4j_tmp_dir / f"{pid}/buggy")),
        tofile=str(tofile.relative_to(d4j_tmp_dir / f"{pid}/fixed")),
        n=context_size,
    )

    return list(diff_lines)


def process_hunks(diff_lines: list[str]) -> list[DiffHunk]:
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

    d4j_gen_dir.mkdir(parents=True, exist_ok=True)
    with (
        open(d4j_gen_dir / "Defects4J.jsonl", "w") as file,
        open(d4j_gen_dir / "rem.txt", "w") as remfile,
        open(d4j_gen_dir / "add.txt", "w") as addfile,
        open(d4j_gen_dir / "context.txt", "w") as ctxfile,
    ):
        for program, hunks in bug_hunks.items():
            file.write(json.dumps({program: [asdict(h) for h in hunks]}) + "\n")
            remfile.writelines(prepare(h.removed_lines) + "\n" for h in hunks)
            addfile.writelines(prepare(h.added_lines) + "\n" for h in hunks)
            ctxfile.writelines(prepare(h.source_context[0]) + "\n" for h in hunks)


def get_file_path(dir_path: Path, class_name: str) -> Path:
    return dir_path / f"{class_name.replace('.', '/')}.java"


def run_d4j_cmd(cmd: str) -> str:
    d4j_cmd = f"perl {d4j_bin} {cmd}"
    args = shlex.split(d4j_cmd)
    result = subprocess.run(args, capture_output=True, check=True, text=True)
    return result.stdout


def checkout_source(
    project_id: str, bug_id: str, buggy: bool, checkout_dir: Path
) -> None:
    checkout_dir.mkdir(parents=True, exist_ok=True)

    cmd = (
        f"checkout -p {project_id} -v {bug_id}{'b' if buggy else 'f'} -w {checkout_dir}"
    )
    run_d4j_cmd(cmd)


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


def worker_func(project_id: str, bug_id: str) -> tuple[str, list[DiffHunk]]:
    """Worker function to process each project bugs"""

    pid = threading.get_ident()

    buggy_checkout_dir = d4j_tmp_dir / f"{pid}/buggy"
    fixed_checkout_dir = d4j_tmp_dir / f"{pid}/fixed"

    # Checkout buggy and fixed versions of the source code
    checkout_source(project_id, bug_id, True, buggy_checkout_dir)
    checkout_source(project_id, bug_id, False, fixed_checkout_dir)
    source_dir_name = run_d4j_cmd(f"export -p dir.src.classes -w {buggy_checkout_dir}")
    modified_classes: list[str] = run_d4j_cmd(
        f"export -p classes.modified -w {buggy_checkout_dir}"
    ).splitlines()

    hunks: list[DiffHunk] = []

    for modified_class in modified_classes:
        buggy_file_path = get_file_path(
            buggy_checkout_dir / source_dir_name, modified_class
        )
        fixed_file_path = get_file_path(
            fixed_checkout_dir / source_dir_name, modified_class
        )

        # if source or target doesn't exist, patch needs creation or deletion of a file
        if buggy_file_path.exists() and fixed_file_path.exists():
            diff_lines = get_diff_lines(
                f"{project_id} {bug_id}", pid, buggy_file_path, fixed_file_path
            )
            file_hunks = process_hunks(diff_lines)

            for hunk in file_hunks:
                line_number = hunk.removed_line_numbers_range[0]
                lines_range = hunk.removed_line_numbers_range[1]
                hunk.source_context = get_context(
                    buggy_file_path, line_number, lines_range
                )
                remove_context_from_source(hunk, buggy_file_path)

            hunks += file_hunks

    return bug_id, hunks


def main():
    check_java_version()

    n_jobs = 6
    bug_hunks: dict[str, list[DiffHunk]] = {}

    projects: dict[str, list[str]] = {}
    projects = {
        pid: run_d4j_cmd(f"bids -p {pid}").splitlines()
        for pid in run_d4j_cmd("pids").splitlines()
    }

    for project_id, bug_ids in projects.items():
        print(project_id)

        with tqdm_joblib(tqdm(total=len(bug_ids))):
            result = Parallel(n_jobs=n_jobs, backend="threading")(
                delayed(worker_func)(project_id, bug_id) for bug_id in bug_ids
            )

        for bug_id, hunks in result:
            bug_hunks[f"{project_id} {bug_id}"] = hunks

    generate_data(bug_hunks)

    print("Generating done! Cleaning temp...")
    # only delete directories in the form of `<int>/[buggy|fixed]`
    for directory in d4j_tmp_dir.iterdir():
        if directory.name.isdecimal():
            shutil.rmtree(directory)

    # Embedding for RAG
    print("Embedding...")
    rag = rag_utils.RAG("Defects4J")
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
