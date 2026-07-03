---
id: 4
title: "Test OpenAiTextNormalizer"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Create `tests/test_openai_text_normalizer.py` covering `OpenAiTextNormalizer` with `AsyncMock`-based mocking of the OpenAI client.

### Shared fixture

Add to `tests/conftest.py`:

- `mock_openai_client` — `AsyncMock(spec=AsyncOpenAI)` with `chat.completions.create` returning a fake response where `choices[0].message.content = "normalized text"`. Each test can override the mock's side_effect or return_value per-scenario.

### Tests

| Test | Scenario |
|------|----------|
| `test_single_chunk_normalized_successfully` | One chunk → normalized result |
| `test_multiple_chunks_yielded_in_order` | Three chunks → results yield in original order regardless of completion timing |
| `test_api_failure_falls_back_to_original` | `create` raises exception → original text returned |
| `test_empty_response_falls_back_to_original` | API returns `""` → original text returned |
| `test_negative_timeout_raises_value_error` | `OpenAiNormalizationConfig(timeout=-1)` in `__init__` |
| `test_non_positive_max_concurrent_raises_value_error` | `max_concurrent_chunks_per_request=0` in `__init__` |
| `test_empty_chunks_iterator_yields_nothing` | No input chunks → generator yields nothing |
| `test_semaphore_respects_concurrency_limit` | Verify `max_concurrent_chunks_per_request` bounds concurrent API calls |
| `test_task_cancellation_on_generator_cleanup` | Cancel generator mid-flight → pending tasks are cancelled |

### Mocking strategy

Use `unittest.mock.AsyncMock` (Python 3.8+) matching the existing project pattern. For ordering test, use `asyncio.sleep` or `Event.wait` to simulate out-of-order completions.

## Acceptance criteria

- [x] `tests/test_openai_text_normalizer.py` exists with `TestOpenAiTextNormalizer`
- [x] `tests/conftest.py` has `mock_openai_client` fixture
- [x] Happy path, ordering, fallback, validation, edge cases all covered
- [x] All tests pass with `pytest`

## Blocked by

None - can start immediately
