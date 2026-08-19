---
on:
  issues:
    types: [opened, edited, reopened]

permissions:
  contents: read
  issues: read
  copilot-requests: write

safe-outputs:
  threat-detection: false
  add-labels:
    allowed:
      - bug
      - feature
      - question
      - needs-info
      - priority/p0
      - priority/p1
      - priority/p2
      - duplicate
    max: 4
  add-comment:
    max: 1
---

# Issue Triage Assistant

Review the triggering issue and do three things:

1. Classify the issue by type and priority, then add the matching labels.
2. Identify likely duplicates from existing open and recent closed issues.
3. If required details are missing, ask concise clarifying questions in one comment.

Use `duplicate` only when the match is strong and include the issue number in the comment. Use `needs-info` when reproduction steps, expected behavior, or environment details are missing.