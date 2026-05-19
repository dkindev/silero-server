---
title: "Move _select_sample_rate to models.py with sorting"
labels:
  - ready-for-agent
created: 2026-05-19
---

## What to build

Convert `_select_sample_rate` method from `SileroTTSEngine` to a module-level function in `models.py`. Also add sorting and deduplication of `supported_rates` inside the function to handle unsorted or duplicate input values.

## Acceptance criteria

- [x] Function moved to models.py as module-level function
- [x] supported_rates are sorted and deduplicated before processing
- [x] Function is importable from models.py
- [x] Original logic preserved

## Blocked by

- 01-cached-model-wrapper