---
name: "Lab 2: Security remediation"
about: Remediate reviewed findings in the insecure report endpoint
title: "Remediate security findings in sales report endpoint"
labels: ["lab-2", "security"]
assignees: []
---

## Context

The `/reports/sales` change has completed CodeQL and Copilot code review. Remediate the
confirmed findings without replacing SQLite or changing the public endpoint path.

## Acceptance criteria

- [ ] SQL execution uses parameters rather than string interpolation.
- [ ] The `formula` input cannot execute Python code.
- [ ] API errors do not disclose stack traces or implementation details.
- [ ] Normal requests still return a category, matching items, and numeric total.
- [ ] Regression tests cover SQL injection, code injection, and error disclosure.
- [ ] `python scripts/validate.py` passes.

## Review constraint

Do not blindly fix every comment. In the PR summary, classify each finding as confirmed,
needs human decision, or not applicable.

