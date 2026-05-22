from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse, StreamingResponse

from src.deps import EngineDep, SettingsDep

router = APIRouter(tags=["process"])


async def process_request(
    engine: EngineDep,
    settings: SettingsDep,
    INPUT_TEXT: str,
    LOCALE: str,
    VOICE: str,
    INPUT_TYPE: str = "TEXT",
    OUTPUT_TYPE: str = "AUDIO",
    AUDIO: str = "WAVE_FILE",
):
    """Common processing logic for GET and POST."""
    if len(INPUT_TEXT) > settings.TTS_MAX_TEXT_LENGTH:
        return JSONResponse(
            status_code=400,
            content={"detail": "Input text exceeds maximum length"},
        )

    if AUDIO != "WAVE_FILE":
        return JSONResponse(
            status_code=400,
            content={"detail": "Unsupported audio format"},
        )

    if not engine.has_locale(LOCALE):
        return JSONResponse(
            status_code=400,
            content={"detail": f"Unsupported locale: {LOCALE}"},
        )

    if not engine.has_voice(LOCALE, VOICE):
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid voice: {VOICE}"},
        )

    if INPUT_TYPE not in engine.get_input_types():
        return JSONResponse(
            status_code=400,
            content={"detail": f"Invalid input type: {INPUT_TYPE}"},
        )

    if OUTPUT_TYPE != "AUDIO":
        return JSONResponse(
            status_code=406,
            content={"detail": f"Invalid output type: {OUTPUT_TYPE}"},
        )

    result = await engine.process(INPUT_TEXT, LOCALE, VOICE, INPUT_TYPE)

    return StreamingResponse(
        content=result.audio,
        media_type="audio/wav",
        headers={"Content-Disposition": "inline"},
    )


@router.get("/process")
async def process_get(
    engine: EngineDep,
    settings: SettingsDep,
    INPUT_TEXT: str = Query(..., description="Text to synthesize"),
    LOCALE: str = Query(..., description="Locale (e.g., ru_RU)"),
    VOICE: str = Query(..., description="Voice name"),
    INPUT_TYPE: str = Query("TEXT", description="Input type: TEXT, SSML"),
    OUTPUT_TYPE: str = Query("AUDIO", description="Output type: AUDIO"),
    AUDIO: str = Query("WAVE_FILE", description="Audio format"),
):
    """Synthesize text to speech."""
    return await process_request(
        engine, settings, INPUT_TEXT, LOCALE, VOICE, INPUT_TYPE, OUTPUT_TYPE, AUDIO
    )


@router.post("/process")
async def process_post(
    engine: EngineDep,
    settings: SettingsDep,
    INPUT_TEXT: str = Form(..., description="Text to synthesize"),
    LOCALE: str = Form(..., description="Locale (e.g., ru_RU)"),
    VOICE: str = Form(..., description="Voice name"),
    INPUT_TYPE: str = Form("TEXT", description="Input type: TEXT, SSML"),
    OUTPUT_TYPE: str = Form("AUDIO", description="Output type: AUDIO"),
    AUDIO: str = Form("WAVE_FILE", description="Audio format"),
):
    """Synthesize text to speech via form data."""
    return await process_request(
        engine, settings, INPUT_TEXT, LOCALE, VOICE, INPUT_TYPE, OUTPUT_TYPE, AUDIO
    )
