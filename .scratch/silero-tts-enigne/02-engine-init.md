---
title: "02: Engine init + get_locales() + get_voices()"
labels:
  - ready-for-agent
created: 2026-05-14
---

## Parent

`.scratch/silero-tts-enigne/silero-tts-engine.md`

## What to build

Implement SileroTTSEngine class init, get_locales() returning tuple, get_voices() returning Mary-TTS formatted tuple.

## Acceptance criteria

- [x] SileroTTSEngine.__init__() accepts TTSConfig and TTSConfigModel
- [x] get_locales() returns tuple of locale strings from config
- [x] get_voices() returns tuple of "{voice} {locale} {gender}" strings
- [x] Locales and voices are cached at init time

## Blocked by

- `.scratch/silero-tts-enigne/01-config-exceptions.md`