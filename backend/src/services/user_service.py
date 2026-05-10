from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from supabase import create_client, Client
from core.config import settings
from models.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserProfileResponse,
    PaginatedUserResponse,
)
from services.user_repo import UserRepository


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(session)
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def get_users(
        self, cursor: Optional[str] = None, limit: int = 50
    ) -> PaginatedUserResponse:
        data = await self.repo.get_users(cursor, limit)
        users = [UserProfileResponse(**row) for row in data["data"]]
        return PaginatedUserResponse(
            data=users, next_cursor=data["next_cursor"], has_more=data["has_more"]
        )

    async def get_user(self, user_id: str) -> Optional[UserProfileResponse]:
        data = await self.repo.get_user(UUID(user_id))
        if not data:
            return None
        return UserProfileResponse(**data)

    async def create_user(self, create_data: UserCreateRequest) -> UserProfileResponse:
        import uuid
        from fastapi import HTTPException, status

        # First, register the user in Supabase Auth via Admin API
        temp_password = str(uuid.uuid4())
        try:
            auth_res = self.supabase.auth.admin.create_user(
                {
                    "email": create_data.email,
                    "password": temp_password,
                    "email_confirm": True,
                }
            )
            user_id = UUID(auth_res.user.id)
        except Exception as e:
            # If user already exists in auth or other error occurs
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create user in Auth: {str(e)}",
            )

        async with self.session.begin():
            data = await self.repo.create_user(
                user_id=user_id,
                email=create_data.email,
                first_name=create_data.first_name,
                last_name=create_data.last_name,
                status="ACTIVE",
            )

            # Roles can be mapped here using RBAC repository if role_ids are provided

        return UserProfileResponse(**data)

    async def update_user(
        self, user_id: str, update_data: UserUpdateRequest
    ) -> Optional[UserProfileResponse]:
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return await self.get_user(user_id)

        async with self.session.begin():
            data = await self.repo.update_user(UUID(user_id), update_dict)
            if not data:
                return None
            return UserProfileResponse(**data)

    async def delete_user(self, user_id: str) -> bool:
        async with self.session.begin():
            return await self.repo.delete_user(UUID(user_id))
