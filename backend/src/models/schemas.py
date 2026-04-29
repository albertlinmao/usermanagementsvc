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
    admin_user_id: UUID


class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    status: str
    created_at: datetime
    updated_at: datetime
