---
title: "Add Model.name field"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Add a `name: str` field as the first field on the `Model` dataclass. The name is the YAML config key for the model entry (e.g. `v5_5_ru`, `v3_en`). This makes the model name a self-contained attribute on the object rather than relying on an external dict key.

Update every `Model(...)` construction in the codebase — all tests and any source code — to include `name=`. The `TTSConfigModel.models` field stays as `dict[str, Model]` for now; the dict keys match the new `name` values, so the storage layer continues to work unchanged.

## Acceptance criteria

- [x] `Model` dataclass has `name: str` as its first field
- [x] All `Model(...)` constructions in `src/` and `tests/` include `name=`
- [x] All existing tests pass without modification to storage or engine logic

## Blocked by

None - can start immediately
