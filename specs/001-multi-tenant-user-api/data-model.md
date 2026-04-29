# Phase 1: Data Model

## Core Entities & Relationships

### `tenant`
Represents an isolated organizational workspace.
- `id` (UUID, Primary Key)
- `name` (String, Required)
- `status` (Enum: ACTIVE, SUSPENDED, Required)
- `created_at` (Timestamp, Auto)
- `updated_at` (Timestamp, Auto)

### `user_profile`
Represents an individual identity, linked to a tenant (Maps 1:1 to Supabase Auth `auth.users`).
- `id` (UUID, Primary Key, Foreign Key to `auth.users.id`)
- `email` (String, Required, Unique) - **PII Encrypted (pgcrypto)**
- `first_name` (String, Required) - **PII Encrypted (pgcrypto)**
- `middle_name` (String, Optional) - **PII Encrypted (pgcrypto)**
- `last_name` (String, Required) - **PII Encrypted (pgcrypto)**
- `status` (Enum: INVITED, ACTIVE, SUSPENDED, SOFT_DELETED, Required)
- `deleted_at` (Timestamp, Optional)
- `created_at` (Timestamp, Auto)
- `updated_at` (Timestamp, Auto)

### `membership`
Associates a user with a tenant and a specific role.
- `id` (UUID, Primary Key)
- `tenant_id` (UUID, Foreign Key to `tenant.id`)
- `user_id` (UUID, Foreign Key to `user_profile.id`)
- `role_id` (UUID, Foreign Key to `role.id`)
- `created_at` (Timestamp, Auto)
*Constraints*: Unique constraint on `(tenant_id, user_id)`.

### `role`
A named collection of permissions, either global (system) or tenant-scoped.
- `id` (UUID, Primary Key)
- `tenant_id` (UUID, Foreign Key to `tenant.id`, Nullable for global roles)
- `name` (String, Required)
- `created_at` (Timestamp, Auto)
*Constraints*: Unique constraint on `(tenant_id, name)`.

### `permission`
A specific granted capability (resource + action).
- `id` (UUID, Primary Key)
- `resource` (String, Required, e.g., 'users', 'roles')
- `action` (String, Required, e.g., 'read', 'write', 'delete')
- `created_at` (Timestamp, Auto)
*Constraints*: Unique constraint on `(resource, action)`.

### `role_permission`
The mapping between roles and capabilities.
- `id` (UUID, Primary Key)
- `role_id` (UUID, Foreign Key to `role.id`)
- `permission_id` (UUID, Foreign Key to `permission.id`)
- `created_at` (Timestamp, Auto)
*Constraints*: Unique constraint on `(role_id, permission_id)`.

### `audit_log`
An immutable record of events.
- `id` (UUID, Primary Key)
- `table_name` (String, Required)
- `record_id` (UUID, Required) - Maintains structural integrity when PII is redacted
- `action` (String, Required, e.g., 'INSERT', 'UPDATE', 'DELETE')
- `old_data` (JSONB, Optional) - Contains state before action, with PII fields replaced by `"[REDACTED_PII]"`
- `new_data` (JSONB, Optional) - Contains state after action, with PII fields replaced by `"[REDACTED_PII]"`
- `changed_by` (UUID, Foreign Key to `user_profile.id`, Nullable)
- `changed_at` (Timestamp, Auto)

## State Transitions
- **User**: `INVITED` -> `ACTIVE` (User completes onboarding). `ACTIVE` -> `SUSPENDED` (User temporarily disabled). `ACTIVE` -> `SOFT_DELETED` (Access revoked, retained for audit).
- **Tenant**: `ACTIVE` -> `SUSPENDED` (All associated users lose access immediately).

## Data Isolation & Encryption
- The database enforces PostgreSQL Row Level Security (RLS) policies as a fallback.
- The FastAPI backend, acting as a trusted service, programmatically applies `tenant_id` filters to all queries based on the `X-Tenant-Id` header injected by the Supabase Edge Gateway.
- **PII Encryption**: The `user_profile` table uses the `pgcrypto` extension to encrypt PII fields at rest. The encryption keys are securely managed and rotated via **Supabase Vault**.
- **GDPR Hard Deletion**: Triggers on the `audit_log` automatically replace `email`, `first_name`, and `last_name` with `"[REDACTED_PII]"` stubs when a GDPR deletion is requested, ensuring the UUID and structure remain intact while PII is purged.