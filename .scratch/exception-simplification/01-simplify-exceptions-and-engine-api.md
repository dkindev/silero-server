---
title: "Simplify Exceptions + Engine Validation API"
labels:
  - ready-for-human
closed: 2026-05-21
created: 2026-05-21
---

## What to build

Collapse the TTS exception hierarchy to a single `TTSEngineError` class, and add domain-query methods to the engine for use by the endpoint layer.

**Exception changes:**
- Remove `InvalidLocaleError`, `InvalidVoiceError`, `InvalidInputTypeError`, `InvalidOutputTypeError`, `TTSProcessingError`
- `TTSEngineError.__init__(self, message)` — passes `message` to `Exception.__init__`, no longer accepts `locale`/`voice`/`status_code` fields
- `TTSProcessingError` usage in the provider (`SileroTTSModelProvider`) replaced with `TTSEngineError`
- `process()` internal validation raises `TTSEngineError` instead of removed subclasses

**Engine API additions:**
- `has_locale(locale: str) -> bool` — returns `True` if locale is in the configured locales
- `has_voice(locale: str, voice_name: str) -> bool` — returns `True` if the voice exists under that locale
- `get_input_types() -> tuple[str, ...]` — returns `("TEXT", "SSML")`

`process()` retains its current signature (including `output_type`) and internal validation — no endpoint changes in this slice. The existing validation in `process()` is unchanged in logic, only the exception type changes.

## Acceptance criteria

- [x] `exceptions.py` contains only `TTSEngineError` with `message`-only constructor
- [x] `InvalidLocaleError`, `InvalidVoiceError`, `InvalidInputTypeError`, `InvalidOutputTypeError`, `TTSProcessingError` removed from all imports and usages
- [x] `SileroTTSEngine` has `has_locale()`, `has_voice()`, `get_input_types()` methods
- [x] `SileroTTSModelProvider` raises `TTSEngineError` instead of `TTSProcessingError`
- [x] `process()` raises `TTSEngineError` for invalid locale/voice/input_type/output_type
- [x] All engine, provider, factory, and model exception tests pass with `TTSEngineError`

## Blocked by

None - can start immediately
