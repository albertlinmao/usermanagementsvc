# Implementation Plan: Multi-Tenant User Service API

**Branch**: `001-multi-tenant-user-api` | **Date**: 2026-04-18 | **Spec**: `/specs/001-multi-tenant-user-api/spec.md`
**Input**: Feature specification from `/specs/001-multi-tenant-user-api/spec.md`

## Summary

Design a production-grade, multi-tenant User Service API using FastAPI and Supabase. The technical approach relies on Supabase Edge Functions acting as the API Gateway for authentication (cryptographically verifying JWTs and resolving tenant IDs) and routing traffic to a Python FastAPI backend deployed on Kubernetes. PostgreSQL (via Supabase) serves as the persistent store, utilizing Row-Level Security (RLS) for MFA enforcement and `pgcrypto` for PII encryption at rest. Audit logs are populated asynchronously via Supabase Database Webhooks.

## Technical Context

**Language/Version**: Python 3.11+, TypeScript/Deno (Edge)
**Primary Dependencies**: FastAPI, Supabase Python Client, Pydantic, pytest, Uvicorn, PyJWT
**Storage**: PostgreSQL (via Supabase)
**Testing**: pytest
**Target Platform**: Kubernetes (Linux server)
**Project Type**: Web API
**Performance Goals**: <200ms p95 response time for paginated lists > 100k records
**Constraints**: Strong tenant isolation, GDPR compliance (PII redaction in audit logs), 99.9% uptime, Unleash for Feature Flagging
**Scale/Scope**: Enterprise multi-tenancy, high scalability

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Supabase-Centric & API-First**: Leverages Supabase Auth, Edge Functions, and DB Webhooks. API-first design with explicit contracts.
- [x] **II. TDD & Reliability**: Adopts pytest for TDD. Graceful degradation and scale via K8s deployment.
- [x] **III. Data & Consistency**: Employs `pgcrypto` for PII, JSONB triggers for Audit logs (GDPR), and Vault for secrets.
- [x] **IV. Security & Compliance**: RBAC, MFA via AAL2 RLS, and immutable audit logs via `pg_net` webhooks.
- [x] **V. Observability & Operability**: Trace ID propagation from Edge to FastAPI for structured logging. Local parity via Docker Compose.

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-tenant-user-api/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/                # API route handlers (v1, v2, etc.)
│   │   └── v1/
│   │       ├── api.py      # Entry point for including all sub-routers
│   │       └── endpoints/  # Resource-specific routes (e.g., users.py, items.py)
│   ├── core/               # App-wide settings, config, and security
│   │   ├── config.py       # Pydantic BaseSettings for env vars
│   │   └── security.py     # JWT, password hashing utilities
│   ├── db/                 # Database initialization and session management
│   │   ├── base.py         # Import all models for Alembic discovery
│   │   └── session.py      # SQLAlchemy/SQLModel engine and SessionLocal
│   ├── models/             # ORM models (SQLAlchemy/SQLModel)
│   ├── schemas/            # Pydantic models for data validation/serialization
│   ├── services/           # Core business logic and external integrations
│   ├── repositories/       # Database CRUD operations (optional but recommended)
│   ├── utils/              # General-purpose helper functions
│   └── main.py             # App entry point; mounts routes and middleware
├── alembic/                # Database migration scripts
├── tests/                  # Pytest suite mirroring the app structure
├── deploy/                 # 🚀 Production deployment assets
│   ├── docker/             # Container build artifacts
│   ├── kubernetes/          # K8s manifests (platform-agnostic base)
│   ├── cloud/                 # ☁️ Cloud-specific configurations
│   ├── ci-cd/              # Pipeline definitions
│   └── scripts/            # Deployment automation
├── .env                    # Environment variables
├── docker-compose.yml      # Local development container setup
└── pyproject.toml          # Dependency management (Poetry, PDM, or UV)

supabase/
├── functions/              # Edge functions (TypeScript/Deno)
│   └── api-gateway/        # The API proxy and auth verifier
├── migrations/             # Supabase schema definitions and audit triggers
└── config.toml             # Local Supabase config
```

**Structure Decision**: A standard Web Application structure divided between `backend/` for FastAPI implementation, `deploy/` for Kubernetes and CI/CD assets (based on the user's explicit structural outline), and `supabase/` for the Edge Functions and database migrations.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **C1: Edge Functions MUST encapsulate business logic** | This project explicitly requires a Python FastAPI backend for primary business logic per the product specification. | Placing all logic in Deno Edge Functions was rejected because Python is the mandated stack for backend extensibility and data engineering workflows in this specific platform. This serves as the approved Architectural Exception. |