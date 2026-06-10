---
title: "Change get_voices() to return dict[str, list[VoiceConfig]] with dedup and update /voices endpoint"
labels:
  - ready-for-agent
created: 2026-06-10
---
## What to build

Change `SileroTTSConfigStorage.get_voices()` to return `dict[str, list[VoiceConfig]]`
keyed by locale. Within each locale's list, deduplicate by `voice_name` (keep only the first occurrence).

Update `_build_voices()` accordingly. Update the `/voices` FastAPI endpoint to iterate
the dict and format each entry as `{voice_name} {locale} {gender}`, one per line.

Update the `/voices` endpoint and `engine.get_storage().get_voices()` references in `CONTEXT.md`.

## Acceptance criteria

- [ ] `SileroTTSConfigStorage.get_voices()` returns `dict[str, list[VoiceConfig]]`
- [ ] Duplicate `voice_name` entries within the same locale are deduplicated (first kept)
- [ ] Voices referencing disabled models are excluded
- [ ] `GET /voices` returns correctly formatted Mary-TTS lines, one per voice
- [ ] All storage, router, and engine tests pass with the new return type

## Blocked by

- [Slice 1: Add voice_name to VoiceConfig](/workspaces/python/.scratch/voice-core-concept/01-add-voice_name-to-voiceconfig.md)
