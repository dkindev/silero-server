---
title: "Rename max_concurrent_per_model to max_concurrent_sentences_per_model"
labels:
  - ready-for-agent
created: 2026-07-13
---

## What to build

Rename the per-model sentence concurrency limit throughout the stack. The semaphore guards concurrent sentence synthesis per model. Rename the config field (with updated description), the TTSConfig dataclass attribute, the engine semaphore reference, the main.py wiring, the config.yml YAML key (with CLI and env var comments), and all test fixtures.

## Acceptance criteria

- [x] `config.py`: Field renamed to `max_concurrent_sentences_per_model`, description updated from "TTS requests" to "sentences"
- [x] `config.yml`: YAML key, CLI comment (`--max_concurrent_sentences_per_model`), env var comment (`TTS_MAX_CONCURRENT_SENTENCES_PER_MODEL`)
- [x] `models.py`: `TTSConfig` field renamed
- [x] `main.py`: wiring updated
- [x] `engine.py`: semaphore reference updated
- [x] Test fixtures in `conftest.py`, `test_engine.py`, `test_tts_models.py` updated
- [x] All tests pass

## Blocked by

- None - can start immediately
