import logging
import sys

from loguru import logger

from src.config import get_settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    IS_PRODUCTION = get_settings().TTS_ENV_TYPE == "production"

    logger.remove()
    logger.configure(extra={"request_id": "-"})

    dev_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "ReqID: <cyan>{extra[request_id]}</cyan> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    prod_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {name}:{function} | {message}"
    )

    logger.add(
        sys.stderr,
        colorize=not IS_PRODUCTION,
        format=prod_format if IS_PRODUCTION else dev_format,
        backtrace=not IS_PRODUCTION,  # Trims noise from library internals in prod
        diagnose=not IS_PRODUCTION,  # Prevents variable value leaking in prod
        level="INFO" if IS_PRODUCTION else "DEBUG",
    )

    if IS_PRODUCTION:
        logger.add(
            "logs/app.log",
            level="DEBUG",
            rotation="10 MB",
            retention="1 month",
            compression="zip",
            serialize=True,
            enqueue=True,
        )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith(("uvicorn", "torch", "fastapi"))
    )

    for module_logger in loggers:
        module_logger.handlers = []
        module_logger.propagate = True
