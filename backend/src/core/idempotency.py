from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# A simple in-memory store for idempotency keys.
# In a real distributed system, use Redis or Postgres.
_idempotency_store = {}


class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        idempotency_key = request.headers.get("Idempotency-Key")

        # Only POST, PUT, DELETE requests should be idempotent
        if request.method in ["POST", "PUT", "DELETE", "PATCH"] and idempotency_key:
            # Note: Storing entire responses in memory here is just a stub!
            if idempotency_key in _idempotency_store:
                # Return the cached response
                return _idempotency_store[idempotency_key]

            response = await call_next(request)

            # Cache successful state-changing responses
            if 200 <= response.status_code < 300:
                _idempotency_store[idempotency_key] = response

            return response

        return await call_next(request)
