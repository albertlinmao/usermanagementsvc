from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from core.security import verify_gateway_psk


class TenantContext(BaseModel):
    user_id: str
    tenant_id: str
    trace_id: Optional[str] = None


def get_tenant_context(
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    x_trace_id: Optional[str] = Header(None, alias="X-Trace-Id"),
    _=Depends(verify_gateway_psk),
) -> TenantContext:
    """
    Extracts the validated user and tenant identity from the Edge Gateway headers.
    """
    if not x_user_id or not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required identity headers.",
        )

    return TenantContext(user_id=x_user_id, tenant_id=x_tenant_id, trace_id=x_trace_id)
