# Technical Implementation Artifacts

**Note:** The user requested specific implementation artifacts (OpenAPI, Schema, Code) as part of the initial specification. These artifacts are provided here to satisfy those constraints.

## 1. OpenAPI 3.0 Specification (YAML)
```yaml
openapi: 3.0.3
info:
  title: Multi-Tenant User Service API
  version: 1.0.0
paths:
  /auth/login:
    post:
      summary: Authenticate user and return JWT
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: Successful authentication
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
  /users:
    get:
      summary: List users for the current tenant
      parameters:
        - in: query
          name: cursor
          schema:
            type: string
        - in: query
          name: status
          schema:
            type: string
      responses:
        '200':
          description: A paginated list of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
components:
  schemas:
    LoginRequest:
      type: object
      properties:
        email:
          type: string
          format: email
        password:
          type: string
      required: [email, password]
    UserResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        tenant_id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        first_name:
          type: string
        last_name:
          type: string
        middle_name:
          type: string
        status:
          type: string
    UserListResponse:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/UserResponse'
        next_cursor:
          type: string
```

## 2. Pydantic Models (Request/Response)
```python
from pydantic import BaseModel, EmailStr, UUID4
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    status: str = "active"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID4
    tenant_id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class StandardError(BaseModel):
    code: str
    message: str
    details: Optional[dict]
    trace_id: str
```

## 3. Suggested FastAPI Folder Structure
```text
src/
├── api/
│   ├── dependencies.py    # DI: get_db, get_current_user, require_permissions
│   ├── middleware/        # Trace ID generation, audit logging
│   └── routers/           # Auth, Tenants, Users, Roles
├── core/
│   ├── config.py          # Settings & Secrets
│   ├── exceptions.py      # Standard error handlers
│   └── security.py        # JWT verification (Supabase)
├── models/                # SQLAlchemy / DB Models
├── schemas/               # Pydantic models (Input/Output)
└── services/              # Business logic (User CRUD, RBAC)
tests/
├── contract/
├── integration/
└── unit/
```

## 4. Supabase/PostgreSQL Schema (DDL)
```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    middle_name VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
```

## 5. Example RLS Policies
```sql
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant Isolation: Users can only view their own tenant users"
ON users FOR SELECT
USING (tenant_id = (current_setting('request.jwt.claims')::json->>'tenant_id')::uuid);

CREATE POLICY "Tenant Isolation: Admins can insert/update their own tenant users"
ON users FOR ALL
USING (
    tenant_id = (current_setting('request.jwt.claims')::json->>'tenant_id')::uuid 
    AND (current_setting('request.jwt.claims')::json->>'role') = 'tenant_admin'
);
```

## 6. Example Middleware/Dependencies
```python
from fastapi import Depends, HTTPException
from core.security import verify_jwt

async def get_current_tenant_user(token: str = Depends(oauth2_scheme)):
    payload = verify_jwt(token)
    return {
        "user_id": payload.get("sub"),
        "tenant_id": payload.get("tenant_id"),
        "role": payload.get("role")
    }

def require_permissions(required_permissions: list[str]):
    async def permission_dependency(user=Depends(get_current_tenant_user)):
        user_perms = await get_user_permissions(user["user_id"])
        if not all(p in user_perms for p in required_permissions):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return permission_dependency
```

## 7. Sample Test Cases (pytest)
```python
def test_tenant_isolation_read_users(client, auth_headers_tenant_a, test_data):
    # User from Tenant A requests users
    response = client.get("/users", headers=auth_headers_tenant_a)
    assert response.status_code == 200
    
    # Assert no users from Tenant B are returned
    users = response.json()["data"]
    for user in users:
        assert user["tenant_id"] == test_data.tenant_a_id

def test_rbac_delete_user_forbidden(client, reader_auth_headers, test_data):
    # Reader role attempts to delete user
    response = client.delete(f"/users/{test_data.user_id}", headers=reader_auth_headers)
    assert response.status_code == 403
    assert response.json()["code"] == "INSUFFICIENT_PERMISSIONS"
```

## 8. Example Audit Log Entries
```json
{
  "id": "e44d...83f1",
  "actor_id": "c71a...92b5",
  "action": "user.delete",
  "resource": "users",
  "resource_id": "a92f...73e0",
  "timestamp": "2026-03-20T10:15:30Z",
  "metadata": {
    "trace_id": "req-99ab-421c",
    "soft_delete": true,
    "ip_address": "192.168.1.10"
  }
}
```
