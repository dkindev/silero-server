---
title: "Make speaker optional in YAML config with voice_name fallback"
labels:
  - ready-for-agent
created: 2026-06-10
---
## What to build

When loading voice configurations from YAML, if the `speaker` field is missing or
empty (`""`), treat it as optional and default `speaker` to the `voice_name` value.

Normalize "missing" and "empty" identically: `speaker` key absent, `speaker: ""`,
`speaker: null`, and `speaker: "   "` (whitespace only) all produce the same fallback.
Non-empty, non-whitespace values are used as-is.

The `VoiceConfig` dataclass (`voice_name`, `speaker`, `model`, `gender`) is not
changed — `speaker` remains a required field at the Python type level. The fallback
is applied during YAML parsing in config loading, before the `VoiceConfig` is
constructed.

No changes to the engine or router are needed — they already consume
`voice_config.speaker`, which will now correctly hold the fallback value.

## Acceptance criteria

- [ ] YAML with `speaker` key missing → `get_voice_config().speaker` equals the voice_name
- [ ] YAML with `speaker: ""` → `get_voice_config().speaker` equals the voice_name
- [ ] YAML with `speaker: "aidar"` → `get_voice_config().speaker` equals `"aidar"` (existing behavior preserved)
- [ ] New tests added for missing and empty-speaker cases
- [ ] CONTEXT.md Voice section notes `speaker` is optional in YAML, defaults to `voice_name`

## Blocked by

None — can start immediately
