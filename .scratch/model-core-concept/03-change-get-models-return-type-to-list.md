---
title: "Change get_models() return type from dict[str, Model] to list[Model]"
labels:
  - ready-for-agent
created: 2026-06-15
---

## What to build

Change `SileroTTSConfigStorage.get_models()` to return `list[Model]` instead of `dict[str, Model]` for consistency with the other collection-returning methods (`get_voices()`, `get_locales_in_voices()`).

The `get_model(name)` method already exists for name-based lookup and continues to work unchanged.

## Acceptance criteria

- [ ] Abstract method signature updated: `get_models(self) -> list[Model]`
- [ ] `SileroTTSYamlConfigStorage.get_models()` returns `list(self._models.values())`
- [ ] `SileroTTSEngine.warmup()` updated to iterate the list directly (drop `.items()`)
- [ ] All tests updated to use list semantics or `storage.get_model()` instead of dict key access
- [ ] All existing tests pass

## Blocked by

None - can start immediately
