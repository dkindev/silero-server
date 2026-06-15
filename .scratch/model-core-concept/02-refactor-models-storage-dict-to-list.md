---
title: "Refactor models storage from dict to list"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

After `Model` carries its own `name` field, change `TTSConfigModel.models` from `dict[str, Model]` to `list[Model]`. This removes the duality of "the model name is both a dict key and absent from the Model object".

Refactor `SileroTTSYamlConfigStorage` internals to compensate for the type change:

- Add `self._models: dict[str, Model]` — a name-indexed lookup built from the filtered `list[Model]`
- Remove `self._config_model` — pass the `TTSConfigModel` as a local variable to `_build_locales_dict`
- `_load_config_model`: build `list[Model]` instead of `dict[str, Model]`, setting `Model.name` from the YAML key
- `_filter_enabled`: work with `list[Model]`, extract model names via `m.name`
- `get_model_info`: use `self._models[model_name]` instead of `self._config_model.models[model_name]`
- `get_models`: return `dict(self._models)` instead of `dict(self._config_model.models)`

Update all test call sites that construct `TTSConfigModel(models=...)` — including the `_build_config` test helper.

Update `CONTEXT.md` to document `Model.name` in the Model core concept section.

## Acceptance criteria

- [x] `TTSConfigModel.models` typed as `list[Model]`
- [x] `SileroTTSYamlConfigStorage` has `self._models: dict[str, Model]` and no `_config_model` field
- [x] `_load_config_model` builds `list[Model]`
- [x] `_filter_enabled` works with `list[Model]`
- [x] `get_model_info` and `get_models` use `self._models`
- [x] All test call sites updated for `list[Model]` construction
- [x] `CONTEXT.md` updated with `Model.name` field documentation
- [x] All existing tests pass

## Blocked by

- `.scratch/model-core-concept/01-add-model-name-field.md`
