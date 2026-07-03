---
title: "Add normalization entries and promts to data.yml + verify end-to-end"
labels:
  - done
created: 2026-07-03
---

## What to build

Add actual `normalization` entries under voice entries and the `promts` array to `data.yml`. Verify the full flow works end-to-end: voice-specific normalization overrides system defaults, enabled:false skips normalization, missing VoiceNormalization falls back to system defaults.

## Acceptance criteria

- [x] `data.yml` contains `normalization` section under at least one voice entry with `text` and/or `ssml` sub-keys
- [x] Each normalization entry has `enabled`, `type`, and optionally `promt_id` fields
- [x] `data.yml` contains top-level `promts` array with at least one `Promt` entry (id, text, model)
- [x] End-to-end: voice with VoiceNormalization uses override settings
- [x] End-to-end: voice without VoiceNormalization falls back to system defaults from config.yml
- [x] End-to-end: voice with `enabled: false` skips normalization entirely

## Blocked by

- Slice 3: Factory integration + wiring must be complete

## Done

Integration tests added in `tests/test_voice_normalization_e2e.py` using mock YAML fixtures. All 3 end-to-end scenarios verified:
- LLM voice normalization → OpenAiTextNormalizer
- Disabled normalization → None
- No normalization → falls back to PlainTextNormalizer (system default)
