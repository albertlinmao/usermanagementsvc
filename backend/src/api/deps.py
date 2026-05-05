from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from core.security import verify_gateway_psk
from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

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


class RequirePermissions:
    def __init__(self, resource: str, action: str):
        self.resource = resource
        self.action = action
        
    async def __call__(
        self,
        context: TenantContext = Depends(get_tenant_context),
        session: AsyncSession = Depends(get_db)
    ) -> TenantContext:
        from services.rbac_repo import RBACRepository
        
        repo = RBACRepository(session)
        user_perms = await repo.get_user_permissions(UUID(context.tenant_id), UUID(context.user_id))
        
        has_perm = any(
            p["resource"] == self.resource and p["action"] == self.action
            for p in user_perms
        )
        
        if not has_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.resource}:{self.action}"
            )
            
        return context
