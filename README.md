# Silero TTS Server

A simple, robust, and performant Wyoming protocol TTS server that wraps the Silero TTS engine, enabling Home Assistant and other Wyoming clients to generate speech audio over TCP with minimal latency and operational overhead.

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
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   uv sync --extra dev
   ```

4. **Run the application**
   ```bash
   python -m src.main
   ```

   The server listens on `tcp://127.0.0.1:10200` by default.

### Docker

1. **Build the image**
   ```bash
   docker build -t silero-server:latest .
   ```

2. **Run the container**
   ```bash
   docker run -p 10200:10200 \
     -e TTS_ENV_TYPE=production \
     -v ./data:/app/data \
     -v ./models:/app/models \
     silero-server:latest
   ```

   The server exposes port `10200` for Wyoming TCP connections.

## Configuration

Configuration is resolved with the following priority (highest first):

1. **CLI arguments** — `--uri`, `--torch_device`, `--tts_sample_rate`, etc.
2. **Environment variables** — `TTS_URI`, `TTS_TORCH_DEVICE`, `TTS_SAMPLE_RATE`, etc.
3. **config.yml** — YAML file at the project root
4. **Defaults** — Pydantic `Field(default=...)`

### CLI Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--uri` | str | `tcp://127.0.0.1:10200` | Server URI (Wyoming TCP) |
| `--zeroconf` | str | `silero` | Zeroconf discovery name |
| `--streaming` / `--no-streaming` | bool | `true` | Enable audio streaming |
| `--env_type` | str | `development` | `development` or `production` |
| `--torch_device` | str | `cpu` | PyTorch device (`cpu`, `cuda`, `xpu`) |
| `--torch_num_threads` | int | `4` | Intra-op thread count |
| `--torch_num_interop_threads` | int | `1` | Inter-op thread count |
| `--torch_flush_denormal` / `--no-torch_flush_denormal` | bool | `true` | Flush denormal floats for performance |
| `--tts_sample_rate` | int | `48000` | Output sample rate (8000, 16000, 24000, 48000) |
| `--tts_max_models` | int | `2` | Max models cached in memory |
| `--tts_max_concurrent_per_model` | int | `2` | Max concurrent chunks per model |
| `--tts_max_chunk_chars` | int | `140` | Max characters per text chunk |
| `--tts_data_yml_path` | str | `data/data.yml` | Path to the voice/model mapping config |
| `--tts_models_dir` | str | `models/silero` | Directory for downloaded model files |
| `--tts_models_yml_url` | str | *(see config.yml)* | URL to the Silero models registry |
| `--tts_models_yml_hash` | str | `""` | SHA-256 hash of the models registry |

### Environment Variables

All env vars use the `TTS_` prefix:

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_ENV_TYPE` | `development` | `development` or `production`. Controls log level, format, and file logging. |
| `TTS_URI` | `tcp://127.0.0.1:10200` | Wyoming server URI |
| `TTS_ZEROCONF` | `silero` | Zeroconf discovery name. Empty string disables. |
| `TTS_STREAMING` | `true` | Enable audio streaming |
| `TTS_TORCH_DEVICE` | `cpu` | `cpu`, `cuda`, or `xpu`. Falls back to `cpu` at runtime if unavailable. |
| `TTS_TORCH_NUM_THREADS` | `4` | PyTorch intra-op thread count |
| `TTS_TORCH_NUM_INTEROP_THREADS` | `1` | PyTorch inter-op thread count |
| `TTS_TORCH_FLUSH_DENORMAL` | `true` | Flush denormal floats for performance |
| `TTS_SAMPLE_RATE` | `48000` | Output audio sample rate (Hz) |
| `TTS_MAX_MODELS` | `2` | Max models cached in memory (oldest evicted) |
| `TTS_MAX_CONCURRENT_PER_MODEL` | `2` | Max concurrent synthesis chunks per model |
| `TTS_MAX_CHUNK_CHARS` | `140` | Max characters per text chunk |
| `TTS_DATA_YML_PATH` | `data/data.yml` | Path to the voice/model mapping config |
| `TTS_MODELS_DIR` | `models/silero` | Directory for downloaded model files |
| `TTS_MODELS_YML_URL` | *(see below)* | URL to Silero models.yml registry |
| `TTS_MODELS_YML_HASH` | `""` | SHA-256 hash for integrity verification |

### config.yml

```yaml
uri: tcp://127.0.0.1:10200
zeroconf: silero
env_type: development
streaming: true

torch:
  device: cpu
  num_threads: 4
  num_interop_threads: 1
  flush_denormal: true

tts:
  sample_rate: 48000
  max_models: 2
  max_concurrent_per_model: 2
  max_chunk_chars: 140
  models_dir: models/silero
  data_yml_path: data/data.yml
  models_yml_url: https://raw.githubusercontent.com/snakers4/silero-models/refs/heads/master/models.yml
  models_yml_hash: ""
```

## Voice and Model Configuration

Voice and locale mappings are defined in a YAML config file (default `data/data.yml`). The config has a `models` top-level section containing model entries.

### Models

```yaml
models:
  v5_5_ru:
    language: ru
    warmup: true
    hash_prefix: 50081637b602126ee06cb3bc8a744d25651d2da149ee8864b9a379bfdd934437
    locales:
      ru_RU:
        voices:
          - name: aidar
          - name: eugene
          - name: baya
          - name: kseniya
          - name: xenia
  v3_en:
    language: en
    locales:
      en_US:
        voices:
          - name: henry
            speaker: en_2
          - name: sophia
            speaker: en_3
```

Each model key (e.g., `v5_5_ru`) is the model name. Supported fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `language` | Yes | — | Silero language identifier (`ru`, `en`, etc.) |
| `enabled` | No | `true` | `false` to disable the model and exclude its voices |
| `warmup` | No | `false` | `true` to preload at startup; `false` for lazy loading |
| `hash_prefix` | No | — | SHA-256 hash prefix for download integrity verification |
| `locales` | Yes | — | Map of locale codes to voice lists |

Each voice entry has the following fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | — | Voice name |
| `speaker` | No | voice name | Silero's native speaker identifier |
| `model` | No | parent model | Explicit model reference (usually inherited from parent) |

Voices are identified in the Wyoming protocol by their computed ID: `{locale}-{model}-{name}` (e.g., `ru_RU-v5_5_ru-aidar`).

## Wyoming Protocol

This server implements the **Wyoming protocol** — a TCP-based protocol used by Home Assistant for satellite and voice pipeline integration. It is **not** an HTTP REST API.

### How it works

1. **Discovery**: Clients connect over TCP. The server responds to `Describe` events with an `Info` event listing all supported voices and languages.
2. **Synthesis**: Clients send a `Synthesize` event with a voice name and text. The server streams audio back as `AudioStart` → `AudioChunk(s)` → `AudioStop` events.
3. **Streaming**: Clients can also stream text incrementally via `SynthesizeStart`/`SynthesizeChunk`/`SynthesizeStop` events.

### Supported Input Types

- `TEXT` — plain text
- `SSML` — Speech Synthesis Markup Language

### Audio Output

- Format: raw PCM (WAV-compatible)
- Sample rate: configurable (8000, 16000, 24000, 48000 Hz)
- Bit depth: 16-bit signed integer
- Channels: mono (1 channel)

## Customization

### Adding a new model

1. Add a model entry under `models:` in `data/data.yml` with the Silero language identifier.
2. Add locales with voices referencing the new model.

### Adding or renaming voices

Add or edit entries under `locales.*.voices` in `data/data.yml`. Set `speaker` to the Silero native speaker name only if it differs from the voice name.

### Disabling a model

Set `enabled: false` on the model entry. Its voices are automatically excluded from discovery.

### Performance tuning

| Setting | Effect |
|---------|--------|
| `TTS_MAX_MODELS` | Maximum models cached in memory (oldest evicted) |
| `TTS_MAX_CONCURRENT_PER_MODEL` | Max concurrent synthesis chunks per model |
| `TTS_MAX_CHUNK_CHARS` | Max characters per text chunk before splitting |

### Hardware selection

Set `TTS_TORCH_DEVICE` to `cpu`, `cuda`, or `xpu`. Falls back to `cpu` if the requested device is unavailable.

### Sample rate

Set `TTS_SAMPLE_RATE` to any of 8000, 16000, 24000, or 48000 Hz. The engine automatically selects the best-supported rate from the model's capabilities.

### Custom text preprocessing

Write a subclass of `TextPreprocessor` and register it in the `_TEXT_PREPROCESSOR_BUILDERS` dict in `src/main.py`. Currently `ru_RU` uses `RuTextPreprocessor` (with `razdel` for Russian sentence splitting); all other locales use the base `TextPreprocessor`.

## Development

### Running Tests

```bash
pytest tests/
```

### Linting and Formatting

```bash
ruff check src tests
ruff format src tests
```

### Pre-commit Hooks

```bash
pre-commit install
```

## CI/CD

The project uses GitHub Actions for continuous integration. On every push:

1. **Lint**: Ruff checks code quality across Python 3.11, 3.12, 3.13, and 3.14
2. **Test**: pytest runs all tests across the same Python versions

See `.github/workflows/ci.yml` for details.

## License

MIT License — see LICENSE file for details.
