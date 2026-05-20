---
title: "Engine model loading integration tests"
labels:
  - ready-for-agent
created: 2026-05-20
---

## Parent

[02-factory-and-engine-wiring](./02-factory-and-engine-wiring.md)

## What to build

Integration tests for `SileroTTSEngine._load_model()` covering model loading via `torch.package.PackageImporter` and corrupt file cleanup.

### Cases to cover

1. **Model loads via `torch.package.PackageImporter`**: verify that a real local `.pt` file (can be a real small model or a minimal Torch package) can be loaded, `apply_tts()` is called, and `TTSResult` is returned with correct sample rate.
2. **Corrupt `.pt` file cleanup**: write a corrupt/truncated `.pt` file to the expected path. Call `_load_model()` directly. Verify the file is deleted and `TTSProcessingError` (or the underlying exception) is raised.

### Note on test dependencies

For case 1, either use a real small Silero model file (fixture) or mock `torch.package.PackageImporter` to return a mock model with `apply_tts()` and `to()` methods. A real model file is preferable if it can be kept small.

## Acceptance criteria

- [x] Real local `.pt` file loads via `PackageImporter`, `apply_tts()` is called, returns valid `TTSResult`
- [x] Corrupt local `.pt` is deleted before the exception propagates
- [x] Tests use temp directories for isolation

## Blocked by

- [02-factory-and-engine-wiring](./02-factory-and-engine-wiring.md)