# Feature Specification: Multi-Tenant User Service API

**Feature Branch**: `001-multi-tenant-user-api`
**Created**: 2026-03-20
**Status**: Draft
**Input**: User description: "Design a production-grade, multi-tenant User Service API using FastAPI and Supabase..."

## Clarifications
### Session 2026-04-18
- Q: How does the system handle concurrent updates to a user's role while they are actively authenticated? → A: Update takes effect on their next JWT token refresh (delay up to token expiry).
- Q: What are the valid lifecycle states for a User entity? → A: Invited, Active, Suspended, Soft-Deleted.
- Q: When processing a GDPR hard deletion (FR-008), how should we handle the User's data to maintain structural integrity? → A: Replace PII fields with anonymized stubs (e.g., "Deleted User") but retain the internal UUID in the database.
- Q: For Custom Roles (FR-004), are the underlying permissions predefined? → A: Permissions are fixed and defined by the system. Tenants can group them into Custom Roles.

### Session 2026-04-02
- Q: Where should the Trace ID / Correlation ID originate to ensure complete end-to-end observability? → A: Option A: Edge Gateway generates Trace ID and passes via `X-Trace-Id` header; FastAPI uses it for all JSON logs and standard errors.
- Q: How should the system block access for all users belonging to a suspended tenant? → A: Option A: Edge Gateway checks tenant status via a fast KV cache and drops requests immediately.
- Q: How should we securely capture and record authentication events occurring at the Edge/Supabase layer? → A: Option A: Use Supabase Auth Webhooks to trigger a backend endpoint that writes to the audit log.
- Q: Which SSO protocol/strategy should be prioritized for MVP tenant onboarding to satisfy the SSO requirement? → A: Option A: Configure SAML 2.0 via Supabase for Enterprise SSO integrations.
- Q: How should we enforce MFA (Multi-factor authentication) for elevated privileges to meet constitutional requirements? → A: Option C: Enforce at database level using Supabase RLS policies for AAL2.

### Session 2026-03-26
- Q: How should responsibilities be divided between Python FastAPI and Supabase Edge Functions? → A: Edge Functions act as an API Gateway/Proxy routing traffic to FastAPI on Kubernetes.
- Q: What does "driven by the dev teams" practically require from this system? → A: Docker Compose for local dev, direct namespace access/pipelines in K8s (DevOps focus).
- Q: How will authentication be handled with Supabase Edge acting as the Gateway to FastAPI? → A: Edge Functions validate tokens and pass trusted context (e.g., X-User-Id, X-Tenant-Id) to FastAPI.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Tenant & User Onboarding (Priority: P1)

As a platform administrator or new subscriber, I want to securely register a new tenant and create an initial administrative user, so that my organization can begin using the platform within its own isolated workspace.

**Why this priority**: Establishing the multi-tenant context and primary user is the fundamental building block for all other platform operations.

**Independent Test**: Can be fully tested by registering a new tenant and user, logging in, and retrieving the isolated profile data.

**Acceptance Scenarios**:
1. **Given** a valid registration request, **When** the system processes the signup, **Then** a new tenant workspace is created alongside a secure user account.
2. **Given** an unauthenticated session, **When** the user provides valid credentials (or authenticates via SAML 2.0 SSO) via the Supabase Edge Gateway, **Then** the system returns an authenticated session context linked specifically to their tenant.
3. **Given** a user from Tenant A, **When** they attempt to read or modify data in Tenant B, **Then** the system denies access to preserve isolation.

---

### User Story 2 - Granular Access Control Administration (Priority: P2)

As a tenant administrator, I want to manage roles and map specific permissions to my users, so that I can enforce least-privilege access across my organization's resources.

**Why this priority**: Security and compliance require strict control over who can perform specific actions (read, write, delete) within the tenant boundaries.

**Independent Test**: Can be tested by creating custom roles, assigning permissions, and verifying that a user with that role can only perform the explicitly allowed actions.

**Acceptance Scenarios**:
1. **Given** an administrative user, **When** they create a new role and assign it permissions (e.g., user.read), **Then** the role is saved and scoped only to their tenant.
2. **Given** a user assigned to a read-only role, **When** they attempt a write action (e.g., deleting a user), **Then** the system rejects the request due to insufficient permissions.

---

### User Story 3 - User Lifecycle Management (Priority: P2)

As a tenant administrator, I want to view, update, and manage the lifecycle of users within my organization, including safely offboarding them without destroying historical records.

**Why this priority**: Managing staff turnover and updating user profiles are daily operational necessities for any B2B SaaS platform.

**Independent Test**: Can be tested by performing full CRUD operations on user records within a tenant, including soft-deleting a user and verifying they no longer have access but remain in audit logs.

**Acceptance Scenarios**:
1. **Given** an administrator querying the user directory, **When** they apply filters (e.g., status, role), **Then** a paginated list of users strictly belonging to their tenant is returned.
2. **Given** a user offboarding request, **When** the administrator deletes the user, **Then** the user is soft-deleted, their access is revoked, and historical data remains intact.

---

### User Story 4 - Audit & Compliance Tracking (Priority: P3)

As a compliance officer, I need an immutable record of all state-mutating actions (who, what, when, where), so that I can satisfy security audits and privacy regulations (like GDPR).

**Why this priority**: Enterprise-grade platforms must guarantee non-repudiation and support forensic investigations into unauthorized access or data modifications.

**Independent Test**: Can be tested by performing several actions (creating users, changing roles) and verifying that the audit trail accurately reflects the events with complete metadata.

**Acceptance Scenarios**:
1. **Given** any state-changing action, **When** the action is completed, **Then** a detailed, immutable log entry is generated capturing the actor, resource, and timestamp.
2. **Given** a GDPR data deletion request, **When** an administrator processes the request, **Then** the user's personal data is purged while maintaining the structural integrity of the audit logs.

### Edge Cases

- What happens when a user belongs to multiple tenants? (The system strictly assumes isolated memberships per the data model, but users may have multiple membership records if needed).
- **Concurrent Role Updates**: If a user's role is updated while they are actively authenticated, the update takes effect on their next JWT token refresh (delay up to token expiry).
- **Tenant Suspension**: If a tenant is suspended, all associated users lose access immediately. This is enforced by the Edge Gateway checking tenant status via a fast KV cache and dropping requests before routing to FastAPI.
- **Gateway Failure**: How does the FastAPI service respond if a request arrives without the trusted Edge Function context headers? (Should return 401/403).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support creating, reading, updating, and soft-deleting (CRUD) user profiles.
- **FR-002**: The system MUST strictly scope all data retrieval and modifications to the authenticated user's tenant context.
- **FR-003**: The Supabase Edge Functions MUST authenticate users, validate session tokens, and proxy requests by injecting secure session context headers (e.g., X-User-Id, X-Tenant-Id) for the FastAPI backend.
- **FR-004**: The system MUST support creating and managing custom roles by grouping system-defined granular permissions (e.g., read, write, admin).
- **FR-005**: The FastAPI system MUST evaluate permissions on every request based on the injected Edge Gateway context and reject unauthorized actions.
- **FR-006**: The system MUST generate an immutable audit log for every state-mutating action and authentication event (utilizing Supabase Auth Webhooks calling a backend endpoint).
- **FR-007**: The system MUST allow administrators to filter, sort, and paginate through lists of users efficiently.
- **FR-008**: The system MUST support GDPR compliance by enabling the permanent deletion of Personally Identifiable Information (PII) upon request, distinct from standard soft-deletion. This MUST be implemented by replacing PII fields with anonymized stubs while retaining the internal UUID to maintain Audit Log structural integrity.
- **FR-009**: The system MUST integrate with Supabase Auth providers to support SAML 2.0 for enterprise Single Sign-On (SSO).

### Non-Functional Requirements (Security, Performance, Observability)

- **NFR-001**: The system MUST guarantee tenant isolation at both the application logic level and the data storage level.
- **NFR-002**: The system MUST NOT expose sensitive information (like passwords or internal system IDs) in any API responses.
- **NFR-003**: The system MUST return deterministic responses and implement idempotent design for state-changing endpoints to facilitate automated testing.
- **NFR-004**: The system MUST support high scalability, avoiding N+1 query patterns and handling paginated lists efficiently.
- **NFR-005**: The system MUST output structured logs that include correlation/trace IDs to track requests across boundaries (Trace IDs MUST be generated by the Edge Gateway and passed to FastAPI via `X-Trace-Id` headers for all logging and error reporting).
- **NFR-006**: The system MUST enforce rate limiting at the Supabase Edge Gateway level to prevent abuse (e.g., maximum 100 requests per minute per tenant, and 5 failed login attempts per 15 minutes per IP).
- **NFR-007**: The system MUST provide local development parity using Docker Compose, allowing dev teams to spin up the entire stack autonomously.
- **NFR-008**: The system MUST deploy the FastAPI application on Kubernetes for production, isolated via team namespaces and driven by dev team pipelines.
- **NFR-009**: The system MUST enforce Multi-Factor Authentication (MFA) for elevated privileges directly at the database level by checking for AAL2 claims in Supabase RLS policies.

### Key Entities

- **Tenant**: Represents an isolated organizational workspace (id, name, status).
- **User**: Represents an individual identity, linked to a tenant (id, email, first_name, middle_name, last_name, status). Valid states are: Invited, Active, Suspended, Soft-Deleted.
- **Membership**: Associates a user with a tenant and a specific role.
- **Role**: A named collection of permissions, either global (system) or tenant-scoped.
- **Permission**: A specific granted capability (resource + action).
- **RolePermission**: The mapping between roles and capabilities.
- **AuditLog**: An immutable record of events (actor, action, resource, timestamp, metadata).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of API endpoints successfully isolate data by tenant context, verified by automated cross-tenant access tests.
- **SC-002**: 100% of state-mutating operations are captured in the immutable audit log with accurate actor and timestamp metadata.
- **SC-003**: Paginated list endpoints (e.g., retrieving users) maintain consistent response times (e.g., <200ms) even when the dataset exceeds 100,000 records.
- **SC-004**: Automated test coverage achieves verification of all primary authorization rules and tenant isolation constraints.
- **SC-005**: API responses conform to a standardized error model (code, message, details, trace_id) across all endpoints without leaking internal system states, utilizing the Trace ID injected by the Gateway.
- **SC-006**: Dev teams can fully build and test the Edge + FastAPI integration locally using Docker Compose within < 5 minutes of setup.