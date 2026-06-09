---
id: 2
title: "Text preprocessing — RuTextPreprocessor for Russian locale"
labels:
  - ready-for-agent
created: 2026-06-09
---

## What to build

Add a locale-specific `RuTextPreprocessor` that uses `razdel.sentenize` for linguistically-aware Russian sentence splitting, and register it in the factory dict so `ru_RU` requests use it instead of the base `TextPreprocessor`.

### RuTextPreprocessor

Extend the base `TextPreprocessor` class. Override only `process_text` — the SSML handling is inherited from the base class.

`process_text` uses `razdel.sentenize` to split normalized text into sentences instead of the base class's regex split on `[.!?\n]`. The rest of the chunking pipeline (punctuation split → word split → hard char split → assembly) is inherited via the shared helper functions `split_by_minor_characters` and `split_by_words` on the base class.

### Registration

Add to `_TEXT_PREPROCESSOR_BUILDERS` in the factory module:

```python
_TEXT_PREPROCESSOR_BUILDERS["ru_RU"] = RuTextPreprocessor
```

`ru_RU` requests will now get linguistically-aware sentence boundaries. Other locales continue using the base `TextPreprocessor`.

### Tests

- Unit tests for `RuTextPreprocessor.process_text` with Russian text: normal sentences, long sentences without punctuation, mixed punctuation, empty input, text with unsupported characters filtered by `symbols`
- Verify `razdel` correctly handles Russian sentence boundaries (e.g. abbreviations like "т.е." are not treated as sentence ends)

## Acceptance criteria

- [x] `RuTextPreprocessor.process_text` uses `razdel.sentenize` for Russian sentence splitting
- [x] Long Russian sentences are split via punctuation → words → hard char fallback
- [x] `ru_RU` is registered in `_TEXT_PREPROCESSOR_BUILDERS` and returned from the factory
- [x] Unit tests cover Russian edge cases (abbreviations, mixed punctuation, empty text, char filtering)

## Blocked by

- [#1](01-engine-factory-integration.md) — Engine factory integration + `TTS_MAX_CHUNK_CHARS` must be merged first (the factory dict and engine integration must exist before registering a locale-specific preprocessor)
