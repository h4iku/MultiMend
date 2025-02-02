from pathlib import Path

# Root of the repository
project_root: Path = Path(__file__).parent.parent
benchmarks_root: Path = project_root / "benchmarks"
data_root: Path = project_root / "data"
outputs_root: Path = project_root / "outputs"

# Hugging Face cache directory
cache_dir: Path = project_root / ".cache"

# Place to store checkpoints
models_root: Path = project_root / "models"
# Place to store cloned models from Hugging Face Hub
cloned_models_dir: Path = models_root / "cloned_models"

# Directories to store raw and preprocessed CoCoNuT training data
coconut_data_dir: Path = data_root / "CoCoNuT"
coconut_java2006: Path = coconut_data_dir / "java/2006"
coconut_python2010: Path = coconut_data_dir / "python/2010"
coconut_javascript2010: Path = coconut_data_dir / "javascript/2010"
coconut_c2005: Path = coconut_data_dir / "c/2005"
coconut_preprocessed_dir: Path = coconut_data_dir / "Preprocessed"

# QuixBugs configs
quixbugs_dir: Path = benchmarks_root / "QuixBugs"
quixbugs_python_buggy_dir: Path = quixbugs_dir / "python_programs"
quixbugs_python_correct_dir: Path = quixbugs_dir / "correct_python_programs"
quixbugs_java_buggy_dir: Path = quixbugs_dir / "java_programs"
quixbugs_java_correct_dir: Path = quixbugs_dir / "correct_java_programs"
quixbugs_genpy_dir: Path = outputs_root / "QuixBugs-Python"
quixbugs_genjava_dir: Path = outputs_root / "QuixBugs-Java"

# Defects4J configs
d4j_root: Path = benchmarks_root / "Defects4J"
d4j_bin: Path = d4j_root / "framework/bin/defects4j"
d4j_gen_dir: Path = outputs_root / "Defects4J"
d4j_tmp_dir: Path = d4j_gen_dir / "tmp"

d4j1_gen_dir: Path = outputs_root / "Defects4J-v1.2"
d4j2_gen_dir: Path = outputs_root / "Defects4J-v2.0"

# Codeflaws configs
codeflaws_data_dir: Path = benchmarks_root / "Codeflaws"
codeflaws_gen_dir: Path = outputs_root / "Codeflaws"

# BugAID configs
bugaid_data_dir: Path = benchmarks_root / "BugAID/data"
bugaid_gen_dir: Path = outputs_root / "BugAID"

results_dir = project_root / "results"

# Embedding DBs
chromadb_path: Path = project_root / "chroma_db"

quixbugs_programs: list[str] = [
    "bitcount",
    "breadth_first_search",
    "bucketsort",
    "depth_first_search",
    "detect_cycle",
    "find_first_in_sorted",
    "find_in_sorted",
    "flatten",
    "gcd",
    "get_factors",
    "hanoi",
    "is_valid_parenthesization",
    "kheapsort",
    "knapsack",
    "kth",
    "lcs_length",
    "levenshtein",
    "lis",
    "longest_common_subsequence",
    "max_sublist_sum",
    "mergesort",
    "minimum_spanning_tree",
    "next_palindrome",
    "next_permutation",
    "pascal",
    "possible_change",
    "powerset",
    "quicksort",
    "reverse_linked_list",
    "rpn_eval",
    "shortest_path_length",
    "shortest_path_lengths",
    "shortest_paths",
    "shunting_yard",
    "sieve",
    "sqrt",
    "subsequences",
    "to_base",
    "topological_ordering",
    "wrap",
]
