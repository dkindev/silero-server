from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.deps import EngineDep

router = APIRouter(tags=["voices"])


@router.get("/voices", response_class=PlainTextResponse)
async def get_voices(engine: EngineDep) -> str:
    """Return available voices in Mary-TTS format, one per line."""
    lines: list[str] = []
    for vc in engine.get_storage().get_voices():
        lines.append(f"{vc.voice_name} {vc.locale} {vc.gender}")
    return "\n".join(lines)
