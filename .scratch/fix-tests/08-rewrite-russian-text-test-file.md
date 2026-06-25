---
title: "Rewrite Russian text test file for new TextSentenizer API"
labels:
  - ready-for-agent
created: 2026-06-25
---

## What to build

`tests/test_ru_text_preprocessor.py` imports `RuTextPreprocessor` which no longer exists. It was replaced by `RuSimpleTextSentenizer` with a different method signature.

Rewrite the 7 tests to use the new API.

### Test mapping

(`TestRuTextPreprocessor` → `TestRuSimpleTextSentenizer`)

| Old call | New call |
|---|---|
| `RuTextPreprocessor().process_text(text, limit, avail)` | `RuSimpleTextSentenizer().text_to_sentences(text, limit)` |

### Pure splitting tests (just need `text_to_sentences`):

- `test_short_text_returns_single_chunk`
- `test_splits_on_sentence_boundary`
- `test_razdel_handles_abbreviations` — verify `razdel.sentenize` doesn't split on "т.е."
- `test_long_sentence_splits_on_comma`
- `test_hard_splits_giant_word`

### Normalization + splitting tests (need `SimpleTextNormalizer` + sentenizer):

- `test_strips_unsupported_characters`: `SimpleTextNormalizer().normalize_text(text, avail)` → `RuSimpleTextSentenizer().text_to_sentences(normalized, limit)`
- `test_empty_after_normalization_returns_empty`: same two-step

### Imports needed

```python
from src.tts.preprocessing import RuSimpleTextSentenizer, SimpleTextNormalizer
```

### File rename (optional)

Rename `test_ru_text_preprocessor.py` → `test_ru_text_sentenizer.py` to match the new naming convention.

## Acceptance criteria

- [x] All 7 tests pass
- [x] `razdel`-based sentence splitting works for Russian (abbreviations like "т.е." and "т.д.")
- [x] Character stripping works via the two-step normalize → sentenize pipeline
- [x] No other tests are broken

## Blocked by

- [#4](04-fix-sentenizer-return-types.md) — Return types must be `list[str]` before sentenizer tests can pass
