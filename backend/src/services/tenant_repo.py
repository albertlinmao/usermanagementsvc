from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID


class TenantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_tenant(self, name: str) -> UUID:
        stmt = text("""
            INSERT INTO public.tenant (name) 
            VALUES (:name) 
            RETURNING id
        """)
        result = await self.session.execute(stmt, {"name": name})
        tenant_id = result.scalar_one()
        return tenant_id

    async def create_user_profile(
        self, user_id: UUID, email: str, first_name: str, last_name: str
    ) -> None:
        # PII fields are encrypted via pgp_sym_encrypt with a key from Vault (assuming key 'pii_encryption_key' exists in vault)
        # Note: Depending on your exact vault setup, you might need to fetch the key dynamically.
        # For simplicity in this SQL, we use a placeholder or read the decrypted secret.

        # In a real setup, we might do:
        # pgcrypto encrypts the data using the secret
        stmt = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            INSERT INTO public.user_profile (id, email, first_name, last_name, status)
            SELECT 
                :user_id,
                pgp_sym_encrypt(:email, secret.decrypted_secret),
                pgp_sym_encrypt(:first_name, secret.decrypted_secret),
                pgp_sym_encrypt(:last_name, secret.decrypted_secret),
                'ACTIVE'
            FROM secret
        """)

        await self.session.execute(
            stmt,
            {
                "user_id": str(user_id),
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

    async def create_membership(
        self, tenant_id: UUID, user_id: UUID, role_name: str
    ) -> None:
        # 1. Ensure the system role exists or create it
        role_stmt = text("""
            INSERT INTO public.role (tenant_id, name)
            VALUES (:tenant_id, :role_name)
            ON CONFLICT (tenant_id, name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """)
        role_result = await self.session.execute(
            role_stmt, {"tenant_id": str(tenant_id), "role_name": role_name}
        )
        role_id = role_result.scalar_one()

        # 2. Assign membership
        membership_stmt = text("""
            INSERT INTO public.membership (tenant_id, user_id, role_id)
            VALUES (:tenant_id, :user_id, :role_id)
        """)
        await self.session.execute(
            membership_stmt,
            {
                "tenant_id": str(tenant_id),
                "user_id": str(user_id),
                "role_id": str(role_id),
            },
        )

    async def get_tenant(self, tenant_id: UUID) -> dict:
        stmt = text("""
            SELECT id, name, status 
            FROM public.tenant 
            WHERE id = :tenant_id
        """)
        result = await self.session.execute(stmt, {"tenant_id": str(tenant_id)})
        row = result.fetchone()
        if not row:
            return None
        return {
            "id": row.id,
            "name": row.name,
            "status": row.status
        }
