from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import List, Dict, Any

class RBACRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_roles(self, tenant_id: UUID) -> List[Dict[str, Any]]:
        # Get roles and their permissions for a tenant
        stmt = text("""
            SELECT r.id as role_id, r.name as role_name, r.tenant_id,
                   p.id as perm_id, p.resource, p.action
            FROM public.role r
            LEFT JOIN public.role_permission rp ON r.id = rp.role_id
            LEFT JOIN public.permission p ON rp.permission_id = p.id
            WHERE r.tenant_id = :tenant_id OR r.tenant_id IS NULL
        """)
        result = await self.session.execute(stmt, {"tenant_id": str(tenant_id)})
        rows = result.fetchall()
        
        roles = {}
        for row in rows:
            r_id = row.role_id
            if r_id not in roles:
                roles[r_id] = {
                    "id": r_id,
                    "tenant_id": row.tenant_id,
                    "name": row.role_name,
                    "permissions": []
                }
            if row.perm_id:
                roles[r_id]["permissions"].append({
                    "id": row.perm_id,
                    "resource": row.resource,
                    "action": row.action
                })
                
        return list(roles.values())

    async def create_role(self, tenant_id: UUID, name: str) -> UUID:
        stmt = text("""
            INSERT INTO public.role (tenant_id, name)
            VALUES (:tenant_id, :name)
            RETURNING id
        """)
        result = await self.session.execute(stmt, {"tenant_id": str(tenant_id), "name": name})
        return result.scalar_one()

    async def get_or_create_permission(self, resource: str, action: str) -> UUID:
        # Check if exists
        check_stmt = text("SELECT id FROM public.permission WHERE resource = :resource AND action = :action")
        result = await self.session.execute(check_stmt, {"resource": resource, "action": action})
        existing = result.scalar_one_or_none()
        if existing:
            return existing
            
        # Create new
        insert_stmt = text("""
            INSERT INTO public.permission (resource, action)
            VALUES (:resource, :action)
            ON CONFLICT (resource, action) DO UPDATE SET resource = EXCLUDED.resource
            RETURNING id
        """)
        result = await self.session.execute(insert_stmt, {"resource": resource, "action": action})
        return result.scalar_one()

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> None:
        stmt = text("""
            INSERT INTO public.role_permission (role_id, permission_id)
            VALUES (:role_id, :permission_id)
            ON CONFLICT DO NOTHING
        """)
        await self.session.execute(stmt, {"role_id": str(role_id), "permission_id": str(permission_id)})
        
    async def get_user_permissions(self, tenant_id: UUID, user_id: UUID) -> List[Dict[str, Any]]:
        stmt = text("""
            SELECT p.resource, p.action
            FROM public.membership m
            JOIN public.role r ON m.role_id = r.id
            JOIN public.role_permission rp ON r.id = rp.role_id
            JOIN public.permission p ON rp.permission_id = p.id
            WHERE m.tenant_id = :tenant_id AND m.user_id = :user_id
        """)
        result = await self.session.execute(stmt, {"tenant_id": str(tenant_id), "user_id": str(user_id)})
        rows = result.fetchall()
        return [{"resource": row.resource, "action": row.action} for row in rows]
