---
title: "Factory function + engine wiring"
labels:
  - ready-for-agent
created: 2026-05-20
---

## Parent

[01-silero-tts-model-provider](./01-silero-tts-model-provider.md)

## What to build

Wire `SileroTTSModelProvider` into `SileroTTSEngine` via a factory function, replacing `torch.hub.load()` with `torch.package.PackageImporter`.

### Factory function

Add `create_silero_engine(config, config_model)` to `src/tts/silero_tts_engine.py` (next to the `SileroTTSEngine` class):

```python
def create_silero_engine(config: TTSConfig, config_model: TTSConfigModel) -> SileroTTSEngine:
    provider = SileroTTSModelProvider()
    return SileroTTSEngine(config=config, config_model=config_model, provider=provider)
```

### Engine constructor change

`SileroTTSEngine.__init__` gains a `provider: SileroTTSModelProvider` parameter. Store as `self._provider`.

### Refactor `_load_model()`

Replace `torch.hub.load("snakers4/silero-models", "silero_tts", ...)` with:

```python
local_path = self._provider.get_model_path(model_info.language, model_name)
importer = torch.package.PackageImporter(local_path)
model = importer.load_pickle("tts_models", "model")
model.to(self._device)
```

### Corrupt file cleanup

If `torch.package.PackageImporter` fails to load a local `.pt` file (corrupt/truncated), delete the file before re-raising so the next request can re-download cleanly.

## Acceptance criteria

- [x] `create_silero_engine()` instantiates provider and engine with correct dependency
- [x] Engine's `_load_model()` uses `torch.package.PackageImporter` to load local `.pt` files
- [x] Engine calls `model.apply_tts()` — interface unchanged from current
- [x] Corrupt local `.pt` file is deleted before re-raising the error
- [x] `main.py` (or wherever the engine is created) uses `create_silero_engine()` instead of direct constructor

## Blocked by

- [01-silero-tts-model-provider](./01-silero-tts-model-provider.md)