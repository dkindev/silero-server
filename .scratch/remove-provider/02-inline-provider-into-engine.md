---
title: "Remove SileroTTSModelProvider, inline into engine"
labels:
  - ready-for-agent
created: 2026-06-02
---

## Parent

[01-add-models-dir-config](./01-add-models-dir-config.md)

## What to build

Delete `SileroTTSModelProvider` and inline its model-resolution logic into `SileroTTSEngine` as a private `_resolve_model()` method. The provider's `get_model()` body (download `models.yml`, parse YAML, download `.pt`, return path + sample rates) becomes the body of `_resolve_model`. The nested `_sync_load()` in `_load_model_async()` calls `self._resolve_model()` instead of `self._provider.get_model()`.

Remove the `provider` parameter from `SileroTTSEngine.__init__`, remove `self._provider`, and store `self._models_dir` from `config.models_dir` instead.

Delete `src/tts/provider.py` and `tests/test_provider.py`.

Update all test constructions of `SileroTTSEngine` to remove the `provider=` argument. Replace mock patches targeting `SileroTTSModelProvider` with patches on `urllib.request.urlretrieve`, `torch.hub.download_url_to_file`, and `torch.package.PackageImporter`. Cache-verification tests assert behavior through `process()` results rather than provider call counts.

## Acceptance criteria

- [x] No references to `SileroTTSModelProvider` remain in source or tests
- [x] `src/tts/provider.py` is deleted
- [x] `tests/test_provider.py` is deleted
- [x] `_resolve_model(language, model_name)` on the engine contains the YAML download/parse + `.pt` download logic
- [x] `_sync_load()` calls `self._resolve_model()` instead of `self._provider.get_model()`
- [x] Engine constructor takes only `(config, storage)` — no `provider` param
- [x] Tests pass with lower-level mocks, no provider mocks
- [x] Cache behavior is verified through `process()` output

## Blocked by

- [01-add-models-dir-config](./01-add-models-dir-config.md)
