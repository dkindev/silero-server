---
title: "Wyoming server & HTTP removal"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Replace the HTTP FastAPI server with a Wyoming-protocol-only TCP server, following the patterns from [wyoming-piper](https://github.com/rhasspy/wyoming-piper). Create a proper Wyoming event handler, rewrite `main.py`, and strip all HTTP API artifacts.

### New `handler.py`

Create `src/handler.py` with `SileroWyomingHandler(AsyncEventHandler)`:

- Accept `wyoming_info: Info` and engine reference at init; cache `wyoming_info_event`
- `Describe.is_type(event.type)`: send cached info event, `return True` (keep connection alive)
- `Synthesize.is_type(event.type)`: extract `voice_id` from `synthesize.voice.name`, iterate `engine.synthesize_pcm_chunks(text, voice_id, "TEXT")`, send `AudioStart(rate, width=BYTES_PER_SAMPLE, channels=CHANNELS)` → `AudioChunk` stream → `AudioStop`, `return True`
- Streaming support: `SynthesizeStart`/`SynthesizeChunk`/`SynthesizeStop` for accumulating text chunks and processing on stop
- Catch exceptions, send `Error` event, re-raise
- Return `True` from all handlers (keep connection alive for multiple events)

### Rewrite `main.py`

- Remove all FastAPI imports and setup
- Move engine creation inline in `main()` (settings → config → storage → engine)
- Add `argparse` CLI with `--uri` (default `tcp://0.0.0.0:10200`)
- Build `Info` dynamically from storage:
  ```python
  for voice in storage.get_voices():
      locale = storage.get_locale(voice.locale)
      TtsVoice(name=voice.id, languages=[locale.language])
  ```
- Wrap `TtsVoice` objects in `TtsProgram` → `Info`
- Signal handlers (`SIGINT`, `SIGTERM`) for clean shutdown via `asyncio.CancelledError`
- `run()` entry point with `asyncio.run(main())`

### Delete HTTP API files

- `src/deps.py` — delete entirely (engine creation folds into main)
- `src/handlers.py` — delete entirely (FastAPI middleware only)
- `docs/adr/0001-mary-tts-compatibility.md` — delete

### Settings cleanup

- `src/config.py`: Remove `TTS_MAX_TEXT_LENGTH`, `TTS_ALLOWED_ORIGINS`. Keep `TTS_ENV_TYPE`.
- `TTS_CONFIG_PATH` default: `"silero-to-mary-config.yml"` → `"config.yml"` (from Slice 1)

### Infrastructure files

- `docker-entrypoint.sh`: no changes needed (entrypoint is agnostic)
- `Dockerfile`: `EXPOSE 8000` → `EXPOSE 10200`, replace healthcheck with TCP connect, `CMD` → `python -m src.main`
- `pyproject.toml`: Remove `fastapi`, `uvicorn[standard]`, `gunicorn`, `python-multipart` from dependencies; remove `httpx` from dev deps; update description
- `.env.example`: Remove `TTS_MAX_TEXT_LENGTH`, `TTS_ALLOWED_ORIGINS`; change `TTS_CONFIG_PATH` default

### Domain docs

- `CONTEXT.md`: Remove "Mary-TTS compatible HTTP API" language; update to "Wyoming protocol TTS server"; update `Voice` and `Locale` glossary entries to reflect `id` and `language` fields

### Test cleanup

- Delete: `tests/test_routers.py`, `tests/test_health.py`, `tests/test_config.py`, `tests/test_env_example.py`
- (Update `tests/test_config_storage.py` and `tests/test_engine.py` were already done in Slices 1 and 2)

## Acceptance criteria

- [x] `src/handler.py` exists with `SileroWyomingHandler` handling Describe, Synthesize, and stream events
- [x] `src/main.py` is a Wyoming-only TCP server with argparser, signal handlers, and `run()` entry point
- [x] `create_wyoming_info()` builds `Info` dynamically from storage, using `get_locale()` to populate `languages`
- [x] Server handles a Wyoming Describe → Synthesize → AudioStart/AudioChunk/AudioStop roundtrip
- [x] `src/deps.py` and `src/handlers.py` are deleted
- [x] `docs/adr/0001-mary-tts-compatibility.md` is deleted
- [x] Settings: `TTS_MAX_TEXT_LENGTH` and `TTS_ALLOWED_ORIGINS` removed; `TTS_ENV_TYPE` kept
- [x] Dockerfile: EXPOSE 10200, healthcheck updated, CMD changed
- [x] `pyproject.toml`: HTTP server dependencies removed
- [x] `.env.example`: stale settings removed
- [x] HTTP test files deleted
- [x] `CONTEXT.md` updated

## Blocked by

- /workspaces/python/.scratch/wyoming-refactor/02-engine-refactor.md
