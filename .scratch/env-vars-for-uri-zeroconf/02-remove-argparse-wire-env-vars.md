---
title: "Remove argparse, wire TTS_URI and TTS_ZEROCONF from Settings"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Remove `argparse` from `main.py`. Read `TTS_URI` and `TTS_ZEROCONF` from `get_settings()` instead. Keep the zeroconf+tcp validation (`Zeroconf requires tcp:// uri`). Delete the `import argparse` line and the parser block.

## Acceptance criteria

- [x] `argparse` import removed from `main.py`
- [x] Parser block (`argparse.ArgumentParser`, `add_argument`, `parse_args`) removed
- [x] `args.uri` → `settings.TTS_URI`, `args.zeroconf` → `settings.TTS_ZEROCONF`
- [x] `settings = get_settings()` called at top of `main()`
- [x] Zeroconf+tcp validation preserved
- [x] Server starts correctly with env vars only, no CLI flags
- [x] `python -m src.main` works without any arguments (uses defaults)

## Blocked by

- `/workspaces/python/.scratch/env-vars-for-uri-zeroconf/01-add-uri-zeroconf-to-settings.md`
