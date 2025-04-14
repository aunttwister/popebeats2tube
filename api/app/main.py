import sys
from fastapi import FastAPI, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from app.components.tune_ops.tune_ops_endpoint import tune_ops_router
from app.components.auth.google_oauth.google_oauth_endpoint import google_oauth_router
from app.components.user_mgmt.user_mgmt_endpoint import user_mgmt_router
from app.components.system_health.system_health_endpoint import system_health_router
from app.auth_dependencies import custom_openapi
from app.jobs.tune_upload_job import start_scheduler
from app.logger.logging_setup import logger
from app.settings.env_settings import KILL_SWITCH_ENABLED, MAINTENANCE_MODE_ENABLED, CORS_ORIGINS, GOOGLE_OAUTH_REDIRECT_URI_PATH
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

    if request.url.path.startswith(GOOGLE_OAUTH_REDIRECT_URI_PATH):
        logger.debug("Skipping security headers for Google OAuth callback route.")
    else:
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        logger.debug("Security headers applied: COOP + COEP")

    return response

# Create a root API router with prefix "/api"
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(tune_ops_router, prefix="/tune-ops", tags=["Tune Operations"])
api_router.include_router(google_oauth_router, prefix="/google-oauth", tags=["Google OAuth 2.0"])
api_router.include_router(user_mgmt_router, prefix="/user-mgmt", tags=["User Management"])
api_router.include_router(system_health_router, prefix="/system-health", tags=["System Health"])

# Mount the API router
app.include_router(api_router)

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)