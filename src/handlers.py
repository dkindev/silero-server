from fastapi.responses import JSONResponse


async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
