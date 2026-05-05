from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.session import get_db
from api.deps import get_tenant_context, TenantContext
from models.rbac_schemas import RoleCreate, RoleResponse
from services.rbac_service import RBACService

router = APIRouter()

@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db)
):
    """Get all roles for the current tenant"""
    service = RBACService(session)
    return await service.get_roles(context.tenant_id)

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db)
):
    """Create a new role for the current tenant"""
    service = RBACService(session)
    try:
        return await service.create_role(context.tenant_id, role_in)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
