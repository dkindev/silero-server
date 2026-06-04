---
title: "01: Rename source module silero_tts_engine.py -> engine.py"
labels:
  - ready-for-agent
created: 2026-06-04
---

## Parent

Conversation with agent on 2026-06-04: rename silero_tts_engine.py to engine.py for readability.

## What to build

Rename `src/tts/silero_tts_engine.py` to `src/tts/engine.py`. Update all imports and mock patch target strings across the codebase to reference the new module path. Update the file path reference in `CONTEXT.md`. The class `SileroTTSEngine` inside the module stays unchanged.

## Acceptance criteria

- [x] `src/tts/silero_tts_engine.py` is renamed to `src/tts/engine.py`
- [x] Import in `src/deps.py` updated: `from src.tts.engine import SileroTTSEngine`
- [x] All imports in `tests/test_silero_tts_engine.py` updated to use `src.tts.engine`
- [x] Mock patch target strings in tests updated (e.g., `"src.tts.engine.torch.package.PackageImporter"`)
- [x] Path reference in `CONTEXT.md` updated to `src/tts/engine.py`
- [x] App starts without import errors
- [x] All tests pass

## Blocked by

None - can start immediately
