import asyncio
from core.config import settings
from supabase import create_client


async def main():
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    try:
        res = supabase.auth.admin.create_user(
            {
                "email": "test456@example.com",
                "password": "password123",
                "email_confirm": True,
            }
        )
        print(res)
    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    asyncio.run(main())
