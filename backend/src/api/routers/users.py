from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.session import get_db
from models.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserProfileResponse,
    PaginatedUserResponse,
)
from services.user_service import UserService
from services.gdpr_service import GdprService
from core.security import verify_gateway_psk
from core.feature_flags import feature_flags

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(verify_gateway_psk)]
)


def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


def get_gdpr_service(session: AsyncSession = Depends(get_db)) -> GdprService:
    return GdprService(session)


@router.get("/", response_model=PaginatedUserResponse)
async def get_users(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    service: UserService = Depends(get_user_service),
):
    """
    Retrieve a paginated list of users.
    """
    return await service.get_users(cursor, limit)


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    """
    Retrieve a specific user profile by ID.
    """
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post(
    "/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateRequest, service: UserService = Depends(get_user_service)
):
    """
    Create a new user profile.
    """
    return await service.create_user(user_data)


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
):
    """
    Update an existing user profile.
    """
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    """
    Soft delete a user profile.
    """
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return None


@router.delete("/{user_id}/hard", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_user(
    user_id: str, service: GdprService = Depends(get_gdpr_service)
):
    """
    Hard delete a user profile (GDPR purging).
    Replaces PII with stubs and maintains the UUID.
    """
    if not feature_flags.is_enabled("gdpr-hard-delete"):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GDPR hard deletion feature is not currently enabled.",
        )

    success = await service.hard_delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return None
