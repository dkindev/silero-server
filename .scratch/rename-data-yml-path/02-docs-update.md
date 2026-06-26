---
title: "Rename models_config_path to data_yml_path — documentation"
labels:
  - ready-for-agent
created: 2026-06-26
---

## What to build

Update `README.md` to reflect the rename of `models_config_path` to `data_yml_path` and `data/models.yml` to `data/data.yml`.

Changes needed:

- **CLI flag**: Update `--tts_models_config_path` → `--tts_data_yml_path` in the options table and narrative text.
- **Env var**: Update `TTS_MODELS_CONFIG_PATH` → `TTS_DATA_YML_PATH` in the environment variables table.
- **YAML examples**: Update `models_config_path: data/models.yml` → `data_yml_path: data/data.yml` in the config.yml example block.
- **Prose references**: Update all `` `data/models.yml` `` → `` `data/data.yml` `` throughout the document (user guide sections that reference the file path).

Also update `src/silero_server.egg-info/PKG-INFO` with the same three categories of changes (CLI flag, env var, YAML example).

## Acceptance criteria

- [x] No remaining references to `models_config_path`, `TTS_MODELS_CONFIG_PATH`, or `--tts_models_config_path` in README.md
- [x] No remaining references to `` `data/models.yml` `` in README.md
- [x] PKG-INFO is in sync with README

## Blocked by

- Rename models_config_path to data_yml_path — core code, file, and config (`01-core-rename.md`)
