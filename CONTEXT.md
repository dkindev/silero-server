# Silero TTS Server — Domain Context

## Project Overview

A simple, robust, and performant **Mary-TTS compatible REST API** that wraps the Silero TTS engine. Provides text-to-speech generation over HTTP with minimal latency and operational overhead.

Target users: any client (web, mobile, desktop, embedded) that needs TTS via a well-defined API.

## Core Concepts

### TTS Engine

The underlying engine is **Silero TTS**. Silero provides neural TTS models per language with multiple speaker voices per model.

Key Silero concepts:
- **Model**: A `.pt` file downloaded per language (e.g., `v5_5_ru.pt`).
- **Speaker**: A named voice within a model (e.g., `aidar`, `baya`, `eugene`, `kseniya`, `xenia` for Russian). Speakers are model-specific.
- **Sample rate**: Audio output frequency in Hz. Silero produces 48000 Hz by default.
- **Output format**: The Silero TTS model always returns a one-dimensional (1D) tensor with batch dimension: [1, samples] (where 1 is one generated text and samples is the number of audio points).

### Model

Models are defined in the YAML config file at `TTS_CONFIG_PATH` (default `silero-to-mary-config.yml`) under the `models:` key:

```yaml
models:
  v5_5_ru:
    language: ru
    warmup: true
    hash_prefix: a1b2c3d4
  v3_en:
    language: en
    enabled: false
```

Each model entry has these fields:

- **`name`** — The YAML config key for the model entry (e.g. `v5_5_ru`, `v3_en`).
- **`language`** — Internal Silero language identifier (`ru`, `en`, `de`, etc.). Used to resolve and download the correct `.pt` model from the Silero model registry. This is **not** the Mary-TTS locale (e.g. `ru_RU`); locale-to-model mapping is handled separately under the `locales:` section of the config.
- **`enabled`** — `true` (default) to make the model active; `false` to disable it and exclude its voices from the API.
- **`warmup`** — `true` to preload the model at startup; `false` (default) to lazy-load on first use.
- **`hash_prefix`** — Optional SHA-256 hash prefix for download integrity verification. When set, the downloaded model file must match this prefix; omitted or empty skips verification.

### Locale

Locales are defined in the YAML config file at `TTS_CONFIG_PATH` (default `silero-to-mary-config.yml`) under the `locales:` key:

```yaml
locales:
  ru_RU:
      ...
  en_US:
      ...
```

Each locale key follows **Mary-TTS locale format** — `{language}_{COUNTRY}` (e.g., `en_US`, `de_DE`, `ru_RU`).

Each locale entry has one field:

- **`name`** — The locale key string (e.g. `ru_RU`).

A locale is included in the supported set only when at least one of its voices references an enabled model (see Voice availability rule). Locales with no voices, or whose voices all reference disabled or undefined models, are excluded.

### Voice

Voices are defined in the YAML config file under the `locales.*.voices` key:

```yaml
locales:
  ru_RU:
    voices:
      aidar:
        model: v5_5_ru
        gender: male
      baya:
        model: v5_5_ru
        gender: female
  en_US:
    voices:
      custom_name:
        speaker: en_0 # required for custom voice name
        model: v3_en
        gender: male
```

A voice is included in the supported set only when its referenced model is enabled and the locale survives filtering (has at least one voice on an enabled model). Voices whose model is disabled, or whose locale has no remaining enabled voices, are excluded.

Each voice entry has these fields:

- **`voice_name`** — The key of the voice entry in the config (e.g. `silero-v5_5_ru-aidar`). Free format; choose a name that is meaningful for your application.
- **`speaker`** — Silero's native speaker identifier (e.g. `aidar`, `en_0`). Must match a speaker known to the model. Optional in YAML — if missing or empty, defaults to the `voice_name` value.
- **`model`** — The model name to use for this voice. References a `model` key defined in the `models:` section.
- **`gender`** — Speaker gender label (`male`, `female`, etc.).
- **`locale`** — The locale this voice belongs to (e.g. `ru_RU`). Injected from the parent YAML key during config loading; not specified in the YAML entry itself.

### SileroTTSEngine

Low-level TTS engine wrapping Silero.

**Methods:**
- `get_storage()` → `SileroTTSConfigStorage` — returns the config storage; clients use it for locale/voice queries (`has_locale`, `has_voice`, `get_locales` → `list[Locale]`, `get_voices` → `list[VoiceConfig]`)
- `get_input_types()` → `tuple[str, ...]` — returns supported input types (`"TEXT"`, `"SSML"`)
- `process(text, locale, voice, input_type)` → `TTSResult` — returns synthesized audio as `TTSResult(audio=io.BytesIO, sample_rate=int, model=str)`
- `warmup()` — async. Preloads models with `warmup: true` from config up to `max_models` capacity. Runs a dummy synthesis pass per model to warm GPU caches. Silently swallows per-model failures. No-op if cache is already populated.

**Initialization:**
- Settings read: `TTS_TORCH_DEVICE`, `TTS_SAMPLE_RATE`, `TTS_MAX_MODELS`, `TTS_MAX_CONCURRENT_PER_MODEL`, `TTS_MAX_CHUNK_CHARS`, `TTS_MODELS_DIR`, `TTS_MODELS_YML_URL`, `TTS_MODELS_YML_HASH`
- Config loaded from `SileroTTSConfigStorage`
- `warmup()` called during application lifespan startup (after engine creation, before first request)

**Validation rules:**
Validation happens at two levels:

1. **Endpoint (first line)** — `/process` endpoint validates before calling the engine:
   - `AUDIO` must be `WAVE_FILE` → 400
   - Locale must exist via `get_storage().has_locale()` → 400
   - Voice must exist via `get_storage().has_voice()` → 400
   - `INPUT_TYPE` must be in `get_input_types()` → 400
   - `OUTPUT_TYPE` must be `AUDIO` → 406

2. **Engine (second line)** — `process()` redundantly validates locale, voice, and input type as a safety net. A second-line failure raises `TTSEngineError` → 500 (indicates a bug: the endpoint should have caught it).

**Model loading logic:**
1. Downloads `models.yml` from Silero models repo, parses it to find the model URL
2. Downloads the `.pt` file to `TTS_MODELS_DIR/{language}/{model_name}.pt`
3. Returns the local path with supported sample rates, sample text, and speaker samples.

**Sample rate selection logic:**
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

**Model Cache:**
- Models are lazy-loaded on first use and cached.
- `TTS_MAX_MODELS` caps the cache size. When a new model is loaded at capacity, the least-recently-used model is evicted and its torch resources freed.
- Eviction calls `gc.collect()` and clears the torch CUDA/XPU cache.

**Concurrency:**
- Per-model `asyncio.Semaphore` with configurable limit via `TTS_MAX_CONCURRENT_PER_MODEL`
- Models lazy-loaded on first `process()` call per language and speaker, cached thereafter

**Normalization:** 
- Clips/clamps Silero audio from \(-1.0\) to \(1.0\) float32 range.
- Scales and converts the audio to 16-bit PCM integer format (int16).

### `/locales` Endpoint

Returns available locales from `SileroTTSConfigStorage.get_locales() -> list[Locale]` (accessed via `engine.get_storage()`) as plain text, one locale `name` per line.

### `/voices` Endpoint

Returns available voices from `SileroTTSConfigStorage.get_voices() -> list[VoiceConfig]` (accessed via `engine.get_storage()`) as plain text, one per line.

Each line is formatted in Mary-TTS voice format: `{voice_name} {locale} {gender}`.

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

### Text Preprocessing

Text input is normalized and split into chunks before synthesis to stay within model length limits and reduce per-chunk latency.

**`TextPreprocessor`** is the base class with two public methods:
- `process_text(text, max_chunk_chars, available_chars)` — normalized and splits plain text into chunks
- `process_ssml(text, max_chunk_chars, available_chars)` — normalized and splits SSML text, preserving XML tag structure across chunks

Chunking strategy (4 levels, each used when the previous cannot split further):
1. **Sentence boundary** — split on `[.!?\n]`
2. **Minor punctuation** — split on `[,:\-—;]`
3. **Word boundary** — split on spaces
4. **Hard character limit** — split at exactly `max_chunk_chars`

**Locale-specific preprocessors** extend the base class (e.g., `RuTextPreprocessor` uses `razdel.sentenize` for Russian sentence boundaries). The engine resolves preprocessors via a factory callable `Callable[[str], TextPreprocessor]` keyed by locale. If no locale-specific preprocessor is registered, the base `TextPreprocessor` is used as fallback.

### Configuration

All configuration via environment variables with `TTS_` prefix:

| Variable | Default | Purpose |
|---|---|---|
| `TTS_TORCH_DEVICE` | `cpu` | `cpu`, `cuda`, or `xpu`. Falls back to `cpu` at runtime if requested device is unavailable. |
| `TTS_TORCH_NUM_THREADS` | `4` | PyTorch intra-op thread count (`torch.set_num_threads`). Must be ≥ 1. |
| `TTS_TORCH_NUM_INTEROP_THREADS` | `1` | PyTorch inter-op thread count (`torch.set_num_interop_threads`). Must be ≥ 1. |
| `TTS_TORCH_FLUSH_DENORMAL` | `true` | Flush denormal floats for performance (`torch.set_flush_denormal`). Only called when `hasattr` passes. |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz). Supported: 8000, 16000, 22050, 24000, 48000 |
| `TTS_MAX_TEXT_LENGTH` | `1000` | Max input characters |
| `TTS_ALLOWED_ORIGINS` | `*` | CORS allowed origins |
| `TTS_CONFIG_PATH` | `silero-to-mary-config.yml` | Path to voice/locale mapping config |
| `TTS_MAX_MODELS` | `2` | Max models cached in memory. Oldest evicted when limit reached. |
| `TTS_MAX_CONCURRENT_PER_MODEL` | `2` | Max concurrent chunks for inferencing per model |
| `TTS_MAX_CHUNK_CHARS` | `140` | Max characters per text chunk. Text longer than this is split into chunks and synthesized separately, then concatenated. |
| `TTS_MODELS_DIR` | `.models/silero` | Directory for downloaded Silero .pt model files |
| `TTS_ENV_TYPE` | `development` | Application environment: `development` or `production`. Controls error detail level in 500 responses, log format (colorized/plain), log level (DEBUG/INFO), backtrace/diagnose, and file logging in production. |
| `TTS_MODELS_YML_URL` | `https://raw.githubusercontent.com/snakers4/silero-models/.../models.yml` | URL to the Silero models.yml registry file downloaded at runtime. |
| `TTS_MODELS_YML_HASH` | `c981f239ed79b3924f952eb3a4dee3a03221d9867330c2b4054c767df77a86d8` | SHA-256 hash of the models.yml for integrity verification. Set empty to skip validation. |

Validated at startup via Pydantic Settings — app exits with a clear error on invalid values.

### Error Responses

All errors return JSON `{"detail": "..."}`. HTTP status codes:
- `400 Bad Request` — unsupported locale/voice/audio format, text too long, invalid input type.
- `406 Not Acceptable` — unsupported output type (PHONEMES, TOKENS).
- `500 Internal Server Error` — engine failure (model loading, synthesis error, or second-line validation miss). Body is generic; detail is logged server-side.

### Health Check

`GET /health` returns extended status:
- `status`: always `"ok"`

### Docker Strategy

- **Default image**: CPU-only, `python:3.14-slim-bookworm`.

## Key Conventions

- **API versioning**: Not versioned at the URL path level. Mary TTS compatibility requires root-level paths.
- **Response format**: Raw bytes for audio; JSON for errors and health.
- **No rate limiting** at the application layer — delegate to infrastructure.
- **No API key auth** at the application layer — delegate to infrastructure.
- **Graceful shutdown**: Gunicorn drains in-flight requests before exit (default graceful timeout).