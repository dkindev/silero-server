from src.tts.models import TTSConfig, TTSConfigModel


class SileroTTSEngine:
    """TTS engine wrapping Silero TTS library."""

    def __init__(self, config: TTSConfig, config_model: TTSConfigModel):
        self._config = config
        self._config_model = config_model
        self._locales = tuple(config_model.locales.keys())
        self._voices = self._build_voices()

    def _build_voices(self) -> tuple[str, ...]:
        voices = []
        for locale, locale_data in self._config_model.locales.items():
            for voice_name, voice_config in locale_data.voices.items():
                voices.append(f"{voice_name} {locale} {voice_config.gender}")
        return tuple(voices)

    def get_locales(self) -> tuple[str, ...]:
        """Return available locales."""
        return self._locales

    def get_voices(self) -> tuple[str, ...]:
        """Return available voices in Mary-TTS format."""
        return self._voices
