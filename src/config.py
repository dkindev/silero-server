from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    tts_device: str = "cpu"
    """Device to run TTS model on: 'cpu' or 'cuda'."""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
