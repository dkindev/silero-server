from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.deps import EngineDep

router = APIRouter(tags=["locales"])


@router.get("/locales", response_class=PlainTextResponse)
async def get_locales(engine: EngineDep) -> str:
    """Return supported locales, one per line."""
    locales = engine.get_locales()
    return "\n".join(locales)
