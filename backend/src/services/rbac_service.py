from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List
from models.rbac_schemas import RoleCreate, RoleResponse, PermissionResponse
from services.rbac_repo import RBACRepository

class RBACService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RBACRepository(session)
        
    async def get_roles(self, tenant_id: str) -> List[RoleResponse]:
        roles_data = await self.repo.get_roles(UUID(tenant_id))
        return [RoleResponse(**data) for data in roles_data]
        
    async def create_role(self, tenant_id: str, role_create: RoleCreate) -> RoleResponse:
        t_id = UUID(tenant_id)
        
        async with self.session.begin():
            # Create role
            role_id = await self.repo.create_role(t_id, role_create.name)
            
            # Map permissions
            assigned_perms = []
            for perm in role_create.permissions:
                perm_id = await self.repo.get_or_create_permission(perm.resource, perm.action)
                await self.repo.assign_permission_to_role(role_id, perm_id)
                assigned_perms.append(PermissionResponse(
                    id=perm_id,
                    resource=perm.resource,
                    action=perm.action
                ))
                
        return RoleResponse(
            id=role_id,
            tenant_id=t_id,
            name=role_create.name,
            permissions=assigned_perms
        )
