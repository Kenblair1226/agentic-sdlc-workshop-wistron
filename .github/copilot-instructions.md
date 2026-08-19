# Repository context

This is a Python 3.10+ FastAPI product catalog used in an AI coding agent workshop.
Keep changes small, reviewable, and suitable for teaching.

## Required commands

Install dependencies with:

```bash
python -m pip install -r requirements-dev.txt
```

Before finishing any change, run:

```bash
python scripts/validate.py
```

For the Lab 1 feature, also run:

```bash
pytest -q -m lab1
```

## Engineering rules

- Preserve existing endpoint response shapes unless the issue explicitly changes them.
- Validate all user-controlled input with FastAPI or Pydantic constraints.
- Use parameterized SQL queries. Never concatenate or interpolate user input into SQL.
- Never use `eval`, `exec`, or shell execution with user-controlled input.
- Do not expose stack traces, credentials, tokens, or personal data in API responses or logs.
- Follow the existing router, model, and repository separation.
- Add or update tests for every behavior change and regression fix.
- Prefer explicit types and small functions over broad exception handling.
- Do not disable Ruff, tests, CodeQL, or security checks to make a change pass.

## Pull request expectations

Summarize the behavior change, security impact, tests run, and any assumptions. Call out
requirements that need human product or security decisions.

