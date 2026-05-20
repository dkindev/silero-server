---
title: "SileroTTSModelProvider unit tests"
labels:
  - ready-for-agent
created: 2026-05-20
---

## Parent

[01-silero-tts-model-provider](./01-silero-tts-model-provider.md)

## What to build

Unit tests for `SileroTTSModelProvider.get_model_path()` covering all code paths.

### Test fixtures needed

- A mocked `models.yml` fixture (real YAML structure matching Silero's format) covering multiple languages and models
- A mock HTTP response for `torch.hub.download_url_to_file` (can use `responses` or `pytest-httpserver`)

### Cases to cover

1. **Cache hit**: model `.pt` file already exists on disk → returns path, no HTTP calls
2. **Missing `models.yml`**: downloads from GitHub, saves to disk, then downloads model
3. **Missing `.pt` file, `models.yml` cached**: loads from disk, downloads model via temp file → rename
4. **Malformed `models.yml`**: raises `TTSProcessingError` with delete-hint message
5. **Model URL missing from registry**: raises `TTSProcessingError` with language/model name and delete hint
6. **Download failure**: `RuntimeError` from `torch.hub.download_url_to_file` wrapped as `TTSProcessingError`
7. **Only `package` key supported**: model entry with only `jit` key raises `TTSProcessingError`

## Acceptance criteria

- [x] All 7 cases covered by individual test methods
- [x] Tests use temp directories for isolation
- [x] No real network calls or real model files in any test

## Blocked by

- [01-silero-tts-model-provider](./01-silero-tts-model-provider.md)