from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.routers import EngineDep, get_engine, tts_exception_handler
from src.tts.exceptions import (
    InvalidInputTypeError,
    InvalidLocaleError,
    InvalidOutputTypeError,
    InvalidVoiceError,
    TTSProcessingError,
)


class TestExceptionHandler:
    """Test global exception handler for TTS engine errors."""

    def test_invalid_locale_returns_400(self):
        """InvalidLocaleError should return 400 status code."""
        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidLocaleError(
            "Unsupported locale: xx_XX", locale="xx_XX"
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidLocaleError, tts_exception_handler)

        @app.get("/test-locale")
        async def test_locale(engine: EngineDep):
            return engine.process("test", "xx_XX", "voice", "TEXT", "AUDIO")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-locale")

        assert response.status_code == 400
        assert response.json() == {"detail": "Unsupported locale: xx_XX"}

    def test_invalid_voice_returns_400(self):
        """InvalidVoiceError should return 400 status code."""
        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidVoiceError(
            "Invalid voice: bad", locale="ru_RU", voice="bad"
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidVoiceError, tts_exception_handler)

        @app.get("/test-voice")
        async def test_voice(engine: EngineDep):
            return engine.process("test", "ru_RU", "bad", "TEXT", "AUDIO")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-voice")

        assert response.status_code == 400

    def test_invalid_input_type_returns_400(self):
        """InvalidInputTypeError should return 400 status code."""
        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidInputTypeError("Invalid input type: INVALID")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidInputTypeError, tts_exception_handler)

        @app.get("/test-input")
        async def test_input(engine: EngineDep):
            return engine.process("test", "ru_RU", "voice", "INVALID", "AUDIO")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-input")

        assert response.status_code == 400

    def test_invalid_output_type_returns_406(self):
        """InvalidOutputTypeError should return 406 status code."""
        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidOutputTypeError("Invalid output type: PHONEMES")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidOutputTypeError, tts_exception_handler)

        @app.get("/test-output")
        async def test_output(engine: EngineDep):
            return engine.process("test", "ru_RU", "voice", "TEXT", "PHONEMES")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-output")

        assert response.status_code == 406

    def test_processing_error_returns_500(self):
        """TTSProcessingError should return 500 status code."""
        mock_engine = MagicMock()
        mock_engine.process.side_effect = TTSProcessingError("Model failed")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(TTSProcessingError, tts_exception_handler)

        @app.get("/test-processing")
        async def test_processing(engine: EngineDep):
            return engine.process("test", "ru_RU", "voice", "TEXT", "AUDIO")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-processing")

        assert response.status_code == 500


class TestLocalesEndpoint:
    """Test GET /locales endpoint."""

    def test_locales_returns_200(self):
        """GET /locales should return 200 status code."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_locales.return_value = ("ru_RU", "en_US")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.status_code == 200

    def test_locales_returns_plain_text(self):
        """GET /locales should return text/plain content type."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_locales.return_value = ("ru_RU", "en_US")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_locales_returns_one_per_line(self):
        """GET /locales should return one locale per line."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_locales.return_value = ("ru_RU", "de_DE", "en_US")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.text == "ru_RU\nde_DE\nen_US"


class TestVoicesEndpoint:
    """Test GET /voices endpoint."""

    def test_voices_returns_200(self):
        """GET /voices should return 200 status code."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_voices.return_value = (
            "silero-v5_5_ru-aidar ru_RU male",
            "silero-v5_5_ru-baya ru_RU female",
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import voices

        app.include_router(voices.router)

        client = TestClient(app)
        response = client.get("/voices")

        assert response.status_code == 200

    def test_voices_returns_plain_text(self):
        """GET /voices should return text/plain content type."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_voices.return_value = ("silero-v5_5_ru-aidar ru_RU male",)

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import voices

        app.include_router(voices.router)

        client = TestClient(app)
        response = client.get("/voices")

        assert "text/plain" in response.headers["content-type"]

    def test_voices_returns_mary_tts_format(self):
        """GET /voices should return voices in Mary-TTS format, one per line."""
        from src.routers import get_engine

        mock_engine = MagicMock()
        mock_engine.get_voices.return_value = (
            "silero-v5_5_ru-aidar ru_RU male",
            "silero-v5_5_ru-baya ru_RU female",
            "silero-v3_en-en_0 en_US male",
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import voices

        app.include_router(voices.router)

        client = TestClient(app)
        response = client.get("/voices")

        assert (
            response.text
            == "silero-v5_5_ru-aidar ru_RU male\nsilero-v5_5_ru-baya ru_RU female\nsilero-v3_en-en_0 en_US male"
        )


class TestProcessEndpoint:
    """Test GET /process endpoint."""

    def test_process_returns_wav(self):
        """GET /process should return WAV audio."""
        from src.routers import get_engine
        from src.tts.result import TTSResult

        mock_audio = b"RIFF" + b"\x00" * 1000
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = AsyncMock()
        mock_engine.process.return_value = mock_result
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar")

        assert "audio/wav" in response.headers["content-type"]

    def test_process_returns_content_disposition_inline(self):
        """GET /process should return Content-Disposition: inline."""
        from src.routers import get_engine
        from src.tts.result import TTSResult

        mock_audio = b"RIFF" + b"\x00" * 1000
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = AsyncMock()
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar")

        assert response.headers.get("content-disposition") == "inline"

    def test_process_text_too_long_returns_400(self):
        """GET /process should return 400 if text exceeds max length."""
        from src.routers import get_engine

        mock_engine = MagicMock()

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        long_text = "a" * 2000

        client = TestClient(app)
        response = client.get(
            f"/process?INPUT_TEXT={long_text}&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar"
        )

        assert response.status_code == 400

    def test_process_invalid_locale_returns_400(self):
        """GET /process should return 400 for invalid locale."""
        from src.routers import get_engine
        from src.tts.exceptions import InvalidLocaleError

        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidLocaleError(
            "Unsupported locale: xx_XX", locale="xx_XX"
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidLocaleError, tts_exception_handler)

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=xx_XX&VOICE=silero-v5_5_ru-aidar")

        assert response.status_code == 400

    def test_process_invalid_voice_returns_400(self):
        """GET /process should return 400 for invalid voice."""
        from src.routers import get_engine
        from src.tts.exceptions import InvalidVoiceError

        mock_engine = MagicMock()
        mock_engine.process.side_effect = InvalidVoiceError(
            "Invalid voice: bad", locale="ru_RU", voice="bad"
        )

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override
        app.add_exception_handler(InvalidVoiceError, tts_exception_handler)

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=bad")

        assert response.status_code == 400


class TestProcessPostEndpoint:
    """Test POST /process endpoint."""

    def test_post_process_returns_wav(self):
        """POST /process should return WAV audio."""
        from src.routers import get_engine
        from src.tts.result import TTSResult

        mock_audio = b"RIFF" + b"\x00" * 1000
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = AsyncMock()
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.post(
            "/process",
            data={
                "INPUT_TEXT": "Hello",
                "LOCALE": "ru_RU",
                "VOICE": "silero-v5_5_ru-aidar",
            },
        )

        assert response.status_code == 200

    def test_post_process_returns_audio_wav_content_type(self):
        """POST /process should return audio/wav content type."""
        from src.routers import get_engine
        from src.tts.result import TTSResult

        mock_audio = b"RIFF" + b"\x00" * 1000
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = AsyncMock()
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.post(
            "/process",
            data={
                "INPUT_TEXT": "Hello",
                "LOCALE": "ru_RU",
                "VOICE": "silero-v5_5_ru-aidar",
            },
        )

        assert "audio/wav" in response.headers["content-type"]

    def test_post_process_text_too_long_returns_400(self):
        """POST /process should return 400 if text exceeds max length."""
        from src.routers import get_engine

        mock_engine = AsyncMock()

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        long_text = "a" * 2000

        client = TestClient(app)
        response = client.post(
            "/process",
            data={
                "INPUT_TEXT": long_text,
                "LOCALE": "ru_RU",
                "VOICE": "silero-v5_5_ru-aidar",
            },
        )

        assert response.status_code == 400
