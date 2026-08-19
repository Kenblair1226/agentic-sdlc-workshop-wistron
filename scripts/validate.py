from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> int:
    print(f"$ {' '.join(command)}")
    completed = subprocess.run(command, cwd=ROOT, check=False)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run workshop validation checks.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Stop after the first test failure; intended for agent hooks.",
    )
    args = parser.parse_args()

    test_command = [sys.executable, "-m", "pytest", "-q", "-m", "not lab1"]
    if args.fast:
        test_command.extend(["-x", "--maxfail=1"])

    commands = [
        [sys.executable, "-m", "ruff", "check", "app", "tests", "scripts"],
        test_command,
    ]
    for command in commands:
        return_code = run(command)
        if return_code != 0:
            return return_code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

