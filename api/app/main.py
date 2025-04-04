import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from app.endpoints.schedule_tune_endpoint import schedule_tune_router
from app.endpoints.auth_endpoint import auth_router
from app.endpoints.instant_tune_endpoint import instant_upload_router
from app.endpoints.user_mgmt_endpoint import user_mgmt_router
from app.endpoints.health_endpoint import health_router
from app.auth_dependencies import custom_openapi
from app.jobs.tune_upload_job import start_scheduler
from app.logger.logging_setup import logger
from app.settings.env_settings import KILL_SWITCH_ENABLED, MAINTENANCE_MODE_ENABLED, CORS_ORIGINS
from app.utils.http_response_util import (
    not_found_handler,
    forbidden_handler,
    unauthorized_handler,
    bad_request_handler,
    internal_server_error_handler
)

# Log application initialization
logger.debug("Initializing the application...")

if KILL_SWITCH_ENABLED:
    log_message = (
    "\n" + "="*50 + "\n"
    "KILL SWITCH ENABLED. APPLICATION WILL NOT START.\n"
    + "="*50 + "\n"
)

    print(log_message)
    logger.critical(log_message)
    sys.exit(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("Application has started.")
    start_scheduler()
    yield
    logger.debug("Application is stopping.")

# Create FastAPI app instance
app = FastAPI(
    docs_url="/api/docs",       # Swagger UI
    redoc_url="/api/redoc",     # Optional: ReDoc UI
    openapi_url="/api/openapi.json",  # OpenAPI schema
    lifespan=lifespan
)

# Store the original app.openapi method before overriding
app._original_openapi = app.openapi

# Override the app.openapi with the custom_openapi function
app.openapi = lambda: custom_openapi(app)

origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

if origins:
    logger.debug(f"Loading CORS origins: {origins}")
else:
    logger.warning("No valid CORS origins were loaded from CORS_ORIGINS!")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.middleware("http")
async def maintenance_mode_middleware(request: Request, call_next):
    if MAINTENANCE_MODE_ENABLED and not request.url.path.startswith("/health"):
        logger.debug("Maintenance mode is enabled. Returning 503 Service Unavailable.")
        return JSONResponse(
            status_code=503,
            content={"detail": "Service is temporarily unavailable due to maintenance. Please try again later."},
        )
    return await call_next(request)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    if request.url.path.startswith("/api/auth/google/callback"):
        logger.debug("Skipping security headers for Google OAuth callback route.")
    else:
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        logger.debug("Security headers applied: COOP + COEP")

    return response

# Create a root API router with prefix "/api"
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(schedule_tune_router, prefix="/scheduled-tune", tags=["scheduled-tune"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(instant_upload_router, prefix="/instant-tune", tags=["instant-tune"])
api_router.include_router(user_mgmt_router, prefix="/user-mgmt", tags=["user-mgmt"])
api_router.include_router(health_router, prefix="/health", tags=["Health"])

# Mount the API router
app.include_router(api_router)

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)