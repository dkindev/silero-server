---
title: "Move Validation to Endpoint + Remove output_type"
labels:
  - ready-for-human
closed: 2026-05-21
created: 2026-05-21
---

## What to build

Move input validation from the engine layer to the `/process` endpoint, making the endpoint the primary gatekeeper with proper HTTP status codes. The engine retains validation as a second-line defense (raises `TTSEngineError` → 500).

**Endpoint changes (`process_request`):**
Add validation checks **before** calling `engine.process()`, in this order:
1. `AUDIO != "WAVE_FILE"` → return `400`
2. `not engine.has_locale(LOCALE)` → return `400`
3. `not engine.has_voice(LOCALE, VOICE)` → return `400`
4. `INPUT_TYPE not in engine.get_input_types()` → return `400`
5. `OUTPUT_TYPE != "AUDIO"` → return `406`
6. Call `engine.process(INPUT_TEXT, LOCALE, VOICE, INPUT_TYPE)` — note `output_type` removed

**Engine changes:**
- `process()` signature drops `output_type`: signature becomes `process(text, locale, voice, input_type)` -> `TTSResult`
- Internal validation remains in `process()` but raises `TTSEngineError` (second-line, status 500)

**Removal of per-exception handler registrations:**
- Remove `app.add_exception_handler(InvalidLocaleError, ...)` etc. — only the generic `Exception` handler (returns 500) plus the new inline JSONResponses remain

**Test changes:**
- Router tests: rewrite `TestExceptionHandler` to test `TTSEngineError` → 500 only
- `test_process_invalid_locale_returns_400`: mock `engine.has_locale` returning `False`
- `test_process_invalid_voice_returns_400`: mock `engine.has_voice` returning `False`
- Add tests: invalid input type → 400, invalid output type → 406, invalid AUDIO → 400

## Acceptance criteria

- [x] `/process` returns 400 for unsupported locale, voice, input type, or audio format
- [x] `/process` returns 406 for non-AUDIO output type
- [x] `/process` returns 500 when engine raises `TTSEngineError` (second-line defense)
- [x] `engine.process()` no longer accepts `output_type` parameter
- [x] Router tests verify correct HTTP status codes via inline validation (not exception handlers)
- [x] No references to removed exception subclasses in router code or tests

## Blocked by

- Exception simplification + engine validation API (slice 1)
