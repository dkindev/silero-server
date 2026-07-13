---
title: "Rename max_concurrent_chunks_per_request to max_concurrent_sentences_per_request"
labels:
  - ready-for-agent
created: 2026-07-13
---

## What to build

Rename the OpenAI text normalizer's concurrency setting throughout the stack. This controls how many sentences the OpenAI normalizer processes concurrently per request. Rename the field, the config class attribute, the normalizer factory pass-through, the normalizer internals (including error message), and all test references.

## Acceptance criteria

- [x] `config.py`: Field renamed, description updated
- [x] `models.py`: `OpenAiNormalizationConfig` field renamed
- [x] `config.yml`: YAML key, CLI comment, env var comment renamed
- [x] `text_normalizer_factory.py`: Pass-through renamed
- [x] `openai_text_normalizer.py`: Field reference, error message, comment, semaphore reference renamed
- [x] Test method names, local vars, and fixture references in `test_openai_text_normalizer.py` updated
- [x] All tests pass

## Blocked by

- None - can start immediately
