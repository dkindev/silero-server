---
title: "Stage 1: Silero Wrapper Module"
labels:
  - ready-for-agent
created: 2026-05-12
---

## Parent

docs/stages/1.md

## What to build

Create `src/silero.py` — core deep module abstracting Silero model lifecycle.

Interface:
- `get_available_locales() -> list[str]` — read cached `.pt` model filenames from Torch Hub directory, map short codes (ru) to Mary-TTS format (ru_RU), deduplicate.
- `get_available_voices() -> list[Voice]` — load cached models, read model.speakers, return Voice(locale, speaker, gender, full_name).
- `synthesize(text, locale, voice, sample_rate) -> tuple[torch.Tensor, int]` — resolve Mary-TTS voice to Silero model + speaker, load model, apply speaker, return audio tensor + sample rate.
- `get_internal_language(locale: str) -> str` — strip _... suffix: ru_RU → ru.
- Speaker gender mapping: hardcoded dict for known Silero speakers, default unknown.

Error on locale/voice mismatch raises domain-specific exception (caught by router layer → 400).

## Acceptance criteria

- [ ] get_available_locales() returns list of Mary-TTS format locales (ru_RU, de_DE) from cached .pt files
- [ ] get_available_voices() returns Voice objects with locale, speaker, gender, full_name
- [ ] synthesize() returns torch.Tensor audio and int sample_rate
- [ ] get_internal_language() correctly maps ru_RU → ru, en_US → en
- [ ] Invalid locale/voice raises exception detectable by router
- [ ] Speaker gender mapping hardcoded for known speakers (aidar→male, baya→female, etc.)

## Blocked by

None - can start immediately