---
title: "Add get_promt and get_voice_normalization to config storage"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Add `get_promt(promt_id)` and `get_voice_normalization(voice_id, text_format)` abstract methods to `SileroTTSConfigStorage` ABC. Implement parsing of the `promts` array and `voices.{voice_name}.normalization` sections from `data.yml` in `SileroTTSYamlConfigStorage`. Implement the two lookup methods using internal dicts.

## Acceptance criteria

- [x] `SileroTTSConfigStorage` has abstract method `get_promt(self, promt_id: str) -> Promt | None`
- [x] `SileroTTSConfigStorage` has abstract method `get_voice_normalization(self, voice_id: str, text_format: TextFormat) -> VoiceNormalization | None`
- [x] `SileroTTSYamlConfigStorage._load_config_model()` parses top-level `promts` array from data.yml into `dict[str, Promt]` (key = id)
- [x] `SileroTTSYamlConfigStorage._load_config_model()` parses `voices.{locale}.{model}.{voice_name}.normalization` into `dict[str, VoiceNormalization]` (key = `"{voice_id}__{text_format_value}"`)
- [x] Voice ID constructed as `"{locale}-{model_name}-{voice_name}"` from YAML nesting
- [x] `get_promt(promt_id)` returns `Promt | None` via dict lookup
- [x] `get_voice_normalization(voice_id, text_format)` returns `VoiceNormalization | None` via dict lookup
- [x] Existing tests still pass

## Blocked by

- Slice 1: Promt + VoiceNormalization entities must exist in models.py
