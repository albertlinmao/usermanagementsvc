from supabase import create_client, Client
from core.config import settings
from models.schemas import TenantRegistrationRequest, TenantResponse
from services.tenant_repo import TenantRepository
from sqlalchemy.ext.asyncio import AsyncSession


from uuid import UUID


class OnboardingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        # Use Service Role to bypass RLS during onboarding logic
        print(f"DEBUG: URL={settings.SUPABASE_URL} KEY={settings.SUPABASE_KEY[:10]}...")
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def register_tenant(
        self, request: TenantRegistrationRequest
    ) -> TenantResponse:
        repo = TenantRepository(self.session)

        # We start a transaction block for safety. If auth creation fails, no DB changes occur.
        async with self.session.begin():
            # 1. Create User in Supabase Auth via Service Role API
            try:
                auth_res = self.supabase.auth.admin.create_user(
                    {
                        "email": request.admin_email,
                        "password": request.admin_password,
                        "email_confirm": True,
                    }
                )
                user_id = UUID(auth_res.user.id)
            except Exception as e:
                # Handle auth user creation failure (e.g. user already exists)
                raise ValueError(f"Failed to create user in Auth: {str(e)}")

            # 2. Create Tenant in DB
            tenant_id = await repo.create_tenant(request.tenant_name)

            # 3. Inject tenant_id into app_metadata (Critical for Edge Gateway security boundary)
            self.supabase.auth.admin.update_user_by_id(
                str(user_id), {"app_metadata": {"tenant_id": str(tenant_id)}}
            )

            # 4. Create UserProfile in DB (PII encrypted)
            await repo.create_user_profile(
                user_id,
                request.admin_email,
                request.admin_first_name,
                request.admin_last_name,
            )

            # 5. Create Admin Role & Membership
            await repo.create_membership(tenant_id, user_id, "Admin")

        return TenantResponse(
            id=tenant_id,
            name=request.tenant_name,
            status="ACTIVE",
            admin_user_id=user_id,
        )

    async def get_tenant(self, tenant_id: UUID) -> TenantResponse:
        repo = TenantRepository(self.session)
        tenant_data = await repo.get_tenant(tenant_id)
        if not tenant_data:
            raise ValueError(f"Tenant not found: {tenant_id}")
            
        return TenantResponse(
            id=tenant_data["id"],
            name=tenant_data["name"],
            status=tenant_data["status"]
        )
