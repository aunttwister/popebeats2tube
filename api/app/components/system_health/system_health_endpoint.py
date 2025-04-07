from fastapi import APIRouter
from fastapi.responses import JSONResponse

system_health_router = APIRouter()

@system_health_router.get("")
async def health_check():
    """
    Basic liveness check endpoint.
    Returns 200 OK if app is running.
    """
    return JSONResponse(status_code=200, content={"status": "ok"})