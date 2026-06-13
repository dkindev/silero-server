---
title: "Rename has_locale() to has_locale_in_voices()"
labels:
  - ready-for-agent
created: 2026-06-13
---

## What to build

Rename the storage method `has_locale()` to `has_locale_in_voices()` throughout the codebase. The implementation stays identical — this is purely a naming change for consistency with `get_locales_in_voices()`.

## Acceptance criteria

- [x] Abstract method `SileroTTSConfigStorage.has_locale_in_voices()` defined
- [x] `SileroTTSYamlConfigStorage.has_locale_in_voices()` implemented with existing logic
- [x] Engine caller updated
- [x] Process router caller updated
- [x] All test call sites and test method names updated
- [x] Test docstrings updated
- [x] `pytest` passes

## Blocked by

None — can start immediately.
