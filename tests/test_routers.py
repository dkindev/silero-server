import io
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.deps import EngineDep, get_engine_from_request
from src.handlers import add_global_exception_handler
from src.tts.exceptions import TTSEngineError


class TestExceptionHandler:
    """Test global exception handler for TTS engine errors."""

    def test_tts_engine_error_returns_500(self, monkeypatch):
        """TTSEngineError should return 500 status code."""
        monkeypatch.setenv("TTS_ENV_TYPE", "production")
        from src.config import get_settings

        get_settings.cache_clear()

        mock_engine = MagicMock()
        mock_engine.process.side_effect = TTSEngineError("Model failed")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override
        add_global_exception_handler(app)

        @app.get("/test-processing")
        async def test_processing(engine: EngineDep):
            return await engine.process("test", "ru_RU", "voice", "TEXT")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-processing")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"

    def test_production_mode_hides_error_detail(self, monkeypatch):
        """Production mode should return generic error message in 500 responses."""
        monkeypatch.setenv("TTS_ENV_TYPE", "production")
        from src.config import get_settings

        get_settings.cache_clear()

        app = FastAPI()

        @app.get("/boom")
        async def boom():
            raise RuntimeError("something broke")

        add_global_exception_handler(app)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/boom")

        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"

    def test_development_mode_shows_error_detail(self, monkeypatch):
        """Development mode should include exception message in 500 responses."""
        monkeypatch.setenv("TTS_ENV_TYPE", "development")
        from src.config import get_settings

        get_settings.cache_clear()

        app = FastAPI()

        @app.get("/boom")
        async def boom():
            raise RuntimeError("something broke")

        add_global_exception_handler(app)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/boom")

        assert response.status_code == 500
        assert "something broke" in response.json()["detail"]


class TestLocalesEndpoint:
    """Test GET /locales endpoint."""

    def test_locales_returns_200(self):
        """GET /locales should return 200 status code."""
        from src.deps import get_engine_from_request
        from src.tts.models import Locale

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_locales.return_value = [
            Locale(name="ru_RU"),
            Locale(name="en_US"),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.status_code == 200

    def test_locales_returns_plain_text(self):
        """GET /locales should return text/plain content type."""
        from src.deps import get_engine_from_request
        from src.tts.models import Locale

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_locales.return_value = [
            Locale(name="ru_RU"),
            Locale(name="en_US"),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.headers["content-type"] == "text/plain; charset=utf-8"

    def test_locales_returns_one_per_line(self):
        """GET /locales should return one locale per line."""
        from src.deps import get_engine_from_request
        from src.tts.models import Locale

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_locales.return_value = [
            Locale(name="ru_RU"),
            Locale(name="de_DE"),
            Locale(name="en_US"),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import locales

        app.include_router(locales.router)

        client = TestClient(app)
        response = client.get("/locales")

        assert response.text == "ru_RU\nde_DE\nen_US"


class TestVoicesEndpoint:
    """Test GET /voices endpoint."""

    def test_voices_returns_200(self):
        """GET /voices should return 200 status code."""
        from src.deps import get_engine_from_request
        from src.tts.models import VoiceConfig

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_voices.return_value = [
            VoiceConfig(
                voice_name="silero-v5_5_ru-aidar",
                speaker="aidar",
                model="v5_5_ru",
                gender="male",
                locale="ru_RU",
            ),
            VoiceConfig(
                voice_name="silero-v5_5_ru-baya",
                speaker="baya",
                model="v5_5_ru",
                gender="female",
                locale="ru_RU",
            ),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import voices

        app.include_router(voices.router)

        client = TestClient(app)
        response = client.get("/voices")

        assert response.status_code == 200

    def test_voices_returns_plain_text(self):
        """GET /voices should return text/plain content type."""
        from src.deps import get_engine_from_request
        from src.tts.models import VoiceConfig

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_voices.return_value = [
            VoiceConfig(
                voice_name="silero-v5_5_ru-aidar",
                speaker="aidar",
                model="v5_5_ru",
                gender="male",
                locale="ru_RU",
            ),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import voices

        app.include_router(voices.router)

        client = TestClient(app)
        response = client.get("/voices")

        assert "text/plain" in response.headers["content-type"]

    def test_voices_returns_mary_tts_format(self):
        """GET /voices should return voices in Mary-TTS format, one per line."""
        from src.deps import get_engine_from_request
        from src.tts.models import VoiceConfig

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.get_voices.return_value = [
            VoiceConfig(
                voice_name="silero-v5_5_ru-aidar",
                speaker="aidar",
                model="v5_5_ru",
                gender="male",
                locale="ru_RU",
            ),
            VoiceConfig(
                voice_name="silero-v5_5_ru-baya",
                speaker="baya",
                model="v5_5_ru",
                gender="female",
                locale="ru_RU",
            ),
            VoiceConfig(
                voice_name="silero-v3_en-en_0",
                speaker="en_0",
                model="v3_en",
                gender="male",
                locale="en_US",
            ),
        ]

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

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
        from src.deps import get_engine_from_request
        from src.tts.result import TTSResult

        mock_audio = io.BytesIO(b"RIFF" + b"\x00" * 1000)
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = MagicMock()
        mock_engine.process = AsyncMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types = MagicMock(return_value=("TEXT", "SSML"))
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar")

        assert "audio/wav" in response.headers["content-type"]

    def test_process_returns_content_disposition_inline(self):
        """GET /process should return Content-Disposition: inline."""
        from src.deps import get_engine_from_request
        from src.tts.result import TTSResult

        mock_audio = io.BytesIO(b"RIFF" + b"\x00" * 1000)
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = MagicMock()
        mock_engine.process = AsyncMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types = MagicMock(return_value=("TEXT", "SSML"))
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar")

        assert response.headers.get("content-disposition") == "inline"

    def test_process_text_too_long_returns_400(self):
        """GET /process should return 400 if text exceeds max length."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        long_text = "a" * 2000

        client = TestClient(app)
        response = client.get(
            f"/process?INPUT_TEXT={long_text}&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar"
        )

        assert response.status_code == 400

    def test_process_invalid_audio_returns_400(self):
        """GET /process should return 400 for unsupported audio format."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types.return_value = ("TEXT", "SSML")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar&AUDIO=MP3"
        )

        assert response.status_code == 400
        assert response.json() == {"detail": "Unsupported audio format"}

    def test_process_invalid_locale_returns_400(self):
        """GET /process should return 400 for invalid locale."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.has_locale.return_value = False

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=xx_XX&VOICE=silero-v5_5_ru-aidar")

        assert response.status_code == 400
        assert "Unsupported locale" in response.json()["detail"]

    def test_process_invalid_voice_returns_400(self):
        """GET /process should return 400 for invalid voice."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = False

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=bad")

        assert response.status_code == 400
        assert "Invalid voice" in response.json()["detail"]

    def test_process_invalid_input_type_returns_400(self):
        """GET /process should return 400 for invalid input type."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types.return_value = ("TEXT", "SSML")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar&INPUT_TYPE=RAWMARYXML"
        )

        assert response.status_code == 400
        assert "Invalid input type" in response.json()["detail"]

    def test_process_invalid_output_type_returns_406(self):
        """GET /process should return 406 for unsupported output type."""
        from src.deps import get_engine_from_request

        mock_engine = MagicMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types.return_value = ("TEXT", "SSML")

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

        from src.routers import process

        app.include_router(process.router)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/process?INPUT_TEXT=Hello&LOCALE=ru_RU&VOICE=silero-v5_5_ru-aidar&OUTPUT_TYPE=PHONEMES"
        )

        assert response.status_code == 406
        assert "Invalid output type" in response.json()["detail"]


class TestProcessPostEndpoint:
    """Test POST /process endpoint."""

    def test_post_process_returns_wav(self):
        """POST /process should return WAV audio."""
        from src.deps import get_engine_from_request
        from src.tts.result import TTSResult

        mock_audio = io.BytesIO(b"RIFF" + b"\x00" * 1000)
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = MagicMock()
        mock_engine.process = AsyncMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types = MagicMock(return_value=("TEXT", "SSML"))
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

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
        from src.deps import get_engine_from_request
        from src.tts.result import TTSResult

        mock_audio = io.BytesIO(b"RIFF" + b"\x00" * 1000)
        mock_result = TTSResult(audio=mock_audio, sample_rate=48000, model="v5_5_ru")

        mock_engine = MagicMock()
        mock_engine.process = AsyncMock()
        mock_engine.get_storage.return_value.has_locale.return_value = True
        mock_engine.get_storage.return_value.has_voice.return_value = True
        mock_engine.get_input_types = MagicMock(return_value=("TEXT", "SSML"))
        mock_engine.process.return_value = mock_result

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

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
        from src.deps import get_engine_from_request

        mock_engine = AsyncMock()

        app = FastAPI()

        async def get_engine_override():
            return mock_engine

        app.dependency_overrides[get_engine_from_request] = get_engine_override

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
