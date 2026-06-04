from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.api_route("/health", methods=["GET", "HEAD"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
