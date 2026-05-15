class TTSEngineError(Exception):
    def __init__(self, message: str, locale: str | None = None, voice: str | None = None):
        self.message = message
        self.locale = locale
        self.voice = voice
        super().__init__(message)

    @property
    def status_code(self) -> int:
        return 500


class InvalidLocaleError(TTSEngineError):
    @property
    def status_code(self) -> int:
        return 400


class InvalidVoiceError(TTSEngineError):
    @property
    def status_code(self) -> int:
        return 400


class InvalidInputTypeError(TTSEngineError):
    @property
    def status_code(self) -> int:
        return 400


class InvalidOutputTypeError(TTSEngineError):
    @property
    def status_code(self) -> int:
        return 406


class TTSProcessingError(TTSEngineError):
    @property
    def status_code(self) -> int:
        return 500
