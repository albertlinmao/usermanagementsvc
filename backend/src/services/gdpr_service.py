from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from supabase import create_client, Client
import uuid
from core.config import settings


class GdprService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.supabase: Client = create_client(
            # pyrefly: ignore [missing-attribute]
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )

    async def hard_delete_user(self, user_id: str) -> bool:
        """
        Perform a GDPR hard delete of a user.
        Replaces PII fields with anonymized stubs but retains the internal UUID
        to maintain Audit Log structural integrity.
        """
        # First verify user exists
        stmt_check = text("SELECT id FROM public.user_profile WHERE id = :user_id")
        result = await self.session.execute(stmt_check, {"user_id": user_id})
        user = result.fetchone()

        if not user:
            return False

        # Generate anonymized data
        anon_email = f"deleted-{uuid.uuid4()}@redacted.local"

        try:
            # Update auth.users to prevent login and remove real email
            # pyrefly: ignore [missing-argument]
            self.supabase.auth.admin.update_user_by_id(
                user_id,
                {
                    "email": anon_email,
                    "password": str(uuid.uuid4()) * 2,  # Random unguessable password
                    "user_metadata": {"deleted": True},
                },
            )
        except Exception as e:
            print(f"Failed to update auth.users: {e}")
            # Proceed to scrub our DB anyway

        # We must overwrite the encrypted PII in public.user_profile
        # We need the vault secret to encrypt the stubs
        stmt_update = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            UPDATE public.user_profile
            SET 
                email = pgp_sym_encrypt(:anon_email, secret.decrypted_secret),
                first_name = pgp_sym_encrypt('[REDACTED_PII]', secret.decrypted_secret),
                last_name = pgp_sym_encrypt('[REDACTED_PII]', secret.decrypted_secret),
                middle_name = NULL,
                status = 'SOFT_DELETED',
                deleted_at = NOW()
            FROM secret
            WHERE id = :user_id
        """)

        await self.session.execute(
            stmt_update, {"anon_email": anon_email, "user_id": user_id}
        )
        await self.session.commit()

        return True
