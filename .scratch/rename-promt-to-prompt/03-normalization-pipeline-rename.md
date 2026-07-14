---
title: "03 — Normalization pipeline rename: promt → prompt"
labels:
  - ready-for-agent
created: 2026-07-14
---

## What to build

Rename all `promt`-rooted identifiers in the LLM-based text normalization pipeline: factory, normalizer, and their tests.

Changes:
- `src/tts/preprocessing/text_normalizer_factory.py`: All local variables (`promt` → `prompt`, `promt_text` → `prompt_text`, `promt_model` → `prompt_model`, `default_promt` → `default_prompt`), method call targets (`get_promt` → `get_prompt`), field accesses (`promt_id` → `prompt_id`, `promts` → `prompts`, `default_promt` → `default_prompt`)
- `src/tts/preprocessing/openai_text_normalizer.py`: Field access `default_promt` → `default_prompt`
- `tests/test_text_normalizer_factory.py`: All imports, constructor calls, method calls, test method names, local variables
- `tests/test_openai_text_normalizer.py`: All `default_promt=` kwargs → `default_prompt=`
- `tests/test_voice_normalization_e2e.py`: Inline YAML keys (`promt_id:` → `prompt_id:`, `promts:` → `prompts:`)

## Acceptance criteria

- [x] All `promt` variables/targets renamed in `text_normalizer_factory.py`
- [x] `default_promt` renamed in `openai_text_normalizer.py`
- [x] All test references updated
- [x] `pytest tests/test_text_normalizer_factory.py tests/test_openai_text_normalizer.py tests/test_voice_normalization_e2e.py -v` passes

## Blocked by

- #2 (Storage + config rename)
