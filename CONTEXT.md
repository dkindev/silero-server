# Silero TTS Server — Domain Context

## Project Overview

A simple, robust, and performant **Mary-TTS compatible REST API** that wraps the Silero TTS engine. Provides text-to-speech generation over HTTP with minimal latency and operational overhead.

Target users: any client (web, mobile, desktop, embedded) that needs TTS via a well-defined API.

## Core Concepts

### TTS Engine

The underlying engine is **Silero TTS** (`silero` Python package). Silero provides neural TTS models per language with multiple speaker voices per model.

Key Silero concepts:
- **Model**: A `.pt` file downloaded per language (e.g., `v5_5_ru.pt`). Downloaded via Torch Hub to `~/.cache/torch/hub/`.
- **Speaker**: A named voice within a model (e.g., `aidar`, `baya`, `eugene`, `kseniya`, `xenia` for Russian). Speakers are model-specific.
- **Sample rate**: Audio output frequency in Hz. Silero produces 48000 Hz by default; torchaudio can resample.

### Locale

The API exposes **Mary-TTS locale format** (`ru_RU`, `de_DE`) on the public API surface. Internally, Silero uses short language codes (`ru`, `de`).

Mapping:
- Public API: `ru_RU`, `en_US`, `de_DE` — Mary-TTS compatible format.
- Internal Silero: `ru`, `en`, `de` — Torch Hub language codes.

A locale is **supported** when the corresponding Silero model (`.pt` file) is cached. A request for an unsupported locale returns **400 Bad Request**.

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

Speaker gender is hardcoded per known speaker name in a mapping. Unrecognized speakers default to `unknown`.

### `/locales` Endpoint

Returns available locales as plain text, one per line. Derived from loaded Silero models at startup. Returns `200 OK` with empty body if no models are loaded.

### `/voices` Endpoint

Returns available voices as Mary-TTS-style lines: `{voice} {locale} {gender}\n`.

Voices are discovered by loading cached models at startup and reading `model.speakers`. Only voices for loaded models are listed.

### `/process` Endpoint

Converts text to speech audio. Supports GET and POST.

**Parameters:**
- `INPUT_TEXT` — text to synthesize (required).
- `LOCALE` — Mary-TTS locale (e.g., `ru_RU`). Must have a cached model.
- `VOICE` — voice name (e.g., `silero-v5_5_ru-aidar`). Must exist for the locale.
- `INPUT_TYPE` — input format: `TEXT` (default), `SSML` (tags stripped), `RAWMARYXML` (rejected).
- `OUTPUT_TYPE` — output format: `AUDIO` (default, WAV), `PHONEMES`/`TOKENS` (rejected with 406).

**Validation rules:**
- Locale must be supported (400 if not).
- Voice must exist for the locale (400 if not).
- Text language must match declared locale (400 if mismatch).
- Text length ≤ `TTS_MAX_TEXT_LENGTH` (default 1000 chars, 400 if exceeded).
- `INPUT_TYPE` must be `TEXT` or `SSML` (400 for others).
- `OUTPUT_TYPE` must be `AUDIO` (406 for others).

**Response:** Raw WAV audio bytes. `Content-Type: audio/wav`, `Content-Disposition: inline`.

### Concurrency

Per-language semaphore with a default limit of **2 concurrent requests** to prevent CUDA OOM. Different languages can run in parallel. Requests for the same language are serialized beyond the limit.

### Configuration

All configuration via environment variables with `TTS_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `TTS_DEVICE` | `cpu` | `cpu` or `cuda` |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz). Supported: 8000, 16000, 22050, 24000, 48000 |
| `TTS_MAX_TEXT_LENGTH` | `1000` | Max input characters |
| `TTS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `TTS_SHUTDOWN_TIMEOUT` | `10` | Graceful shutdown timeout (seconds) |

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
- `cached_locales`: list of available locales from loaded models
- `loaded_models`: list of loaded models with their speakers

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