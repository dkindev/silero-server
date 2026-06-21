---
title: "Fix config test assertions"
labels:
  - ready-for-agent
created: 2026-06-19
---

## What to build

Fix `test_config.py` which accesses `settings.TTS_URI` and `settings.TTS_ZEROCONF` — these don't exist as Python attribute names. The actual field names are `settings.uri` and `settings.zeroconf`. The env var aliases (`TTS_URI`, `TTS_ZEROCONF`) are only used for loading from environment variables, not for attribute access.

Also fix the expected default values:
- `uri` defaults to `"tcp://127.0.0.1:10200"` (not `tcp://0.0.0.0:10200`)
- `zeroconf` defaults to `"silero"` (not `""`)

Add a test that loads `config.yml` explicitly to verify the YamlConfigSettingsSource integration works end-to-end.

## Acceptance criteria

- [x] `settings.uri` is used instead of `settings.TTS_URI`
- [x] `settings.zeroconf` is used instead of `settings.TTS_ZEROCONF`
- [x] Default value assertions match the actual `Settings` field defaults
- [x] New test verifies config.yml file source integration
- [x] `pytest tests/test_config.py` passes

## Blocked by

None - can start immediately
