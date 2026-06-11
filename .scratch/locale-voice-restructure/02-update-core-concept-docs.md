---
title: "Update Locale and Voice core concepts in CONTEXT.md"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Update `CONTEXT.md` to reflect the new Locale and Voice data model after the dataclass/storage restructure.

**Locale core concept (currently lines 41–61):**
- Add `name` field description (the locale key string, e.g. `ru_RU`)
- Remove `voices` field from the Locale entry description
- Keep YAML example unchanged (the `name` is the YAML key, voices are now described separately)

**Voice core concept (currently lines 63–92):**
- Add `locale` field description (references the `Locale.name` this voice belongs to)
- Remove language that implies voices are nested "under `locales.*.voices`" — describe voices as a flat list, each referencing a locale
- Keep the YAML example in the Voice section but note that `locale` is injected from the parent key

**`/locales` Endpoint section (currently lines 151–153):**
- Update to reflect `get_locales() -> list[Locale]` (behavior unchanged, output format same)

**`/voices` Endpoint section (currently lines 155–159):**
- Update to reflect `get_voices()` now returns a flat `list[VoiceConfig]` (behavior unchanged, output format same)

## Acceptance criteria

- [x] Locale concept documents `name` field and does not mention `voices`
- [x] Voice concept documents `locale` field and describes the flat-list model
- [x] `/locales` and `/voices` endpoint sections reference the current API signatures
- [x] YAML examples in Voice section remain accurate

## Blocked by

- /workspaces/python/.scratch/locale-voice-restructure/01-dataclass-storage-endpoints.md
