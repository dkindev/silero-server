---
title: "Rewrite README.md"
labels:
  - ready-for-agent
created: 2026-06-19
---

## What to build

Full rewrite of `README.md` to match the actual codebase. The current README is significantly outdated:

**Fixes needed:**
- Replace the "Quick Start" section: remove `uvicorn src.main:app --reload` (the server is a Wyoming TCP server, not an ASGI HTTP app). Replace with `python -m src.main`. Fix Docker run port from 8000 to 10200.
- Replace the "API Endpoints" section (currently describes a non-existent HTTP REST API: GET /health, GET /locales, GET /voices, GET/POST /process) with a Wyoming protocol description explaining Describe/Info events, Synthesize requests, and audio streaming.
- Replace the "Environment Variables" table to match the actual `Settings` model: remove `TTS_MAX_TEXT_LENGTH`, `TTS_ALLOWED_ORIGINS`, `TTS_CONFIG_PATH`; add `TTS_URI`, `TTS_ZEROCONF`, `TTS_ENV_TYPE`, `TTS_MODELS_CONFIG_PATH`, `TTS_MODELS_DIR`, `TTS_MODELS_YML_URL`, `TTS_MODELS_YML_HASH`.
- Replace the "Configuration" section documenting `silero-to-mary-config.yml` with docs for the actual `data/models.yml` format (merged structure with `models > locales > voices` fields: `language`, `enabled`, `warmup`, `hash_prefix`, `speaker`).
- Add a new "Configuration Priority" section documenting the chain: CLI args > environment variables > config.yml > defaults.
- Add a CLI args reference table.
- Fix the "Customization" section (references Mary-TTS locales, needs update to match the actual config format).
- Add a Docker volumes section documenting mounts for config.yml, data/models.yml, and models/.
- Keep: Development, CI/CD, License sections (they're accurate).

## Acceptance criteria

- [x] No references to HTTP REST API, uvicorn, or Mary-TTS remain
- [x] Quick Start runs the server with the correct command (`python -m src.main`)
- [x] Env var table matches the actual `TtsSettings` and `TorchSettings` models
- [x] CLI args table documents all `--flag` options from `CliArgsSource`
- [x] `config.yml` and `data/models.yml` formats are documented correctly
- [x] Configuration priority (CLI > ENV > config.yml > Defaults) is documented
- [x] Docker section uses correct port (10200) and documents volume mounts

## Blocked by

None - can start immediately
