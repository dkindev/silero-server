---
title: "02 — Storage + config rename: promt → prompt"
labels:
  - ready-for-agent
created: 2026-07-14
---

## What to build

Rename the `NormalizationPromt` class, all config storage methods, and their internal state to the corrected spelling.

Changes:
- `src/config.py`: `NormalizationPromt` → `NormalizationPrompt`, field `promts` → `prompts`
- `src/tts/config_storage.py`: `get_promt` → `get_prompt`, `_promts` → `_prompts`, `_parse_promts` → `_parse_prompts`, all local variable/parameter names
- `tests/test_config_storage.py`: All import references, method calls, test class/method names, inline YAML keys
- `tests/conftest.py`: `get_promt` mock reference → `get_prompt`

## Acceptance criteria

- [x] `NormalizationPromt` renamed to `NormalizationPrompt` in `src/config.py`
- [x] `promts` field renamed to `prompts` in `BaseNormalizationSettings`
- [x] `get_promt` → `get_prompt` in ABC and implementation
- [x] All private/internal names (`_promts`, `_parse_promts`) renamed
- [x] All test references updated
- [x] `pytest tests/test_config_storage.py -v` passes

## Blocked by

- #1 (Core model rename)
