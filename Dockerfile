FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock* README.md ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY src/ ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM python:3.14-slim-bookworm

RUN set -x; \
    apt-get update && \
	apt-get install -y --no-install-recommends \
        # grab gosu for easy step-down from root
        gosu \
        && \
	rm -rf /var/lib/apt/lists/* && \
    # verify that the gosu binary works
	gosu nobody true

WORKDIR /app

ARG UID=1000
ARG GID=1000

RUN set -x; \
    groupadd --system --gid $GID silero && \
    useradd --system --gid silero --home-dir /app --comment "silero user" --shell /bin/bash --uid $UID silero

COPY --from=builder /app/.venv /app/.venv
COPY silero-to-mary-config.yml .
COPY src/ ./src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health', timeout=2)" || exit 1

COPY --chmod=555 docker-entrypoint.sh /usr/local/bin
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "src.main:app", "--bind", "0.0.0.0:8000"]