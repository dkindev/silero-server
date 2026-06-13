---
title: "Rename VoiceConfig dataclass to Voice across entire codebase"
labels:
  - ready-for-agent
created: 2026-06-13
---

## What to build

Rename the `VoiceConfig` frozen dataclass to `Voice` and its `voice_name` field to `name` across all source, test, and configuration files. Pure mechanical rename — no behavioral change, no API contract changes.

### Files affected

- **`src/tts/models.py`** — class + field rename; update `TTSConfigModel.voices` type
- **`src/tts/config_storage.py`** — `get_voice_config()` → `get_voice()`; params `locale` → `locale_name`; YAML var `v` → `voice_data`; all `vc` → `voice`
- **`src/tts/engine.py`** — param `voice: str` → `voice_name: str`; `get_voice_config` → `get_voice`; `voice_config` → `voice`
- **`src/routers/voices.py`** — `vc` → `voice`; `vc.voice_name` → `voice.name`
- **Test files** — imports, class names, instantiations, variables

### Not changed

README.md, CONTEXT.md, .scratch/, docs/adr/, silero-to-mary-config.yml

## Acceptance criteria

- [x] `VoiceConfig` removed; replaced by `Voice` with field `name`
- [x] `get_voice_config()` → `get_voice()` on storage classes
- [x] `locale` → `locale_name` in storage method params
- [x] Engine param `voice` → `voice_name`
- [x] `ruff check src/ tests/` passes
- [x] `pytest tests/` passes

## Blocked by

None — can start immediately
