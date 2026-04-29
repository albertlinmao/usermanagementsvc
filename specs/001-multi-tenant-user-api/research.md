# Phase 0: Research & Architecture Decisions

## FastAPI in Multi-Tenant APIs (Behind Edge Gateway)
**Task**: Find best practices for FastAPI multi-tenancy behind a proxy.
**Decision**: Use FastAPI Dependencies (`Depends`) to extract and validate `X-User-Id` and `X-Tenant-Id` headers injected by the Edge Function, storing them in a `Request` state or passing them directly to route handlers.
**Rationale**: Keeps route handlers clean, explicitly declares security requirements at the endpoint level, and guarantees tenant isolation is evaluated early in the request lifecycle.
**Alternatives considered**: Middleware-based tenant context injection (rejected because it's harder to selectively apply or mock in pytest compared to dependencies).

## Supabase Python Client for Backend
**Task**: Decide how FastAPI interacts with Supabase Postgres.
**Decision**: Instantiate the official `supabase-py` async client using the `SERVICE_ROLE_KEY` internally, but *always* inject the extracted `tenant_id` into queries programmatically.
**Rationale**: The FastAPI backend is acting as a trusted worker behind the API Gateway (Edge). Using the service role bypasses user RLS but allows the backend to perform complex administrative tasks (like user creation/deletion). We rely on the application code to enforce the boundaries correctly.
**Alternatives considered**: Generating short-lived user JWTs to assume the user's role (rejected due to complexity; the Edge function already authenticated the request).

## Edge Gateway Proxying to Kubernetes (FastAPI)
**Task**: Research patterns for Supabase Edge Functions proxying to K8s.
**Decision**: The Edge Function uses the incoming `Authorization: Bearer <token>`, cryptographically validates it via the `jose` library (low latency), looks up the user's `tenant_id` from `app_metadata`, and proxies the HTTP request to the internal FastAPI Kubernetes Service/Ingress. It attaches an `X-Internal-Secret` to authenticate the Edge Function to the K8s cluster.
**Rationale**: Centralizes authentication at the Edge, avoids unnecessary database calls by verifying tokens cryptographically, and secures the K8s boundary.
**Alternatives considered**: FastAPI directly validating JWTs (rejected since it breaks the Edge-as-Gateway pattern defined in the spec). Making a DB call for token verification on every request (rejected due to high latency).

## Local Development Parity (Docker Compose)
**Task**: Figure out how dev teams will run the stack locally.
**Decision**: Utilize the Supabase CLI (`supabase start`) to provision local Auth, DB, and Edge Functions. Run the FastAPI service via a separate `docker-compose.yml` (or integrated into the Supabase local stack). The local Edge Function is configured to proxy requests to `http://host.docker.internal:8000` or a dedicated Docker network alias.
**Rationale**: Maintains environment parity and meets the SC-006 criteria of <5 minute setup.
**Alternatives considered**: Mocking Supabase Auth locally (rejected because it breaks environment parity and complicates edge function testing).

## K8s CI/CD Pipelines
**Task**: Define deployment automation per the constitution.
**Decision**: Use GitHub Actions to build Docker images, test, and apply Helm charts or Kustomize manifests to the Kubernetes production cluster.
**Rationale**: Strongly aligns with the "Automated testing REQUIRED for all changes. Deployment MUST be automated." constitutional rule. Provides a single source of truth for dev teams.
**Alternatives considered**: Manual `kubectl` deployment (rejected due to constitution violation).

## Secrets Management with Supabase Vault
**Task**: Ensure secrets are encrypted and rotated.
**Decision**: Store the `GATEWAY_PSK` and third-party integration keys in Supabase Vault. The FastAPI backend and Edge Functions will decrypt these keys dynamically at runtime or via initialization tasks mapped to environment variables.
**Rationale**: "Supabase Vault integration REQUIRED for secrets" is a strict constitutional requirement.
**Alternatives considered**: Storing secrets in plain `.env` files or standard K8s secrets without Vault syncing (rejected due to explicit mandate).

## PII Encryption at Rest
**Task**: Ensure Personally Identifiable Information is encrypted at rest.
**Decision**: Use the PostgreSQL `pgcrypto` extension to encrypt fields like `first_name`, `last_name`, and `email` directly at the column level within `user_profile`. Keys for `pgcrypto` will be fetched securely from Supabase Vault.
**Rationale**: Solves the critical gap identified against the "PII encryption REQUIRED at rest and in transit" rule.
**Alternatives considered**: Application-level Python encryption (rejected because it breaks SQL LIKE queries and complicates database migrations, though it can be a fallback if `pgcrypto` is restrictive).

## Feature Flags for Gradual Rollout
**Task**: Add mechanisms for feature toggling.
**Decision**: Implement an internal Feature Flag module (or integrate an open-source tool like Unleash) to wrap new feature rollouts (e.g., granular RBAC, GDPR deletion).
**Rationale**: Constitution mandates "Feature flags REQUIRED for all deployments".
**Alternatives considered**: Static config files (rejected as they require full redeploys to toggle).

## Multi-Factor Authentication (MFA) Enforcement
**Task**: Determine enforcement mechanism for the MFA mandate on elevated privileges.
**Decision**: Enforce AAL2 claims directly via PostgreSQL Row Level Security (RLS) policies.
**Rationale**: Constitution requires MFA. RLS prevents any bypass via application-layer bugs.
**Alternatives considered**: Edge Gateway validation (rejected because RLS provides more robust data protection).

## Single Sign-On (SSO) Integration
**Task**: Evaluate SSO capabilities to meet enterprise onboarding requirements.
**Decision**: Configure SAML 2.0 via Supabase Auth for enterprise integrations.
**Rationale**: Meets constitutional requirement to use Supabase Auth providers for SSO.
**Alternatives considered**: OIDC providers only (rejected per explicit design preference to support SAML).

## Supabase Auth Webhooks Implementation
**Task**: Research Supabase Auth Webhooks implementation for audit logging.
**Decision**: Use asynchronous Database Webhooks (`pg_net` extension) listening to `INSERT` and `UPDATE` events on the `auth.users` table to trigger a FastAPI endpoint secured with an `x-webhook-secret` header.
**Rationale**: Asynchronous database webhooks ensure that the user's login or signup flow is never blocked or slowed down if the backend audit logging system is temporarily unavailable or slow.
**Alternatives considered**: Synchronous Supabase Auth Hooks (would block the authentication flow and add latency to every login).

## GDPR Compliance and PII Anonymization in PostgreSQL Audit Logs
**Task**: Find best practices for GDPR compliance and PII anonymization in PostgreSQL audit logs.
**Decision**: Implement a JSONB trigger-based audit table (`audit_logs`) that intercepts `OLD` and `NEW` row states. A PL/pgSQL function will dynamically scrub predefined PII columns (e.g., email, names) by replacing them with a stub (`"[REDACTED_PII]"`) while extracting and maintaining the `record_id` (UUID).
**Rationale**: This fulfills the requirement to anonymize PII upon request or during standard operations while maintaining the structural integrity of the audit log via the UUID. The trigger ensures no database changes bypass the anonymization.
**Alternatives considered**: `pgaudit` extension (logs raw SQL, extremely difficult to scrub PII from strings). Application-level logging only (misses direct database modifications). Hashing PII (good for pseudonymization, but stubs are simpler and fully meet the "Right to be Forgotten" without risking hash collision/reversal).