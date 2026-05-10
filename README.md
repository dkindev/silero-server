# Silero TTS Server

A simple, robust, and performant Mary-TTS compatible REST API that wraps the Silero TTS engine, enabling any client (web, mobile, desktop, embedded) to generate speech audio over HTTP/HTTPS with minimal latency and operational overhead.

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
   pip install -e ".[dev]"
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

## API Endpoints

### Health Check
- **Endpoint**: `GET /api/v1/health`
- **Response**: `{"status": "ok"}`
- **Status Code**: 200

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_DEVICE` | `cpu` | Device to run TTS model on: `cpu` or `cuda` |

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

## Project Structure

```
silero-server/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings and configuration
│   └── routers/
│       ├── __init__.py
│       └── health.py        # Health check endpoint
├── tests/
│   ├── __init__.py
│   └── test_health.py       # Health endpoint tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── .env.example             # Environment variables template
├── Dockerfile               # Production Docker image
├── pyproject.toml           # Project configuration and dependencies
├── README.md                # This file
└── LICENSE                  # MIT License
```

## CI/CD

The project uses GitHub Actions for continuous integration. On every push:

1. **Lint**: Ruff checks code quality across Python 3.10, 3.11, 3.12, and 3.13
2. **Test**: pytest runs all tests across the same Python versions

See `.github/workflows/ci.yml` for details.

## License

MIT License - see LICENSE file for details.

## Author

Dmitry Kiselev
