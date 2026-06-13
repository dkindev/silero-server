---
title: "Rename get_model_info() to get_model()"
labels:
  - ready-for-agent
created: 2026-06-13
---

## What to build

Rename the storage method `get_model_info()` to `get_model()` throughout the codebase. The implementation stays identical — this is purely a naming change to reflect that the method returns a `Model` object directly, not "info" about it. Rename all call sites, the local variable `model_info` in `_warmup_model()`, and the parameter `model_info` in `_load_model_async()`. Update test class, method names, call sites, and docstrings that explicitly reference the old name.

## Acceptance criteria

- [x] ABC method `SileroTTSConfigStorage.get_model()` defined
- [x] `SileroTTSYamlConfigStorage.get_model()` implemented with existing logic
- [x] Engine call site updated: `self._storage.get_model(name)`
- [x] Local variable `model_info` → `model` in `_warmup_model()`
- [x] Parameter `model_info` → `model` in `_load_model_async()`
- [x] Test class `TestGetModelInfo` → `TestGetModel`
- [x] Test methods and call sites updated
- [x] Test docstrings updated
- [x] `pytest` passes

## Blocked by

None — can start immediately.
