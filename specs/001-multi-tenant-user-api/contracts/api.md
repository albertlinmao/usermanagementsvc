# Phase 1: API Contracts

## Version 1 REST API (`/api/v1`)

The API follows RESTful principles and semantic versioning. 
All requests require a valid Supabase JWT Bearer token in the `Authorization` header.

### 1. Tenant Management

- **POST `/tenants`**
  - **Description**: Registers a new tenant and an initial administrative user.
  - **Request Body**:
    ```json
    {
      "tenant_name": "Acme Corp",
      "admin_email": "admin@acmecorp.com",
      "admin_first_name": "Admin",
      "admin_last_name": "User",
      "admin_password": "secure_password123"
    }
    ```
  - **Response**: `201 Created`
    ```json
    {
      "id": "uuid-tenant",
      "name": "Acme Corp",
      "status": "ACTIVE",
      "admin_user_id": "uuid-user"
    }
    ```

### 2. User Management

- **GET `/users`**
  - **Description**: Retrieves a paginated list of users within the authenticated user's tenant.
  - **Query Parameters**: `cursor` (string), `limit` (integer), `status` (string), `role_id` (string)
  - **Response**: `200 OK`
    ```json
    {
      "data": [
        {
          "id": "uuid-user",
          "email": "user@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "status": "ACTIVE",
          "role": { "id": "uuid-role", "name": "Admin" }
        }
      ],
      "next_cursor": "encoded-cursor-string"
    }
    ```

- **POST `/users`**
  - **Description**: Creates a new user in the tenant and assigns a role.
  - **Request Body**:
    ```json
    {
      "email": "newuser@example.com",
      "first_name": "New",
      "last_name": "User",
      "role_id": "uuid-role"
    }
    ```
  - **Response**: `201 Created`

- **DELETE `/users/{id}`**
  - **Description**: Soft-deletes a user from the tenant, retaining audit logs but removing access.
  - **Response**: `204 No Content`

- **DELETE `/users/{id}/hard`** (GDPR request)
  - **Description**: Permanently purges PII for a specific user.
  - **Response**: `204 No Content`

### 3. Role-Based Access Control (RBAC)

- **GET `/roles`**
  - **Description**: Retrieves roles available for the tenant.
  - **Response**: `200 OK` (List of Roles and associated Permissions)

- **POST `/roles`**
  - **Description**: Creates a new custom role with specific permissions.
  - **Request Body**:
    ```json
    {
      "name": "ReadOnlyUser",
      "permission_ids": ["uuid-perm-1", "uuid-perm-2"]
    }
    ```
  - **Response**: `201 Created`

### 4. Audit & Compliance

- **GET `/audit-logs`**
  - **Description**: Retrieves audit logs for the tenant.
  - **Query Parameters**: `cursor`, `limit`, `actor_id`, `action`, `resource_type`
  - **Response**: `200 OK`
    ```json
    {
      "data": [
        {
          "id": "uuid-log",
          "actor_id": "uuid-user",
          "action": "CREATE",
          "resource_type": "users",
          "resource_id": "uuid-user-created",
          "timestamp": "2026-03-20T10:00:00Z",
          "metadata": { "email": "newuser@example.com" }
        }
      ],
      "next_cursor": "encoded-cursor-string"
    }
    ```

## Standard Error Response
All endpoints use a unified error schema.
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid access token",
    "details": {},
    "trace_id": "req-uuid"
  }
}
```