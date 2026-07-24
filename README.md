# Wyoming Silero TTS

[Wyoming protocol](https://github.com/OHF-Voice/wyoming) server wrapping [Silero TTS models](https://github.com/snakers4/silero-models). Supports Home Assistant integration, streaming audio, and optional per-voice LLM normalization.

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

5. **Test with HTTP server**
    ```bash
    uv run --with "wyoming[http]" python -m wyoming.http.tts_server --uri tcp://127.0.0.1:10200
    ```

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

1. **CLI arguments** — `--uri`, `--torch_device`, `--sample_rate`, etc.
2. **Environment variables** — `TTS_URI`, `TTS_TORCH__DEVICE`, `TTS_SAMPLE_RATE`, etc.
3. **config.yml** — YAML file at the project root
4. **Defaults** — Default values in code

See `config.yml` for full configuration reference with all fields, CLI argument names, and environment variable names.

## Voice and Model Configuration

Voice and model mappings are defined in `data/data.yml`. The file has two top-level sections: `models` and `prompts`.

### Models

```yaml
models:
  v5_5_ru:
    language: ru
    warmup: true
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

#### Adding a new model

1. Add a model entry under `models:` in `data/data.yml` with the Silero language identifier.
2. Add locales with voices referencing the new model.

#### Disabling a model

Set `enabled: false` on the model entry. Its voices are automatically excluded from discovery.

### Voices

Each voice entry has the following fields:

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `name` | Yes | — | Voice name |
| `speaker` | No | voice name | Silero's native speaker identifier |
| `model` | No | parent model | Explicit model reference (usually inherited from parent) |
| `normalization.text.enabled` | No | `true` | Override text normalization enabled state |
| `normalization.text.type` | No | `simple` | Override normalization type (`simple`, `llm`) |
| `normalization.text.prompt_id` | No | — | Reference a custom LLM prompt from `prompts` |
| `normalization.ssml.enabled` | No | `false` | Override SSML normalization enabled state |
| `normalization.ssml.type` | No | `simple` | Override SSML normalization type |
| `normalization.ssml.prompt_id` | No | — | Reference a custom LLM prompt for SSML |

Voices are identified by their computed ID: `{locale}-{model}-{name}` (e.g., `ru_RU-v5_5_ru-aidar`).

#### Adding or renaming voices

Add or edit entries under `locales.*.voices` in `data/data.yml`. Set `speaker` to the Silero native speaker name only if it differs from the voice name.

#### Voice normalization

Per-voice override of the server-wide normalization settings (defined in `config.yml`). Override the normalization type, disable it entirely, or reference a custom LLM prompt.

```yaml
models:
  v5_5_ru:
    locales:
      ru_RU:
        voices:
          - name: aidar
            normalization:
              text:
                enabled: true
                type: llm
                prompt_id: ru_text

prompts:
  - id: ru_text
    text: "Normalize Russian text for TTS..."
    model: qwen3.5:4b
```

Without a `normalization` block on a voice, the server-wide defaults from `config.yml` apply.

### Prompts

Reusable LLM prompt definitions referenced by `prompt_id` in voice normalization.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `id` | Yes | — | Unique identifier referenced by `prompt_id` |
| `text` | Yes | — | LLM prompt instruction text |
| `model` | Yes | — | LLM model name (e.g., `qwen3.5:4b`) |

## Audio

### Supported Input Types

- `TEXT` — plain text
- `SSML` — Speech Synthesis Markup Language

### Audio Output

- Format: raw PCM (WAV-compatible)
- Sample rate: configurable (8000, 16000, 24000, 48000 Hz)
- Bit depth: 16-bit signed integer
- Channels: mono (1 channel)

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
