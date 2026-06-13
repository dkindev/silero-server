---
title: "Rename get_locales() to get_locales_in_voices()"
labels:
  - ready-for-agent
created: 2026-06-13
---

## What to build

Rename the storage method `get_locales()` to `get_locales_in_voices()` throughout the codebase. The implementation stays identical — this is purely a naming change to reflect that the method returns only locales backed by enabled voices. The FastAPI handler function in the `/locales` endpoint retains its current name.

## Acceptance criteria

- [x] Abstract method `SileroTTSConfigStorage.get_locales_in_voices()` defined
- [x] `SileroTTSYamlConfigStorage.get_locales_in_voices()` implemented with existing logic
- [x] Router caller updated to call `engine.get_storage().get_locales_in_voices()`
- [x] All test call sites, test class names, and test method names updated
- [x] Test docstrings updated
- [x] `pytest` passes

## Blocked by

None — can start immediately.
