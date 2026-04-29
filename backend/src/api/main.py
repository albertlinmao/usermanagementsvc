from fastapi import FastAPI, HTTPException
from api.routers.tenants import router as tenants_router
from core.logging import TraceIdMiddleware
from core.idempotency import IdempotencyMiddleware
from core.exceptions import custom_exception_handler, APIError

app = FastAPI(title="Multi-Tenant User API", version="0.1.0")

# Middlewares
app.add_middleware(TraceIdMiddleware)
app.add_middleware(IdempotencyMiddleware)

# Exception Handlers
app.add_exception_handler(Exception, custom_exception_handler)
app.add_exception_handler(APIError, custom_exception_handler)
app.add_exception_handler(HTTPException, custom_exception_handler)

# Routers
app.include_router(tenants_router, prefix="/api/v1/tenants", tags=["Tenants"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
