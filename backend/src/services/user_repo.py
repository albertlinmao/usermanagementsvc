from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from typing import Optional, Dict, Any


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(
        self, cursor: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
        # Using pagination with offset/limit for simplicity, or we can use cursor based.
        # Let's assume cursor is an offset for simplicity if it's digit, otherwise 0
        offset = int(cursor) if cursor and cursor.isdigit() else 0

        stmt = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            SELECT 
                u.id, 
                pgp_sym_decrypt(u.email::bytea, secret.decrypted_secret) as email,
                pgp_sym_decrypt(u.first_name::bytea, secret.decrypted_secret) as first_name,
                pgp_sym_decrypt(u.last_name::bytea, secret.decrypted_secret) as last_name,
                u.status,
                u.created_at,
                u.updated_at
            FROM public.user_profile u, secret
            WHERE u.status != 'SOFT_DELETED'
            ORDER BY u.created_at DESC
            LIMIT :limit OFFSET :offset
        """)

        count_stmt = text("""
            SELECT count(*) 
            FROM public.user_profile u 
            WHERE u.status != 'SOFT_DELETED'
        """)

        result = await self.session.execute(stmt, {"limit": limit, "offset": offset})
        rows = result.fetchall()

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar() or 0

        data = []
        for row in rows:
            data.append(
                {
                    "id": str(row.id),
                    "email": row.email,
                    "first_name": row.first_name,
                    "last_name": row.last_name,
                    "status": row.status,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                }
            )

        has_more = (offset + limit) < total_count
        next_cursor = str(offset + limit) if has_more else None

        return {"data": data, "next_cursor": next_cursor, "has_more": has_more}

    async def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        stmt = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            SELECT 
                u.id, 
                pgp_sym_decrypt(u.email::bytea, secret.decrypted_secret) as email,
                pgp_sym_decrypt(u.first_name::bytea, secret.decrypted_secret) as first_name,
                pgp_sym_decrypt(u.last_name::bytea, secret.decrypted_secret) as last_name,
                u.status,
                u.created_at,
                u.updated_at
            FROM public.user_profile u, secret
            WHERE u.id = :user_id AND u.status != 'SOFT_DELETED'
        """)

        result = await self.session.execute(stmt, {"user_id": str(user_id)})
        row = result.fetchone()

        if not row:
            return None

        return {
            "id": str(row.id),
            "email": row.email,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    async def create_user(
        self,
        user_id: UUID,
        email: str,
        first_name: str,
        last_name: str,
        status: str = "ACTIVE",
    ) -> Dict[str, Any]:
        stmt = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            INSERT INTO public.user_profile (id, email, first_name, last_name, status, created_at, updated_at)
            SELECT 
                :user_id,
                pgp_sym_encrypt(:email, secret.decrypted_secret),
                pgp_sym_encrypt(:first_name, secret.decrypted_secret),
                pgp_sym_encrypt(:last_name, secret.decrypted_secret),
                :status,
                NOW(),
                NOW()
            FROM secret
            RETURNING id, status, created_at, updated_at
        """)

        result = await self.session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "status": status,
            },
        )
        row = result.fetchone()
        if not row:
            raise Exception("Failed to create user")
        return {
            "id": str(row.id),
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "status": row.status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }

    async def update_user(
        self, user_id: UUID, update_data: dict
    ) -> Optional[Dict[str, Any]]:
        # Fetch current user first
        current_user = await self.get_user(user_id)
        if not current_user:
            return None

        # Build update query dynamically
        updates = []
        params = {"user_id": str(user_id)}

        if "first_name" in update_data:
            updates.append(
                "first_name = pgp_sym_encrypt(:first_name, secret.decrypted_secret)"
            )
            params["first_name"] = update_data["first_name"]

        if "last_name" in update_data:
            updates.append(
                "last_name = pgp_sym_encrypt(:last_name, secret.decrypted_secret)"
            )
            params["last_name"] = update_data["last_name"]

        if "status" in update_data:
            updates.append("status = :status")
            params["status"] = update_data["status"]

        if not updates:
            return current_user

        updates.append("updated_at = NOW()")

        update_str = ", ".join(updates)

        stmt = text(f"""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            UPDATE public.user_profile
            SET {update_str}
            FROM secret
            WHERE public.user_profile.id = :user_id AND public.user_profile.status != 'SOFT_DELETED'
            RETURNING public.user_profile.id
        """)

        await self.session.execute(stmt, params)

        # Return updated user
        return await self.get_user(user_id)

    async def delete_user(self, user_id: UUID) -> bool:
        stmt = text("""
            UPDATE public.user_profile
            SET status = 'SOFT_DELETED', deleted_at = NOW(), updated_at = NOW()
            WHERE id = :user_id AND status != 'SOFT_DELETED'
        """)

        result = await self.session.execute(stmt, {"user_id": str(user_id)})
        return getattr(result, "rowcount", 0) > 0
