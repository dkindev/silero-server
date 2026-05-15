# Silero TTS Server — Domain Context

## Project Overview

A simple, robust, and performant **Mary-TTS compatible REST API** that wraps the Silero TTS engine. Provides text-to-speech generation over HTTP with minimal latency and operational overhead.

Target users: any client (web, mobile, desktop, embedded) that needs TTS via a well-defined API.

## Core Concepts

### TTS Engine

The underlying engine is **Silero TTS** (`silero` Python package). Silero provides neural TTS models per language with multiple speaker voices per model.

Key Silero concepts:
- **Model**: A `.pt` file downloaded per language (e.g., `v5_5_ru.pt`). Downloaded via Torch Hub to `~/.cache/torch/hub/`. Each model has a `language` field used by `torch.hub.load()`.
- **Speaker**: A named voice within a model (e.g., `aidar`, `baya`, `eugene`, `kseniya`, `xenia` for Russian). Speakers are model-specific.
- **Sample rate**: Audio output frequency in Hz. Silero produces 48000 Hz by default; torchaudio can resample.

### Locale

The API exposes **Mary-TTS locale format** (`ru_RU`, `de_DE`) on the public API surface. Locales are derived from `SileroTTSEngine.get_locales()`.

A locale is **supported** if it appears in `SileroTTSEngine.get_locales()`. A request for an unsupported locale returns **400 Bad Request**.

### Voice

Voices are named in `silero-{model_name}-{speaker}` format, e.g.:
- `silero-v5_5_ru-aidar`
- `silero-v5_5_ru-baya`
- `silero-v5_5_ru-eugene`
- `silero-v5_5_ru-kseniya`
- `silero-v5_5_ru-xenia`

This naming scheme:
- Prefixes all voices with `silero-` to avoid collision with other TTS systems.
- Embeds the model name (e.g., `v5_5_ru`) to disambiguate speakers that may not exist in other model versions.
- Speaker names are Silero's native speaker identifiers.

Voice validation at request time:
1. Look up locale in config → get voices → get model
2. Verify requested locale matches config locale
3. Verify requested voice is contained in locale
4. Get model's supported sample_rates from config
5. Sample rate selection logic (already sorted and deduplicated):
   a. Empty list → use TTS_SAMPLE_RATE
   b. None → use TTS_SAMPLE_RATE
   c. Single element → use that element
   d. TTS_SAMPLE_RATE > max → use max
   e. TTS_SAMPLE_RATE < min → use min
   f. Exact match → use that value
   g. Not in list → use highest value less than TTS_SAMPLE_RATE

Gender is sourced from config.

### SileroTTSEngine

Low-level TTS engine wrapping Silero. Lives in `src/tts/silero_tts_engine.py`.

**Methods:**
- `get_locales()` → `list[str]` — returns cached list from config (e.g., `["ru_RU", "de_DE"]`)
- `get_voices()` → `list[str]` — returns cached list in Mary-TTS format: `"{voice_name} {locale} {gender}"` per voice (e.g., `["silero-v5_5_ru-aidar ru_RU male", "silero-v5_5_ru-baya ru_RU female"]`)
- `process(text, locale, voice, input_type, output_type)` → `bytes` — returns raw WAV audio

**Initialization:**
- Config loaded from `TTS_CONFIG_PATH` at init, cached for app lifetime
- Settings read: `TTS_DEVICE`, `TTS_SAMPLE_RATE`, `TTS_MAX_CONCURRENT_PER_LOCALE`

**Validation rules (in engine):**
- Locale must exist in config → 400 if not
- Voice must exist for locale → 400 if not
- `INPUT_TYPE` must be TEXT or SSML → 400 if not
- `OUTPUT_TYPE` must be AUDIO → 400 for invalid, 406 for non-AUDIO

**Concurrency:**
- Per-locale `asyncio.Semaphore` with configurable limit via `TTS_MAX_CONCURRENT_PER_LOCALE`
- Models lazy-loaded on first `process()` call per language and speaker, cached thereafter

### `/locales` Endpoint

Returns available locales from `SileroTTSEngine.get_locales()` as plain text, one per line.

### `/voices` Endpoint

Returns available voices from `SileroTTSEngine.get_voices()` as plain text, one per line.

### `/process` Endpoint

Converts text to speech audio. Uses `SileroTTSEngine.process()` for synthesis. Supports GET and POST.

**Parameters:**
- `INPUT_TEXT` — text to synthesize (required).
- `LOCALE` — Mary-TTS locale (e.g., `ru_RU`). Must have a cached model.
- `VOICE` — voice name (e.g., `silero-v5_5_ru-aidar`). Must exist for the locale.
- `INPUT_TYPE` — input format: `TEXT` (default), `SSML`, `RAWMARYXML` (rejected).
- `OUTPUT_TYPE` — output format: `AUDIO` (default, WAV), `PHONEMES`/`TOKENS` (rejected with 406).

**Validation rules:**
- Text length ≤ `TTS_MAX_TEXT_LENGTH` (default 1000 chars, 400 if exceeded) — checked in endpoint
- Engine handles: locale existence, voice existence, `INPUT_TYPE`, `OUTPUT_TYPE`

**Response:** Raw WAV audio bytes. `Content-Type: audio/wav`, `Content-Disposition: inline`.

### Configuration

All configuration via environment variables with `TTS_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `TTS_DEVICE` | `cpu` | `cpu` or `cuda` |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz). Supported: 8000, 16000, 22050, 24000, 48000 |
| `TTS_MAX_TEXT_LENGTH` | `1000` | Max input characters |
| `TTS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `TTS_SHUTDOWN_TIMEOUT` | `10` | Graceful shutdown timeout (seconds) |
| `TTS_CONFIG_PATH` | `silero-to-mary-config.yml` | Path to voice/locale mapping config |
| `TTS_MAX_CONCURRENT_PER_LOCALE` | `2` | Max concurrent requests per locale |

Validated at startup via Pydantic Settings — app exits with a clear error on invalid values.

### Error Responses

All errors return JSON `{"detail": "..."}`. HTTP status codes:
- `400 Bad Request` — unsupported locale/voice, text too long, locale/text mismatch, invalid input type.
- `406 Not Acceptable` — unsupported output type (PHONEMES, TOKENS).
- `500 Internal Server Error` — model failure, audio generation error. Body is generic; detail is logged server-side.

### Health Check

`GET /api/v1/health` returns extended status:
- `status`: always `"ok"`
- `device`: `"cpu"` or `"cuda"`
- `sample_rate`: configured output sample rate

### Docker Strategy

- **Default image**: CPU-only, `python:3.14-slim`.
- **CUDA image**: `Dockerfile.cuda` variant.
- **Models**: Pre-downloaded at build time (no cold-start latency in production).

## Key Conventions

- **API versioning**: All routes under `/api/v1/`.
- **Response format**: Raw bytes for audio; JSON for errors and health.
- **No rate limiting** at the application layer — delegate to infrastructure.
- **No API key auth** at the application layer — delegate to infrastructure.
- **Graceful shutdown**: Drain in-flight requests up to `TTS_SHUTDOWN_TIMEOUT` before exit.