import asyncio
import signal
from functools import partial

import torch
from loguru import logger
from openai import AsyncOpenAI
from wyoming.server import AsyncServer, AsyncTcpServer

from src.config import Settings, get_settings
from src.handler import SileroEventHandler
from src.logger import setup_logging
from src.tts.config_storage import SileroTTSConfigStorage, SileroTTSYamlConfigStorage
from src.tts.engine import SileroTTSEngine
from src.tts.models import TTSConfig
from src.tts.preprocessing import TextNormalizerFactory, TextSentenizerFactory

setup_logging()


def create_storage(settings: Settings) -> SileroTTSConfigStorage:
    return SileroTTSYamlConfigStorage(settings.tts.data_yml_path)


def create_text_sentenizer_factory() -> TextSentenizerFactory:
    return TextSentenizerFactory()


def create_text_normalizer_factory(
    openai_client: AsyncOpenAI, settings: Settings, storage: SileroTTSConfigStorage
) -> TextNormalizerFactory:
    return TextNormalizerFactory(
        openai_client=openai_client,
        settings=settings.tts.normalization,
        storage=storage,
    )


def create_engine(
    settings: Settings,
    storage: SileroTTSConfigStorage,
    text_sentenizer_factory: TextSentenizerFactory,
    text_normalizer_factory: TextNormalizerFactory,
) -> SileroTTSEngine:
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

    return SileroTTSEngine(
        config=config,
        storage=storage,
        text_sentenizer_factory=text_sentenizer_factory,
        text_normalizer_factory=text_normalizer_factory,
    )


def create_openai_client(settings: Settings) -> AsyncOpenAI:
    config = settings.open_ai
    if config is None:
        return None

    if not config.base_url or not config.api_key:
        return None

    openai_client = AsyncOpenAI(
        base_url=settings.open_ai.base_url,
        api_key=settings.open_ai.api_key,
    )

    return openai_client


async def register_zeroconf_server(name: str, for_server: AsyncServer):
    if not isinstance(for_server, AsyncTcpServer):
        raise ValueError("Zeroconf requires tcp:// uri")

    from wyoming.zeroconf import HomeAssistantZeroconf

    tcp_server: AsyncTcpServer = for_server
    hass_zeroconf = HomeAssistantZeroconf(
        name=name,
        port=tcp_server.port,
        host=tcp_server.host,
    )
    await hass_zeroconf.register_server()
    logger.debug("Zeroconf discovery enabled")


async def main():
    settings = get_settings()
    logger.debug(settings)

    server = AsyncServer.from_uri(settings.uri)

    if settings.zeroconf:
        await register_zeroconf_server(settings.zeroconf, server)

    openai_client = create_openai_client(settings)

    storage = create_storage(settings)
    text_sentenizer_factory = create_text_sentenizer_factory()
    text_normalizer_factory = create_text_normalizer_factory(openai_client, settings, storage)
    engine = create_engine(settings, storage, text_sentenizer_factory, text_normalizer_factory)

    await engine.warmup()

    logger.info(f"Starting server on {settings.uri}")
    server_task = asyncio.create_task(
        server.run(
            partial(
                SileroEventHandler,
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

        if openai_client is not None:
            await openai_client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
