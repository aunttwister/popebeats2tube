from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from app.endpoints.schedule_tune_endpoint import schedule_tune_router
from app.endpoints.config_mgmt_endpoint import config_mgmt_router
from app.endpoints.auth_endpoint import auth_router
from app.endpoints.instant_tune_endpoint import instant_upload_router
from app.endpoints.user_mgmt_endpoint import user_mgmt_router
from app.auth_dependencies import custom_openapi
from app.services.config_mgmt_service import load_config
from app.logging.logging_setup import logger
from app.utils.http_response_util import (
    not_found_handler,
    forbidden_handler,
    unauthorized_handler,
    bad_request_handler,
    internal_server_error_handler
)

# Log application initialization
logger.debug("Initializing the application...")

# Load configuration during startup
CONFIG = load_config()

# Create FastAPI app instance
app = FastAPI()

# Store the original app.openapi method before overriding
app._original_openapi = app.openapi

# Override the app.openapi with the custom_openapi function
app.openapi = lambda: custom_openapi(app)

origins = [
    "http://localhost:3000",  # Your React frontend
    "http://127.0.0.1:3000",  # Alternative localhost format
    # Add more origins as needed
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies to be included
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response

# Create a root API router with prefix "/api"
api_router = APIRouter(prefix="/api")

# Include routers
api_router.include_router(schedule_tune_router, prefix="/scheduled-tune", tags=["scheduled-tune"])
api_router.include_router(config_mgmt_router, prefix="/config-management", tags=["config-management"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(instant_upload_router, prefix="/instant-tune", tags=["instant-tune"])
api_router.include_router(user_mgmt_router, prefix="/user-mgmt", tags=["user-mgmt"])

# Mount the API router
app.include_router(api_router)

# Register exception handlers
app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(403, forbidden_handler)
app.add_exception_handler(401, unauthorized_handler)
app.add_exception_handler(400, bad_request_handler)
app.add_exception_handler(500, internal_server_error_handler)

# Add startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    logger.debug("Application has started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.debug("Application is stopping.")
