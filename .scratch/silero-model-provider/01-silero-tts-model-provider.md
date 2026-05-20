---
title: "SileroTTSModelProvider class"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

A `SileroTTSModelProvider` class in `src/tts/provider.py` that manages local `.pt` model files.

### Behavior of `get_model_path(language, model_name)`

1. Base path is `.models/silero/` (CWD-relative). Create the directory if missing.
2. If `.models/silero/{language}/{model_name}.pt` exists, return its full path.
3. If the file is missing:
   a. Load `models.yml` — if `.models/silero/models.yml` exists on disk, load it. Otherwise download from `https://raw.githubusercontent.com/snakers4/silero-models/refs/heads/master/models.yml` and save to `.models/silero/models.yml`.
   b. Parse the YAML. If malformed, raise `TTSProcessingError` with a hint to delete `models.yml`.
   c. Resolve URL: `tts_models → {language} → {model_name} → latest → package`. If the path is missing or has no `package` key, raise `TTSProcessingError` with language, model name, and hint to delete `models.yml`.
   d. Download the `.pt` file to a temp path (`.models/silero/{language}/{model_name}.pt.tmp`) using `torch.hub.download_url_to_file`. Wrap any `RuntimeError` in `TTSProcessingError`.
   e. Rename the temp file to the final path (atomic on POSIX).
   f. Return the final path.

### Error handling

- Network failure fetching `models.yml` → `TTSProcessingError`
- Malformed YAML on disk → `TTSProcessingError` with delete hint
- Model URL not in registry → `TTSProcessingError` with language/model name and delete hint
- Download failure → `RuntimeError` wrapped in `TTSProcessingError`
- Disk I/O errors on read/write → bubble up as-is (OS-level)

### No memory caching

`models.yml` is read from disk on every call. No in-memory cache.

### No concurrency guard

Multiple concurrent calls for the same missing model may both attempt download. Acceptable — one wins, file is written atomically.

## Acceptance criteria

- [x] `get_model_path("ru", "v5_5_ru")` returns a valid local path for a cached model
- [x] Missing `models.yml` triggers download from GitHub and save to disk
- [x] Missing `.pt` file triggers download via `torch.hub.download_url_to_file` using temp file + rename
- [x] Malformed `models.yml` raises `TTSProcessingError` with delete hint
- [x] Missing model URL in registry raises `TTSProcessingError` with language/model name
- [x] Download failure is wrapped in `TTSProcessingError`
- [x] Only `.pt` files with `package` key are supported (not `jit`-only models)

## Blocked by

None — can start immediately.