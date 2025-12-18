import json
import string
from collections import ChainMap, defaultdict
from itertools import chain
from pathlib import Path

import torch
from datasets import Dataset, concatenate_datasets
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    set_seed,
)

from .configs import (
    bugaid_gen_dir,
    bugsinpy_gen_dir,
    codeflaws_gen_dir,
    d4j_gen_dir,
    models_root,
    quixbugs_genjava_dir,
    quixbugs_genpy_dir,
    runbugrunjs_gen_dir,
)
from .rag_utils import RAG

set_seed(42)

# Config
dataset = "QuixBugs-Python"
model_name = "multimend-codet5-small"


def get_checkpoints(checkpoints_dir: Path) -> list[tuple[str, Path]]:
    """Get the list of checkpoints from the checkpoints directory"""

    checkpoints: dict[str, Path] = {}
    for d in checkpoints_dir.iterdir():
        name_parts = d.name.split("-")
        if (
            len(name_parts) == 2
            and name_parts[0] == "checkpoint"
            and name_parts[1].isdigit()
        ):
            checkpoints[d.name] = d

    sorted_checkpoints = sorted(
        checkpoints.items(), key=lambda x: int(x[0].split("-")[1])
    )

    return sorted_checkpoints


def load_test_input_from_meta(prefix: str) -> Dataset:
    """Extract source and context from metadata file"""

    def prepare(hunk: str) -> str:
        lines_concat = " ".join([line.strip() for line in hunk.splitlines()])
        return lines_concat.strip()

    n_return = 5
    threshold = 0.5
    rag = RAG(dataset.split("_")[0])
    test_data = defaultdict(list)

    with open(gen_dir / bugs_metadata_file) as meta_file:
        bugs_metadata = ChainMap(*[json.loads(line) for line in meta_file][::-1])

    print("# RAG retrievals...")
    for bugid, hunks in bugs_metadata.items():
        for h, hunk in enumerate(hunks):
            src = prepare(hunk["removed_lines"])
            source = f"{prefix} {src} :"
            context = " ".join(hunk["source_context"][0].split())

            metadata = {"bugid": bugid, "hunk": h}
            rag_result = None
            if src.strip(string.punctuation + string.whitespace):
                docs, metas = rag.retrieve(src, metadata, n_return, threshold)
                rag_result = f" ".join(docs)

            print(bugid, h)
            if rag_result:
                test_input = f"{source} {rag_result} {context}".replace(
                    tokenizer.eos_token, tokenizer.unk_token
                )
            else:
                test_input = f"{source} {context}".replace(
                    tokenizer.eos_token, tokenizer.unk_token
                )
            test_data["inputs"].append(test_input)

    test_dataset = Dataset.from_dict(test_data)
    return test_dataset


def tokenize_data(examples):
    inputs = tokenizer(
        examples["inputs"],
        padding="longest",
        truncation=True,
        max_length=max_input_length,
    )
    return inputs


def generate_candidates(examples, model, ch_name):
    input_ids = examples["input_ids"].to(device)
    attention_mask = examples["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            num_beams=beam_size,
            early_stopping=True,
            max_length=max_target_length,
            min_length=min_target_length,
            num_return_sequences=num_return_sequences,
            output_scores=True,
            return_dict_in_generate=True,
        )

    outputs_str = tokenizer.batch_decode(
        outputs["sequences"],
        skip_special_tokens=True,
        cleanup_tokenization_spaces=False,
    )

    return {
        "checkpoint": [ch_name] * len(outputs_str),
        "decoded_sequences": outputs_str,
        "sequences_scores": outputs["sequences_scores"].cpu().numpy(),
    }


def save_results(checkpoints_results: list[Dataset]) -> None:
    concatenated_results = concatenate_datasets(checkpoints_results)

    with open(gen_dir / bugs_metadata_file) as meta_file:
        bugs_metadata = ChainMap(*[json.loads(line) for line in meta_file][::-1])

    # Create bugid and hunks for a single checkpoint
    input_bugs_hunks = defaultdict(list)
    for bugid, hunks in bugs_metadata.items():
        input_bugs_hunks["bugid"] += [bugid] * (num_return_sequences * len(hunks))
        input_bugs_hunks["hunk"] += chain.from_iterable(
            [i] * num_return_sequences for i in range(len(hunks))
        )

    # Repeat bugid and hunks in the number of checkpoints
    for colname, coldata in input_bugs_hunks.items():
        input_bugs_hunks[colname] = coldata * len(checkpoints_results)

    bugid_added = concatenated_results.add_column("bugid", input_bugs_hunks["bugid"])
    hunk_added = bugid_added.add_column("hunk", input_bugs_hunks["hunk"])

    hunk_added.to_json(output_dir / f"sequences_{beam_size}.jsonl")


if dataset == "QuixBugs-Python":
    gen_dir = quixbugs_genpy_dir
    bugs_metadata_file = "QuixBugs_Python.jsonl"
    prefix = "Python"
elif dataset == "QuixBugs-Java":
    gen_dir = quixbugs_genjava_dir
    bugs_metadata_file = "QuixBugs_Java.jsonl"
    prefix = "Java"
elif dataset == "Defects4J":
    gen_dir = d4j_gen_dir
    bugs_metadata_file = "Defects4J.jsonl"
    prefix = "Java"
elif dataset == "BugAID":
    gen_dir = bugaid_gen_dir
    bugs_metadata_file = "BugAID.jsonl"
    prefix = "JavaScript"
elif dataset == "Codeflaws":
    gen_dir = codeflaws_gen_dir
    bugs_metadata_file = "Codeflaws.jsonl"
    prefix = "C"
elif dataset == "BugsInPy":
    gen_dir = bugsinpy_gen_dir
    bugs_metadata_file = "BugsInPy.jsonl"
    prefix = "Python"
elif dataset == "RunBugRun-JS":
    gen_dir = runbugrunjs_gen_dir
    bugs_metadata_file = "RunBugRun-JS.jsonl"
    prefix = "JavaScript"
else:
    raise ValueError("Wrong dataset name")


checkpoints_dir = models_root / model_name
output_dir = gen_dir / f"outputs-{model_name.split('-')[0]}"

max_input_length = 512
max_target_length = 256
min_target_length = 0
beam_size = 100
num_return_sequences = 100
batch_size = 1
num_checkpoints = 5

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

checkpoints = get_checkpoints(checkpoints_dir)
tokenizer = AutoTokenizer.from_pretrained(checkpoints[0][1])

test_dataset = load_test_input_from_meta(prefix)
test_dataset.to_json(output_dir / "generated_input.jsonl")

print("Tokenizing...")
tokenized_test_dataset = test_dataset.map(
    tokenize_data,
    batched=True,
    remove_columns=test_dataset.column_names,
)
tokenized_test_dataset.set_format("torch")
output_dir.mkdir(exist_ok=True)

checkpoints_results: list[Dataset] = []
for ch_name, checkpoint in checkpoints[-num_checkpoints:]:
    print(f"Generating from {ch_name}...")
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint).to(device)
    results = tokenized_test_dataset.map(
        lambda examples: generate_candidates(examples, model, ch_name),
        batched=True,
        batch_size=batch_size,
        remove_columns=tokenized_test_dataset.column_names,
    )
    checkpoints_results.append(results)
    torch.cuda.empty_cache()

save_results(checkpoints_results)
