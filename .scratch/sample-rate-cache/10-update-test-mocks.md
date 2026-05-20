---
title: "Update test mocks and method references"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Update all 48+ test references: rename `get_model_path` → `get_model`, adjust return values from `str` to `tuple[str, list[int]]`.

## Acceptance criteria

- [x] All test files updated
- [x] All mocks return correct tuple type

## Blocked by

.scratch/sample-rate-cache/06-rename-get-model-method.md