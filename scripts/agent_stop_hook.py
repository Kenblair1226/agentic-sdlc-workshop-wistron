from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def changed_paths() -> set[str]:
    commands = [
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "diff", "--name-only", "origin/main...HEAD"],
    ]
    paths: set[str] = set()
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0:
            paths.update(completed.stdout.splitlines())
    return paths


def main() -> int:
    # Consume the hook payload so future versions can inspect it without changing the interface.
    sys.stdin.read()
    commands = [[sys.executable, "scripts/validate.py", "--fast"]]
    if "app/routers/products.py" in changed_paths():
        commands.append([sys.executable, "-m", "pytest", "-q", "-m", "lab1"])

    outputs: list[str] = []
    failed = False
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        outputs.extend(part for part in [completed.stdout, completed.stderr] if part)
        if completed.returncode != 0:
            failed = True
            break

    if not failed:
        print(json.dumps({"decision": "allow"}))
        return 0

    output = "\n".join(outputs).strip()
    reason = (
        "Repository validation failed. Fix the reported lint or test failures, then rerun "
        f"`python scripts/validate.py --fast`.\n\n{output[-5000:]}"
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
