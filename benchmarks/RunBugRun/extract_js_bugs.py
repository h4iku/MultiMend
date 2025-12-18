import sqlite3
from pathlib import Path

script_dir = Path("__file__").parent
db_path = script_dir / "runbugrun.db"
bugs_dir = script_dir / "jsbugs"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

cursor = conn.execute(
    "SELECT * FROM bugs WHERE language = 2 AND split = 2 AND active = 1"
)
for row in cursor.fetchall():
    bug_dir = bugs_dir / f"{row['problem_id']}-{row['id']}"
    bug_dir.mkdir(parents=True)
    if row["id"] in [1223358, 348266, 768764]:
        # These bugs seem to have swapped buggy and fixed versions based on the testcases!
        (bug_dir / "buggy.js").write_text(row["fixed_code"])
        (bug_dir / "fixed.js").write_text(row["buggy_code"])
    else:
        (bug_dir / "buggy.js").write_text(row["buggy_code"])
        (bug_dir / "fixed.js").write_text(row["fixed_code"])

    tests = conn.execute(
        "SELECT * FROM tests WHERE problem_id = ? AND active = 1", (row["problem_id"],)
    )
    for i, test in enumerate(tests.fetchall()):
        (bug_dir / f"input{i}").write_text(test["input"])
        (bug_dir / f"output{i}").write_text(test["output"])

conn.close()
