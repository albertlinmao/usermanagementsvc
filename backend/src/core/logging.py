import logging
import json
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


# Set up basic structured JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "trace_id": getattr(record, "trace_id", None),
            "tenant_id": getattr(record, "tenant_id", None),
            "user_id": getattr(record, "user_id", None),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


logger = logging.getLogger("user-management-api")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = request.headers.get("X-Trace-Id", "unknown")
        tenant_id = request.headers.get("X-Tenant-Id", "unknown")
        user_id = request.headers.get("X-User-Id", "unknown")

        # Attach to request state for downstream use
        request.state.trace_id = trace_id

        # We could use ContextVars here for deep integration, but for now we'll rely on explicitly passing it.
        # Alternatively, we could inject a custom logger adapter here.

        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
