---
title: "Update Documentation"
labels:
  - ready-for-human
closed: 2026-05-21
created: 2026-05-21
---

## What to build

Update `CONTEXT.md` to reflect the new validation architecture and simplified exception model.

**Sections to update:**

- **"Validation rules (in engine)"** — rename to "Validation rules" and split into:
  - *Endpoint validation (first line)* — locale, voice, input type, output type, AUDIO checked before engine call; 400/406 returned inline
  - *Engine validation (second line)* — redundant check in `process()` raises `TTSEngineError` → 500
- **"/process Endpoint"** — update parameter table: remove `OUTPUT_TYPE` from engine params, note `OUTPUT_TYPE` validated at endpoint (406 if not AUDIO), add `AUDIO` validation rule
- **"Error Responses"** — keep 400/406/500 status codes but remove language about specific exception subclasses
- **"SileroTTSEngine"** — add `has_locale()`, `has_voice()`, `get_input_types()` to the methods list; remove `output_type` from `process()` signature

Do not change `docs/mary-tts-core-endpoints.md` (it documents the Mary-TTS specification, not our implementation specifics).

## Acceptance criteria

- [x] `CONTEXT.md` accurately describes two-tier validation (endpoint then engine)
- [x] `CONTEXT.md` reflects removed exception subclasses
- [x] `CONTEXT.md` shows updated `process()` signature without `output_type`
- [x] `CONTEXT.md` lists `has_locale()`, `has_voice()`, `get_input_types()` under engine methods
- [x] `docs/mary-tts-core-endpoints.md` is unchanged

## Blocked by

- Move validation to endpoint + remove `output_type` (slice 2)
