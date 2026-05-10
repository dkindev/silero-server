---
title: "Remove TTS_MODEL_PATH configuration"
labels:
  - ready-for-human
created: 2026-05-10
---

## What to build

Remove the unused `TTS_MODEL_PATH` environment variable and associated `./models` directory references throughout the codebase. The Silero TTS library uses the default PyTorch cache location (`~/.cache/torch/hub/`) automatically - no custom path needed.

## Changes required

- `src/config.py`: Remove `tts_model_path` field from Settings class
- `.env.example`: Remove `TTS_MODEL_PATH=./models` line
- `README.md`: Remove TTS_MODEL_PATH row from environment variables table
- `docs/stages/0.md`: Remove TTS_MODEL_PATH references
- `Dockerfile`: Remove `RUN mkdir -p models`

## Acceptance criteria

- [x] `tts_model_path` field removed from `src/config.py`
- [x] `TTS_MODEL_PATH` removed from `.env.example`
- [x] TTS_MODEL_PATH documentation removed from README.md
- [x] TTS_MODEL_PATH references removed from docs/stages/0.md
- [x] `mkdir -p models` removed from Dockerfile
- [x] Application still starts and health check passes

## Blocked by

None - can start immediately