---
title: "Create shared test infrastructure"
labels:
  - ready-for-agent
created: 2026-06-19
---

## What to build

Create `tests/conftest.py` with shared fixtures and helpers extracted from the existing test files. This eliminates duplication of test setup code across files.

Extract:
- `make_models_dir` — creates temp models directory with models.yml and .pt files
- `make_config_file` — creates temp YAML config file with merged structure
- `make_voice` — creates a Voice dataclass instance
- `make_model` — creates a Model dataclass instance
- `collect_chunks` — async helper to collect all chunks from `synthesize_pcm_chunks`
- `_hash_models_yml` — computes SHA256 of a models.yml file
- `make_merged_yaml` — writes and returns path to a merged-structure YAML
- `mock_model` fixture — preconfigured MagicMock with `symbols`, `apply_tts`, fake audio tensor
- `mock_importer` fixture — MagicMock wrapping `PackageImporter.load_pickle`
- `default_tts_config` fixture — prebuilt `TTSConfig` with sensible defaults

## Acceptance criteria

- [x] `tests/conftest.py` exists with all listed fixtures
- [x] No existing test file is modified (infrastructure-only change)
- [x] All existing tests still pass with `pytest tests/`
- [x] Fixtures use `tmp_path` for temp directories (no hardcoded paths)

## Blocked by

None - can start immediately
