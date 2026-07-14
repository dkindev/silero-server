---
title: "01 — Core model rename: Promt → Prompt"
labels:
  - ready-for-agent
created: 2026-07-14
---

## What to build

Rename the `Promt` dataclass and its fields in the domain model, plus update all direct references in the corresponding test class.

Changes:
- `src/tts/models.py`: `Promt` → `Prompt`, field `promt_id` → `prompt_id`, field `promts` → `prompts`, field `default_promt` → `default_prompt`
- `tests/test_tts_models.py`: `TestPromt` → `TestPrompt`, all method names and local variable/field references accordingly

This is the foundation slice — downstream slices update consumers of this class.

## Acceptance criteria

- [x] `Promt` class renamed to `Prompt` in `src/tts/models.py`
- [x] All fields (`promt_id`, `promts`, `default_promt`) renamed to corrected spelling
- [x] Test class `TestPromt` and its methods/variables updated
- [x] `pytest tests/test_tts_models.py -v` passes

## Blocked by

None — can start immediately
