# Tasks: Multi-Tenant User Service API

**Input**: Design documents from `/specs/001-multi-tenant-user-api/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks, reflecting the constitutional mandate for TDD.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Includes exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Initialize Python environment (requirements, pyproject.toml) in `backend/pyproject.toml`
- [x] T002 Copy and configure Supabase Docker Compose setup in `supabase/docker-compose.yml`
- [x] T003 [P] Configure FastAPI local development container orchestration in `backend/docker-compose.yml`
- [x] T004 [P] Configure pytest and base fixtures in `backend/pytest.ini` and `backend/tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create database schema initialization script for core entities (`tenant`, `user_profile`, `membership`, `role`, `permission`, `role_permission`, `audit_log`) in `supabase/migrations/01_initial_schema.sql`
- [x] T006 [P] Enable `pgcrypto` extension, Vault schema, and configure PII encryption keys in `supabase/migrations/02_vault_pgcrypto.sql`
- [x] T007 [P] Configure AAL2 MFA enforcement via Supabase RLS policies in `supabase/migrations/03_rls_mfa.sql`
- [x] T008 [P] Implement generic audit log Postgres Trigger for state mutations in `supabase/migrations/04_audit_trigger.sql`
- [x] T009 [P] Implement Edge Function API Gateway proxy logic with JWT validation and Trace ID generation in `supabase/functions/api-gateway/index.ts`
- [x] T010 [P] Implement Tenant Suspension KV check in Edge Gateway to block suspended tenants in `supabase/functions/api-gateway/index.ts`
- [x] T011 Implement FastAPI core config and Edge PSK validation dependencies in `backend/src/core/security.py`
- [x] T012 [P] Implement JSON structured logging and Trace ID middleware in `backend/src/core/logging.py`
- [x] T013 [P] Implement global exception handlers for standardized error model in `backend/src/core/exceptions.py`
- [x] T014 [P] Implement Feature Flag provider interface in `backend/src/core/feature_flags.py`
- [x] T015 Create base SQLAlchemy/SQLModel definitions in `backend/src/models/base.py`
- [x] T016 [P] Implement idempotency key middleware in `backend/src/core/idempotency.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Secure Tenant & User Onboarding (Priority: P1) 🎯 MVP

**Goal**: Securely register a new tenant and create an initial administrative user to establish the multi-tenant context, integrating SAML SSO.

**Independent Test**: Register a new tenant, authenticate via Edge gateway (or SAML SSO), and fetch isolated profile data verifying PII is encrypted at rest but decrypted in response.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T017 [P] [US1] Write integration tests for onboarding, auth proxy, PII encryption in `backend/tests/integration/test_onboarding.py`

### Implementation for User Story 1

- [x] T018 [P] [US1] Configure Supabase SAML 2.0 Auth Provider for Enterprise SSO in `supabase/config.toml`
- [x] T019 [P] [US1] Create Pydantic schemas for Tenant and UserProfile in `backend/src/models/schemas.py`
- [x] T020 [US1] Implement DB repository for Tenant and UserProfile with `pgp_sym_encrypt` in `backend/src/services/tenant_repo.py`
- [x] T021 [US1] Implement tenant registration service logic in `backend/src/services/onboarding_service.py`
- [x] T022 [US1] Create POST `/api/v1/tenants` endpoint in `backend/src/api/routers/tenants.py`
- [x] T023 [P] [US1] Update Edge Function to route `/tenants` bypassing JWT validation in `supabase/functions/api-gateway/index.ts`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Granular Access Control Administration (Priority: P2)

**Goal**: Manage roles and map specific permissions to users to enforce least-privilege access.

**Independent Test**: Create custom roles, assign permissions, and verify a user is restricted by their assigned role.

### Tests for User Story 2 ⚠️

- [x] T024 [P] [US2] Write unit and integration tests for RBAC in `backend/tests/integration/test_rbac.py`

### Implementation for User Story 2

- [x] T025 [P] [US2] Create Pydantic schemas for Role, Permission, Membership in `backend/src/models/rbac_schemas.py`
- [x] T026 [US2] Implement DB repository for roles and permissions in `backend/src/services/rbac_repo.py`
- [x] T027 [US2] Implement authorization dependency checking in FastAPI in `backend/src/api/dependencies.py`
- [x] T028 [US2] Create POST/GET `/api/v1/roles` endpoints in `backend/src/api/routers/roles.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - User Lifecycle Management (Priority: P2)

**Goal**: View, update, and manage the lifecycle of users including safely offboarding (soft-deleting) them.

**Independent Test**: Perform full CRUD operations on user records within a tenant, including soft-deletion.

### Tests for User Story 3 ⚠️

- [x] T029 [P] [US3] Write integration tests for User CRUD and pagination in `backend/tests/integration/test_users.py`

### Implementation for User Story 3

- [x] T030 [US3] Implement DB repository for paginated user list with `pgp_sym_decrypt` in `backend/src/services/user_repo.py`
- [x] T031 [US3] Implement soft-delete logic for users in `backend/src/services/user_repo.py`
- [x] T032 [US3] Create GET/PUT/DELETE `/api/v1/users` endpoints in `backend/src/api/routers/users.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Audit & Compliance Tracking (Priority: P3)

**Goal**: Maintain an immutable record of all state-mutating actions and satisfy GDPR data deletion requests.

**Independent Test**: Verify audit logs accurately reflect state changes and GDPR deletions scrub PII.

### Tests for User Story 4 ⚠️

- [x] T033 [P] [US4] Write tests for audit log retrieval and GDPR hard deletion in `backend/tests/integration/test_audit.py`

### Implementation for User Story 4

- [x] T034 [US4] Implement Supabase Auth Webhook handler endpoint to capture authentication events in `backend/src/api/routers/webhooks.py`
- [x] T035 [US4] Implement audit log retrieval repository and endpoint in `backend/src/api/routers/audit.py`
- [x] T036 [US4] Implement GDPR hard-delete logic (scrubbing PII) in `backend/src/services/gdpr_service.py`
- [x] T037 [US4] Create DELETE `/api/v1/users/{id}/hard` endpoint for GDPR purging in `backend/src/api/routers/users.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T038 [P] Create GitHub Actions pipeline to run tests and build Docker images in `.github/workflows/ci.yml`
- [ ] T039 [P] Create Kubernetes deployment manifests and Helm chart configurations in `backend/k8s/deployment.yaml`
- [ ] T040 Create GitHub Actions deployment pipeline for Kubernetes in `.github/workflows/deploy.yml`
- [ ] T041 Implement rate-limiting at the Supabase Edge Gateway in `supabase/functions/api-gateway/index.ts`
- [ ] T042 Create load testing script (`k6`) to validate <200ms latency in `backend/tests/performance/load_test.js`
- [ ] T043 [P] Configure and verify Supabase automated daily backups and Point-in-Time Recovery (PITR) via IaC/Config
- [ ] T044 Wrap the new GDPR hard-deletion endpoint (US4) and Onboarding endpoint (US1) with the configured Feature Flag provider

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on US3 logic for GDPR deletion mapping

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T017 [P] [US1] Write integration tests for onboarding, auth proxy, PII encryption in backend/tests/integration/test_onboarding.py"

# Launch schemas and SSO configurations together:
Task: "T018 [P] [US1] Configure Supabase SAML 2.0 Auth Provider for Enterprise SSO in supabase/config.toml"
Task: "T019 [P] [US1] Create Pydantic schemas for Tenant and UserProfile in backend/src/models/schemas.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories
