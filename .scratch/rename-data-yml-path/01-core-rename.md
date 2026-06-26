---
title: "Rename models_config_path to data_yml_path — core code, file, and config"
labels:
  - ready-for-agent
created: 2026-06-26
---

## What to build

Rename the `TtsSettings.models_config_path` configuration field to `data_yml_path` and its associated files. This is a strict rename with no backward compatibility — the old `TTS_MODELS_CONFIG_PATH` env var, `--tts_models_config_path` CLI flag, and `models_config_path` YAML key will no longer be accepted.

Changes needed:

- **`src/config.py`**: Rename the field `models_config_path` to `data_yml_path`. Update the `validation_alias` to `AliasChoices("data_yml_path", "TTS_DATA_YML_PATH")`. Update the default value from `"data/models.yml"` to `"data/data.yml"`. Update the docstring.
- **`src/main.py`**: Change `settings.tts.models_config_path` to `settings.tts.data_yml_path`.
- **`data/models.yml`**: Rename the file to `data/data.yml`.
- **`config.yml`**: Change `models_config_path: data/models.yml` to `data_yml_path: data/data.yml`.
- **`.env.example`**: Change `TTS_MODELS_CONFIG_PATH=data/models.yml` to `TTS_DATA_YML_PATH=data/data.yml`.
- **`.env`**: Change `# TTS_MODELS_CONFIG_PATH=data/models.yml` to `# TTS_DATA_YML_PATH=data/data.yml`.

Note: The `models.yml` file cached in the models directory by `_resolve_tts_model` (the Silero upstream registry) is a different file and must NOT be renamed. Only the project's local config file at `data/models.yml` is affected.

No test files need changes — all `models.yml` references in tests mock the Silero registry, not the local config file.

## Acceptance criteria

- [x] `server --help` shows `--tts_data_yml_path` (not `--tts_models_config_path`)
- [x] Setting `TTS_DATA_YML_PATH` env var overrides the path
- [x] `data/data.yml` exists and `data/models.yml` does not
- [x] `python -c "from src.config import get_settings; print(get_settings().tts.data_yml_path)"` prints `"data/data.yml"`
- [x] Server starts successfully with default config
- [x] Old env var `TTS_MODELS_CONFIG_PATH` is ignored (no fallback)

## Blocked by

None - can start immediately
