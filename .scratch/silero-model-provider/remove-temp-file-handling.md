---
title: "Remove temp file handling in SileroTTSModelProvider"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Remove unnecessary temp file handling in `src/tts/provider.py`. The `torch.hub.download_url_to_file` function already handles atomic downloads, so our explicit `.tmp` file approach is redundant.

## Changes required

- `src/tts/provider.py`:
  - Remove `tmp_path` variable
  - Change `torch.hub.download_url_to_file(package_url, tmp_path)` to download directly to `model_path`
  - Remove `os.rename(tmp_path, model_path)` 
  - Update except block to clean up `model_path` instead of `tmp_path`

## Acceptance criteria

- [ ] Downloads directly to `model_path` instead of via temp file
- [ ] Failed downloads still clean up partial file before raising `TTSProcessingError`
- [ ] Engine's existing load-failure cleanup unchanged
- [ ] Existing tests pass

## Blocked by

None - can start immediately