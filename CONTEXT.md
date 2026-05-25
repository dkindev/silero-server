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
- **Output format**: The Silero TTS model always returns a two-dimensional (2D) tensor with batch dimension: [1, samples] (where 1 is one generated text and samples is the number of audio points).

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

Voice validation at request time (endpoint level):
1. Check locale exists via `has_locale()`
2. Check voice exists via `has_voice(locale, voice_name)`

Gender is sourced from config.

### SileroTTSEngine

Low-level TTS engine wrapping Silero. Lives in `src/tts/silero_tts_engine.py`.

**Methods:**
- `has_locale(locale)` → `bool` — returns True if locale is configured
- `has_voice(locale, voice_name)` → `bool` — returns True if voice exists for the locale
- `get_input_types()` → `tuple[str, ...]` — returns supported input types (`"TEXT"`, `"SSML"`)
- `get_locales()` → `list[str]` — returns cached list from config (e.g., `["ru_RU", "de_DE"]`)
- `get_voices()` → `list[str]` — returns cached list in Mary-TTS format: `"{voice_name} {locale} {gender}"` per voice (e.g., `["silero-v5_5_ru-aidar ru_RU male", "silero-v5_5_ru-baya ru_RU female"]`)
- `process(text, locale, voice, input_type)` → `TTSResult` — returns synthesized audio as `TTSResult(audio=io.BytesIO, sample_rate=int, model=str)`

**Initialization:**
- Config loaded from `TTS_CONFIG_PATH` at init, cached for app lifetime
- Settings read: `TTS_DEVICE`, `TTS_SAMPLE_RATE`, `TTS_MAX_CONCURRENT_PER_MODEL`

Sample rate selection logic:
1. Get voice model (after receiving a voice from the config)
2. Get model's supported sample_rates from config
3. Sample rate selection logic (sort and deduplicate):
   a. Empty list → use TTS_SAMPLE_RATE
   b. None → use TTS_SAMPLE_RATE
   c. Single element → use that element
   d. TTS_SAMPLE_RATE > max → use max
   e. TTS_SAMPLE_RATE < min → use min
   f. Exact match → use that value
   g. Not in list → use highest value less than TTS_SAMPLE_RATE

**Validation rules:**
Validation happens at two levels:

1. **Endpoint (first line)** — `/process` endpoint validates before calling the engine:
   - `AUDIO` must be `WAVE_FILE` → 400
   - Locale must exist via `has_locale()` → 400
   - Voice must exist via `has_voice()` → 400
   - `INPUT_TYPE` must be in `get_input_types()` → 400
   - `OUTPUT_TYPE` must be `AUDIO` → 406

2. **Engine (second line)** — `process()` redundantly validates locale, voice, and input type as a safety net. A second-line failure raises `TTSEngineError` → 500 (indicates a bug: the endpoint should have caught it).

**Model Cache:**
- Models are lazy-loaded on first use and cached.
- `TTS_MAX_MODELS` caps the cache size. When a new model is loaded at capacity, the least-recently-used model is evicted and its torch resources freed.
- Eviction calls `gc.collect()` and clears the torch CUDA/XPU cache.

**Concurrency:**
- Per-model `asyncio.Semaphore` with configurable limit via `TTS_MAX_CONCURRENT_PER_MODEL`
- Models lazy-loaded on first `process()` call per language and speaker, cached thereafter

**Normalization:** 
- Clips/clamps Silero audio from \(-1.0\) to \(1.0\) float32 range.
- Scales and converts the audio to 16-bit PCM integer format (int16). This creates a smaller file size and matches standard audio streaming expectations.

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
- `INPUT_TYPE` — input format: `TEXT` (default), `SSML`, `RAWMARYXML` (rejected with 400).
- `OUTPUT_TYPE` — output format: `AUDIO` (default), `PHONEMES`/`TOKENS` (rejected with 406).
- `AUDIO` — audio file format: `WAVE_FILE` (default). Other formats rejected with 400.

**Validation rules:**
- Text length ≤ `TTS_MAX_TEXT_LENGTH` (default 1000 chars, 400 if exceeded) — checked in endpoint
- `AUDIO`, locale, voice, `INPUT_TYPE`, `OUTPUT_TYPE` — all validated by the endpoint before the engine is called

**Response:** WAV audio streamed from a `BytesIO` buffer via `StreamingResponse`. `Content-Type: audio/wav`, `Content-Disposition: inline`.

### Configuration

All configuration via environment variables with `TTS_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `TTS_DEVICE` | `cpu` | `cpu`, `cuda`, or `xpu`. Falls back to `cpu` at runtime if requested device is unavailable. |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz). Supported: 8000, 16000, 22050, 24000, 48000 |
| `TTS_MAX_TEXT_LENGTH` | `1000` | Max input characters |
| `TTS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `TTS_SHUTDOWN_TIMEOUT` | `10` | Graceful shutdown timeout (seconds) |
| `TTS_CONFIG_PATH` | `silero-to-mary-config.yml` | Path to voice/locale mapping config |
| `TTS_MAX_MODELS` | `2` | Max models cached in memory. Oldest evicted when limit reached (ge=1). |
| `TTS_MAX_CONCURRENT_PER_MODEL` | `2` | Max concurrent requests per model |

Validated at startup via Pydantic Settings — app exits with a clear error on invalid values.

### Error Responses

All errors return JSON `{"detail": "..."}`. HTTP status codes:
- `400 Bad Request` — unsupported locale/voice/audio format, text too long, invalid input type.
- `406 Not Acceptable` — unsupported output type (PHONEMES, TOKENS).
- `500 Internal Server Error` — engine failure (model loading, synthesis error, or second-line validation miss). Body is generic; detail is logged server-side.

### Health Check

`GET /api/v1/health` returns extended status:
- `status`: always `"ok"`

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