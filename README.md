# Silero TTS Server

A simple, robust, and performant Mary-TTS compatible HTTP API that wraps the Silero TTS engine, enabling any client (web, mobile, desktop, embedded) to generate speech audio over HTTP/HTTPS with minimal latency and operational overhead.

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/dkindev/silero-server.git
   cd silero-server
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv sync --extra dev
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

5. **Run the application**
   ```bash
   uvicorn src.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

6. **Access API documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Docker

1. **Build the image**
   ```bash
   docker build -t silero-server:latest .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 silero-server:latest
   ```

   > **Note:** This image runs on CPU only. CUDA/GPU support is not yet containerized.

## API Endpoints

### Process

Synthesizes text to speech audio. Supports GET and POST.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `INPUT_TEXT` | string | Yes | — | Text to synthesize |
| `LOCALE` | string | Yes | — | Mary-TTS locale (e.g., `ru_RU`) |
| `VOICE` | string | Yes | — | Voice name |
| `INPUT_TYPE` | string | No | `TEXT` | Input format: `TEXT`, `SSML` |
| `OUTPUT_TYPE` | string | No | `AUDIO` | Output format: `AUDIO` (others rejected) |
| `AUDIO` | string | No | `WAVE_FILE` | Audio format: `WAVE_FILE` (others rejected) |

**Validation:**
- Input text must not exceed the configured max length (default 1000 chars) — `400 Bad Request`
- Audio must be `WAVE_FILE` — `400 Bad Request`
- Locale and voice must exist — `400 Bad Request`
- Input type must be `TEXT` or `SSML` — `400 Bad Request`
- Output type must be `AUDIO` — `406 Not Acceptable`

**Response:** WAV audio streamed with `Content-Type: audio/wav`.

### Locales

Returns all supported Mary-TTS locales.

- **Endpoint**: `GET /locales`
- **Response**: Plain text, one locale per line (e.g., `ru_RU`)
- **Status Code**: 200

### Voices

Returns all available voices.

- **Endpoint**: `GET /voices`
- **Response**: Plain text, one voice per line in format `{voice_name} {locale} {gender}`
- **Status Code**: 200

### Health Check
- **Endpoint**: `GET /health`
- **Response**: `{"status": "ok"}`
- **Status Code**: 200

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_TORCH_DEVICE` | `cpu` | `cpu`, `cuda`, or `xpu`. Falls back to `cpu` at runtime if requested device is unavailable. |
| `TTS_TORCH_NUM_THREADS` | `4` | PyTorch intra-op thread count (`torch.set_num_threads`). Must be ≥ 1. |
| `TTS_TORCH_NUM_INTEROP_THREADS` | `1` | PyTorch inter-op thread count (`torch.set_num_interop_threads`). Must be ≥ 1. |
| `TTS_TORCH_FLUSH_DENORMAL` | `true` | Flush denormal floats for performance (`torch.set_flush_denormal`). Only called when `hasattr` passes. |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz). Supported: 8000, 16000, 22050, 24000, 48000 |
| `TTS_MAX_TEXT_LENGTH` | `1000` | Max input characters. |
| `TTS_ALLOWED_ORIGINS` | `*` | CORS allowed origins. |
| `TTS_CONFIG_PATH` | `silero-to-mary-config.yml` | Path to voice/locale mapping config. |
| `TTS_MAX_MODELS` | `2` | Max models cached in memory. Oldest evicted when limit reached. |
| `TTS_MAX_CONCURRENT_PER_MODEL` | `2` | Max concurrent chunks for inferencing per model. |
| `TTS_MAX_CHUNK_CHARS` | `140` | Max characters per text chunk. Longer text is split automatically. |
| `TTS_MODELS_DIR` | `.models/silero` | Directory for downloaded Silero .pt model files. |
| `TTS_ENV_TYPE` | `development` | Application environment: `development` or `production`. Controls error detail level, log format, log level, and file logging. |

## Configuration

Voice and locale mappings are defined in a YAML config file (default `silero-to-mary-config.yml`). The config has two top-level sections: `models` and `locales`.

### Models

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

Each model key (e.g., `v5_5_ru`) is the model name. Supported fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `language` | Yes | — | Silero language identifier (`ru`, `en`, `de`, etc.) |
| `enabled` | No | `true` | `false` to disable the model and exclude its voices |
| `warmup` | No | `false` | `true` to preload at startup; `false` for lazy loading |
| `hash_prefix` | No | — | SHA-256 hash prefix for download integrity verification; empty or omitted skips verification |

### Locales and Voices

```yaml
locales:
  ru_RU:
    voices:
      aidar:
        model: v5_5_ru
        gender: male
      custom_name:
        speaker: en_0
        model: v3_en
        gender: female
```

Each locale key follows Mary-TTS format (`{language}_{COUNTRY}`, e.g., `ru_RU`). A locale is available in the API only when at least one of its voices references an enabled model.

Each voice key is the voice name. Supported fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `model` | Yes | — | References a model key from the `models:` section |
| `gender` | Yes | — | Speaker gender label (e.g., `male`, `female`) |
| `speaker` | No | voice name | Silero's native speaker identifier; must match a speaker known to the model |

## Customization

### Adding a new language

1. Add a model entry under `models:` with the Silero language identifier.
2. Add a locale entry under `locales:` with one or more voices referencing the new model.

### Adding or renaming voices

Add or edit entries under `locales.*.voices`. Set `speaker` to the Silero native speaker name only if it differs from the voice name.

### Disabling a model

Set `enabled: false` on the model entry. Its voices are automatically excluded from API responses.

### Performance tuning

| Variable | Effect |
|----------|--------|
| `TTS_MAX_MODELS` | Maximum models cached in memory (oldest evicted) |
| `TTS_MAX_CONCURRENT_PER_MODEL` | Max concurrent synthesis chunks per model |
| `TTS_MAX_CHUNK_CHARS` | Max characters per text chunk before splitting |

### Hardware selection

Set `TTS_TORCH_DEVICE` to `cpu`, `cuda`, or `xpu`. Falls back to `cpu` if the requested device is unavailable.

### Sample rate

Set `TTS_SAMPLE_RATE` to any of 8000, 16000, 22050, 24000, or 48000 Hz. The engine automatically selects the best-supported rate from the model.

### Custom text preprocessing

Write a subclass of `TextPreprocessor` for a locale and register it in the `_TEXT_PREPROCESSOR_BUILDERS` dict in `src/deps.py`.

## Development

### Running Tests

```bash
pytest tests/
```

### Linting and Formatting

```bash
# Check code with Ruff
ruff check src tests

# Format code with Ruff
ruff format src tests
```

### Pre-commit Hooks

Install pre-commit hooks to automatically lint and format code before commits:

```bash
pre-commit install
```

This will run Ruff linting and formatting on staged files before each commit.

## CI/CD

The project uses GitHub Actions for continuous integration. On every push:

1. **Lint**: Ruff checks code quality across Python 3.11, 3.12, 3.13, and 3.14
2. **Test**: pytest runs all tests across the same Python versions

See `.github/workflows/ci.yml` for details.

## License

MIT License - see LICENSE file for details.
