---
id: 3
title: "Test PlainTextNormalizer + SsmlNormalizer"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Create `tests/test_text_normalizer.py` covering `PlainTextNormalizer` and `SsmlNormalizer` with shared test fixtures for normalization options.

### Shared fixtures

Add to `tests/conftest.py`:

- `normalization_options` — returns `NormalizationOptions(voice, model, silero_model=mock_model)` where `mock_model` already has `symbols` set. Uses `helpers.make_voice` and `helpers.make_model`.
- `default_normalization_settings` — returns `NormalizationSettings()` with all defaults (timeout=5, max_concurrent=2, text.enabled=True, ssml.enabled=False).

### PlainTextNormalizer tests

All tests are async generators — collect results with `[chunk async for chunk in normalizer.normalize_text(iter(chunks), options)]`.

| Test | Scenario |
|------|----------|
| `test_normalizes_text_with_all_available_chars` | Chars in `mock_model.symbols` pass through unchanged |
| `test_filters_unavailable_characters` | Chars outside symbol set are stripped via negated character class regex |
| `test_skips_empty_chunks` | Whitespace-only chunk is dropped from output |
| `test_no_filter_when_silero_model_is_none` | `silero_model=None` → no regex built, text passes through |
| `test_no_filter_when_model_lacks_symbols` | `silero_model` exists without `symbols` attr |
| `test_filters_all_chars_when_symbols_empty` | `symbols=""` removes all non-space chars |
| `test_raises_type_error_for_none_chunks` | `chunks=None` → `TypeError` |
| `test_filtering_is_case_insensitive` | Mixed-case symbols applied with `re.IGNORECASE` |

### SsmlNormalizer tests

| Test | Scenario |
|------|----------|
| `test_preserves_ssml_structure` | Strips whitespace, keeps SSML tags intact |
| `test_skips_empty_chunks` | Whitespace-only chunk dropped |
| `test_raises_type_error_for_none_chunks` | `chunks=None` → `TypeError` |

## Acceptance criteria

- [x] `tests/test_text_normalizer.py` exists with `TestPlainTextNormalizer` and `TestSsmlNormalizer`
- [x] `tests/conftest.py` has `normalization_options` and `default_normalization_settings` fixtures
- [x] `PlainTextNormalizer` tests cover happy path, filtering, empty chunks, None model, None symbols, empty symbols, None input, case-insensitive flag
- [x] `SsmlNormalizer` tests cover happy path, empty chunks, None input
- [x] All tests pass with `pytest`

## Blocked by

None - can start immediately
