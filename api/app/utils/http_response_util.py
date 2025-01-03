"""
http_response.py

This module provides utilities for creating standardized HTTP responses for FastAPI applications. 
It includes functions to generate JSON responses with consistent structure, 
supporting any JSON-serializable data,
as well as centralized exception handling.
"""

from typing import Any
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request

def create_response(status_code: int, title: str, message: str, data: Any = None) -> JSONResponse:
    """
    Creates a standardized JSON response using Pydantic's jsonable_encoder.

    Args:
    - status_code (int): HTTP status code (e.g., 200, 404).
    - message (str): A descriptive message for the response.
    - data (Any): Response data, which can be any JSON-serializable object.

    Returns:
    - JSONResponse: A standardized JSON response.
    """
    response_content = {
        "title": title,  # Title field to reflect error basis
        "message": message,  # Message for user-facing context
        "data": jsonable_encoder(data) if data is not None else None,  # Attach data if present
    }
    return JSONResponse(status_code=status_code, content=response_content)


# Exception Handlers

def not_found_handler(request: Request, exc: HTTPException):
    """
    Handles 404 errors (Resource not found).
    """
    return create_response(404, "Resource not found", exc.detail, {"path": str(request.url)})

def forbidden_handler(request: Request, exc: HTTPException):
    """
    Handles 403 errors (Forbidden access).
    """
    return create_response(403, "Access forbidden", exc.detail, {"path": str(request.url)})

def unauthorized_handler(request: Request, exc: HTTPException):
    """
    Handles 401 errors (Unauthorized access).
    """
    return create_response(401, "Unauthorized access", exc.detail, {"path": str(request.url)})

def bad_request_handler(request: Request, exc: HTTPException):
    """
    Handles 400 errors (Bad request).
    """
    return create_response(400, "Bad request", exc.detail, {"path": str(request.url)})

def internal_server_error_handler(request: Request, exc: HTTPException):
    """
    Handles 500 errors (Internal server error).
    """
    return create_response(500, "Internal server error occurred", exc.detail, {"path": str(request.url)})

# Response Interceptors for Specific 2xx (Success) Status Codes

def response_200(title:str, message: str, data: Any = None) -> JSONResponse:
    """
    Creates a response for 200 OK status code.
    
    Args:
    - message (str): A descriptive message for the response.
    - data (Any): Optional response data.

    Returns:
    - JSONResponse: A standardized 200 OK response.
    """
    return create_response(200, title, message, data)

def response_201(title: str, message: str, data: Any = None) -> JSONResponse:
    """
    Creates a response for 201 Created status code.
    
    Args:
    - message (str): A descriptive message for the response.
    - data (Any): Optional response data.

    Returns:
    - JSONResponse: A standardized 201 Created response.
    """
    return create_response(201, title, message, data)

def response_202(message: str, data: Any = None) -> JSONResponse:
    """
    Creates a response for 202 Accepted status code.
    
    Args:
    - message (str): A descriptive message for the response.
    - data (Any): Optional response data.

    Returns:
    - JSONResponse: A standardized 202 Accepted response.
    """
    return create_response(202, message, data)

def response_204(message: str) -> JSONResponse:
    """
    Creates a response for 204 No Content status code.
    
    Args:
    - message (str): A descriptive message for the response.
    - data (Any): Optional response data.

    Returns:
    - JSONResponse: A standardized 204 No Content response.
    """
    response_content = {
        "title": message,
        "status_code": "204",
        "message": message,
        "data": None  # No content for 204
    }
    return JSONResponse(status_code=204, content=response_content)
