from fastapi import FastAPI


def setup_routers(app: FastAPI) -> None:
    """Configure routers for the application."""

    from src.routers import health, locales, process, voices

    app.include_router(health.router)
    app.include_router(locales.router)
    app.include_router(voices.router)
    app.include_router(process.router)
