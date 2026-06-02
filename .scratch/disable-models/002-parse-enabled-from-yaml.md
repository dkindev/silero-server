---
title: "Parse `enabled` from YAML config"
labels:
  - ready-for-agent
created: 2026-06-02
---

## What to build

Read `enabled` from the YAML `models.<name>.enabled` field in `_load_config_model(...)` method of `SileroTTSYamlConfigStorage`. Default to `true` when the field is absent, so existing configs work unchanged.

## Acceptance criteria

- [x] YAML `models.<name>.enabled: false` disables the model
- [x] YAML without `enabled` field keeps the model enabled (backward compatible)
- [x] YAML `models.<name>.enabled: true` explicitly enables the model
- [x] Mixed YAML with some enabled, some disabled models — only enabled voices/locales exposed

## Blocked by

- `#001` — Add `enabled` field + storage-level filtering
