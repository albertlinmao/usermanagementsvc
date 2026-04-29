from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from core.logging import logger


from typing import Optional


class APIError(Exception):
    """Base API Error class"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[dict] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


async def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", "unknown")

    if isinstance(exc, APIError):
        status_code = exc.status_code
        error_payload = {
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "trace_id": trace_id,
        }
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        error_payload = {
            "code": "HTTP_EXCEPTION",
            "message": exc.detail,
            "details": {},
            "trace_id": trace_id,
        }
    else:
        # Unhandled generic exception
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            extra={"trace_id": trace_id, "path": request.url.path},
        )
        error_payload = {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "details": {},
            "trace_id": trace_id,
        }

    return JSONResponse(status_code=status_code, content={"error": error_payload})
