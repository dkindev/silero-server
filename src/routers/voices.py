from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.main import EngineDep

router = APIRouter(tags=["voices"])


@router.get("/voices", response_class=PlainTextResponse)
async def get_voices(engine: EngineDep) -> str:
    """Return available voices in Mary-TTS format, one per line."""
    voices = engine.get_voices()
    return "\n".join(voices)
