from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PermissionBase(BaseModel):
    resource: str
    action: str

class PermissionResponse(PermissionBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)

class RoleCreate(BaseModel):
    name: str
    permissions: List[PermissionBase] = []

class RoleResponse(BaseModel):
    id: UUID
    tenant_id: Optional[UUID] = None
    name: str
    permissions: List[PermissionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class MembershipResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: UUID
    role_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
