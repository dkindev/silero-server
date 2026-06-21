---
title: "Refactor config_storage and model tests"
labels:
  - ready-for-agent
created: 2026-06-19
---

## What to build

Refactor `test_config_storage.py` (624 lines) and `test_tts_models.py` (195 lines) to use the shared fixtures from `conftest.py`.

Changes:
- Move inline imports (`from src.tts.config_storage import SileroTTSYamlConfigStorage`) to module-level imports
- Replace inline `import yaml` inside function bodies with conftest helpers
- Use `make_model`, `make_voice`, `make_config_file`, `make_merged_yaml` from conftest instead of redefining data inline
- Remove `make_merged_yaml` from test_config_storage.py (now in conftest)
- No functional changes to test coverage

## Acceptance criteria

- [x] All imports are moved to module level (no late imports)
- [x] `make_merged_yaml` removed from test_config_storage.py (now in conftest)
- [x] Duplicate TTSConfigModel construction replaced with conftest helpers
- [x] `pytest tests/test_config_storage.py tests/test_tts_models.py` passes
- [x] Test coverage is identical (no tests removed or simplified in assertions)

## Blocked by

- `01-create-shared-test-infrastructure`
