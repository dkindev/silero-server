from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    tts_device: str = "cpu"
    """Device to run TTS model on: 'cpu' or 'cuda'."""

    tts_model_path: str = "./models"
    """Path to cache Silero TTS models."""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
