import asyncio
import signal
from functools import partial

import torch
from loguru import logger
from wyoming.server import AsyncServer, AsyncTcpServer

from src.config import Settings, get_settings
from src.handler import SileroWyomingHandler
from src.logger import setup_logging
from src.tts.config_storage import SileroTTSYamlConfigStorage
from src.tts.engine import SileroTTSEngine
from src.tts.models import TTSConfig
from src.tts.preprocessing import RuTextPreprocessor, TextPreprocessor

setup_logging()

_TEXT_PREPROCESSOR_BUILDERS: dict[str, type[TextPreprocessor]] = {
    "ru_RU": RuTextPreprocessor,
}


def build_text_preprocessor(locale: str) -> TextPreprocessor:
    builder = _TEXT_PREPROCESSOR_BUILDERS.get(locale)
    return builder() if builder is not None else TextPreprocessor()


def create_engine(settings: Settings) -> SileroTTSEngine:
    torch.set_num_threads(settings.torch.num_threads)
    torch.set_num_interop_threads(settings.torch.num_interop_threads)
    if settings.torch.flush_denormal and hasattr(torch, "set_flush_denormal"):
        torch.set_flush_denormal(True)

    config = TTSConfig(
        device=settings.torch.device,
        sample_rate=settings.tts.sample_rate,
        max_models=settings.tts.max_models,
        max_concurrent_per_model=settings.tts.max_concurrent_per_model,
        max_chunk_chars=settings.tts.max_chunk_chars,
        models_dir=settings.tts.models_dir,
        models_yml_url=settings.tts.models_yml_url,
        models_yml_hash=settings.tts.models_yml_hash,
    )
    storage = SileroTTSYamlConfigStorage(settings.tts.models_config_path)
    return SileroTTSEngine(
        config=config,
        storage=storage,
        text_preprocessor_factory=build_text_preprocessor,
    )


async def main():
    settings = get_settings()
    logger.debug(settings)

    server = AsyncServer.from_uri(settings.uri)

    if settings.zeroconf:
        if not isinstance(server, AsyncTcpServer):
            raise ValueError("Zeroconf requires tcp:// uri")

        from wyoming.zeroconf import HomeAssistantZeroconf

        tcp_server: AsyncTcpServer = server
        hass_zeroconf = HomeAssistantZeroconf(
            name=settings.zeroconf,
            port=tcp_server.port,
            host=tcp_server.host,
        )
        await hass_zeroconf.register_server()
        logger.debug("Zeroconf discovery enabled")

    engine = create_engine(settings)

    await engine.warmup()

    logger.info(f"Starting server on {settings.uri}")
    server_task = asyncio.create_task(
        server.run(
            partial(
                SileroWyomingHandler,
                engine,
                settings.streaming,
                settings.env_type == "development",
            )
        )
    )

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, server_task.cancel)
    loop.add_signal_handler(signal.SIGTERM, server_task.cancel)

    try:
        await server_task
    except asyncio.CancelledError:
        logger.info("Server stopped")
    finally:
        await engine.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
