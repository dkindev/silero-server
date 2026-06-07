import traceback
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import get_settings


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        with logger.contextualize(request_id=req_id):
            try:
                response = await call_next(request)
                response.headers["X-Request-ID"] = req_id
                return response

            except Exception as exc:
                logger.exception(f"Unhandled exception during {request.method} {request.url.path}")

                content = {
                    "request_id": req_id,
                }

                if get_settings().TTS_ENV_TYPE == "development":
                    content["detail"] = str(exc)
                    content["exceptionType"] = (exc.__class__.__name__,)
                    content["traceback"] = "".join(
                        traceback.format_exception(type(exc), exc, exc.__traceback__)
                    )
                else:
                    content["detail"] = "Internal Server Error"

                return JSONResponse(
                    status_code=500,
                    content=content,
                    headers={"X-Request-ID": req_id},
                )


def add_global_exception_handler(app: FastAPI):
    app.add_middleware(GlobalExceptionMiddleware)


def add_cors(app: FastAPI):
    app_settings = get_settings()
    allowed_origins = app_settings.TTS_ALLOWED_ORIGINS
    origins = ["*"] if allowed_origins == "*" else allowed_origins.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
