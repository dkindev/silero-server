---
id: 5
title: "Test TextNormalizerFactory"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Create `tests/test_text_normalizer_factory.py` covering the two-level dispatch in `TextNormalizerFactory`: factory lookup (`_factories`) by locale+format, then builder lookup (`_builders`) by locale+format+type.

### Fixture dependency

Reuses `default_normalization_settings` fixture from issue #03 (must be implemented first).

### Tests

| Test | Scenario | Expected |
|------|----------|----------|
| `test_text_simple_returns_plain_text_normalizer` | `text` + `SIMPLE` + default locale | `PlainTextNormalizer` |
| `test_ssml_simple_returns_ssml_normalizer` | `ssml` + `SIMPLE` + default locale | `SsmlNormalizer` |
| `test_text_llm_returns_openai_normalizer` | `text` + `LLM` + configured prompt + valid client | `OpenAiTextNormalizer` |
| `test_text_llm_no_prompt_returns_none` | Locale not in `promts` dict | `None` |
| `test_text_llm_no_client_returns_none` | `openai_client=None` | `None` |
| `test_raises_type_error_for_none_voice` | `voice=None` | `TypeError` |
| `test_text_normalization_disabled_returns_none` | `text.enabled=False` | `None` |
| `test_ssml_normalization_disabled_returns_none` | `ssml.enabled=False` | `None` |
| `test_locale_specific_factory_used_over_default` | Locale key registered in `_factories` | Locale builder called, not `default__...` |
| `test_no_builder_found_logs_warning_and_returns_none` | Unknown locale+type combination | Warning logged, returns `None` |
| `test_llm_with_none_promts_returns_none` | `settings.promts=None` | `None` |

### Mocking strategy

- Mock `AsyncOpenAI` client for LLM tests
- Build `NormalizationSettings` with custom `promts` dicts for locale-specific scenarios
- Build `Voice` with specific locale via `helpers.make_voice`

## Acceptance criteria

- [x] `tests/test_text_normalizer_factory.py` exists with `TestTextNormalizerFactory`
- [x] All 11 scenarios pass
- [x] Locale fallback, enable/disable, and missing builder paths covered
- [x] All tests pass with `pytest`

## Blocked by

- Issue #03 — `default_normalization_settings` fixture
