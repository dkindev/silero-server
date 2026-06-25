---
title: "Rewrite text/SSML test file for new TextSentenizer API"
labels:
  - ready-for-agent
created: 2026-06-25
---

## What to build

`tests/test_text_preprocessor.py` imports `TextNormalizer` and calls `.process_text()` / `.process_ssml()` — methods that no longer exist. The old `TextPreprocessor` class has been replaced by separate `TextSentenizer` and `TextNormalizer` hierarchies.

Rewrite the 11 tests to use the new API.

### Test mapping

**SSML tests** (`TestTextPreprocessorProcessSSML` → `.text_to_sentences` on `SsmlSentenizer(SimpleTextSentenizer())`):

| Old call | New call |
|---|---|
| `TextNormalizer().process_ssml(text, limit, avail)` | `SsmlSentenizer(SimpleTextSentenizer()).text_to_sentences(text, limit)` |

- `test_valid_ssml_preserves_structure`
- `test_invalid_ssml_falls_back_to_text_split`
- `test_ssml_splits_long_text_and_reopens_tags`

**Text splitting tests** (`TestTextPreprocessorProcessText` → `.text_to_sentences` on `SimpleTextSentenizer()`):

| Old call | New call |
|---|---|
| `TextNormalizer().process_text(text, limit, avail)` | `SimpleTextSentenizer().text_to_sentences(text, limit)` |

- `test_short_text_returns_single_chunk`
- `test_long_text_splits_on_sentence_boundary`
- `test_long_sentence_splits_on_minor_punctuation`
- `test_splits_by_words_when_no_punctuation`
- `test_hard_splits_giant_word`

**Normalization + splitting tests** — need a two-step pipeline:

- `test_strips_unsupported_characters`: `SimpleTextNormalizer().normalize_text(text, avail)` → `SimpleTextSentenizer().text_to_sentences(normalized, limit)`
- `test_empty_after_normalization_returns_empty`: same two-step

### Imports needed

```python
from src.tts.preprocessing import SimpleTextNormalizer, SimpleTextSentenizer, SsmlSentenizer
```

### File rename (optional)

Rename `test_text_preprocessor.py` → `test_text_sentenizer.py` to match the new naming convention.

## Acceptance criteria

- [x] All 11 tests pass
- [x] Each test matches the same behavioral expectations as the original (check boundaries, split behavior, character stripping)
- [x] No other tests are broken

## Blocked by

- [#4](04-fix-sentenizer-return-types.md) — Return types must be `list[str]` before sentenizer tests can pass
- [#5](05-fix-ssml-tag-splitting-regex.md) — SSML tests require tags to be preserved by the split regex
