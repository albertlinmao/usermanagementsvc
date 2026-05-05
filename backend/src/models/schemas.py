from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class TenantRegistrationRequest(BaseModel):
    tenant_name: str
    admin_email: EmailStr
    admin_first_name: str
    admin_last_name: str
    admin_password: str


class TenantResponse(BaseModel):
    id: UUID
    name: str
    status: str
    admin_user_id: Optional[UUID] = None


class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    status: str
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    role_ids: Optional[list[UUID]] = []


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    status: Optional[str] = None


class PaginatedUserResponse(BaseModel):
    data: list[UserProfileResponse]
    next_cursor: Optional[str] = None
    has_more: bool
