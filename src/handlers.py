from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings


def add_global_exception_handler(app: FastAPI):
    async def global_exception_handler(request, exc):
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    app.add_exception_handler(Exception, global_exception_handler)


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
