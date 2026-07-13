---
title: "Rename config field max_chunk_chars to max_sentence_chars"
labels:
  - ready-for-agent
created: 2026-07-13
---

## What to build

Rename the config field `max_chunk_chars` to `max_sentence_chars` throughout the config layer. This covers the Settings class field, the Pydantic field description, the TTSConfig dataclass field, the main.py wiring, engine.py config reference, and the config.yml YAML key (with CLI flag and env var comments). Update the description from "text chunk" to "text sentence". Update all test fixtures that reference this config field.

This is a breaking change — no backward compatibility for the old YAML key, CLI flag, or env var.

## Acceptance criteria

- [x] `config.py`: Field renamed to `max_sentence_chars` with updated description
- [x] `config.yml`: YAML key, CLI comment, env var comment renamed
- [x] `models.py`: `TTSConfig.max_chunk_chars` → `max_sentence_chars`
- [x] `main.py`: wiring updated
- [x] `engine.py`: `self._config.max_chunk_chars` → `self._config.max_sentence_chars`
- [x] Test fixtures in `conftest.py`, `test_engine.py`, `test_tts_models.py` updated
- [x] `config.yml` comment no longer references "text chunk"
- [x] All tests pass

## Blocked by

- None - can start immediately
