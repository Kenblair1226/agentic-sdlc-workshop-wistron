---
name: secure-fastapi-endpoint
description: Implement or remediate a FastAPI endpoint with validated input, safe data access, explicit errors, and regression tests.
---

# Secure FastAPI endpoint workflow

Use this skill when adding an API endpoint or fixing an endpoint reported by CodeQL or
code review.

1. Read the route, response model, repository code, tests, and issue acceptance criteria.
2. Identify every user-controlled value and constrain it with FastAPI/Pydantic types.
3. Keep database access parameterized. Do not use string formatting for SQL.
4. Remove dynamic execution such as `eval`, `exec`, or user-controlled shell commands.
5. Replace stack-trace responses with a stable public error and preserve diagnostic detail
   only through the project's safe logging pattern.
6. Add regression tests for the original exploit or failure mode and normal behavior.
7. Run `python scripts/validate.py` and the relevant targeted tests.
8. In the PR summary, map each finding to its fix and identify any residual risk.

