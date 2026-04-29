# Quickstart: Multi-Tenant User Service API

This guide walks you through setting up the local development environment for the FastAPI backend and a pure Self-Hosted Supabase Docker instance.

## Prerequisites
- Docker Desktop (Supabase is installed and runs as Docker containers, along with the FastAPI backend)
- Python 3.11+
- Poetry or virtualenv for Python dependency management
- Git

## 1. Local Stack Setup (Docker Compose)
We use a pure Docker Compose approach for both the Supabase infrastructure and the Python backend, removing the dependency on the Supabase CLI for local development.

```bash
# 1. Start the Self-Hosted Supabase stack
# (Assuming your self-hosted docker-compose.yml is in supabase/docker)
cd supabase/docker
cp .env.example .env  # If not already configured
docker compose up -d

# 2. Start the FastAPI backend
cd ../../backend
docker-compose up --build -d
```
*(Note: Ensure your FastAPI backend does not have port conflicts with Supabase. Supabase's API gateway usually defaults to port 8000, so you may need to map the backend to port 8080 or similar).*

## 2. Environment Configuration & Secrets
Copy the sample environment variables in the `backend/` directory:
```bash
cd backend
cp .env.example .env
```
Update `.env` with the values matching your local self-hosted Supabase `.env` configuration:
```ini
SUPABASE_URL=http://localhost:8000
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key-from-supabase-docker-env>
GATEWAY_PSK=my_local_psk
# Feature flags configuration
FEATURE_FLAGS_PROVIDER=local  # 'local', 'unleash', 'posthog'
```

**Supabase Vault & Edge Function Secrets**:
In a pure self-hosted environment without the CLI, you can inject the `GATEWAY_PSK` and `PGCRYPTO_KEY` into your local Vault by:
1. Opening the local Supabase Studio (typically `http://localhost:8000`).
2. Navigating to the **Vault** section to add them manually.
3. Or executing a SQL insert directly into the `vault.secrets` table via the SQL Editor.

## 3. Database Migrations
To apply the base schema (RLS policies, Triggers for audit logs, pgcrypto setup):
1. Open local Supabase Studio in your browser.
2. Navigate to the **SQL Editor**.
3. Paste and run the contents of your migration files.
*(Alternatively, for a fresh start, you can place your `.sql` initialization scripts in the `volumes/db/init/` directory of your Supabase docker setup so they run automatically when the Postgres container is first created).*

## 4. Run Edge Functions Locally
Since the CLI (`supabase functions serve`) is not being used, Edge Functions are handled by the self-hosted `edge-runtime` container.
- Ensure your `docker-compose.yml` mounts your function code into the Edge Runtime, or deploy them via the API.
- The Edge Function should be configured to proxy to the local Docker FastAPI service (using the Docker network, e.g., `http://backend:8000` or `http://host.docker.internal:8000` depending on your network setup).

## 5. Testing
The project uses `pytest` for TDD in the backend. To run the suite:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Architecture Notes
- **Authentication**: Endpoints require a Bearer token issued by Supabase Auth, sent to the Edge Function.
- **Proxy Flow**: The Edge Function validates the token, extracts the tenant/user context, and proxies the request to the backend with `X-User-Id` and `X-Tenant-Id` headers.
- **Security & PII**: The FastAPI backend rejects any requests that don't include the correct `GATEWAY_PSK` (pre-shared key) header. PII data (emails, names) are encrypted at rest using `pgcrypto` with keys from Supabase Vault.
- **Feature Flags**: New capabilities (like granular RBAC and GDPR deletes) are wrapped in feature flags configurable via `FEATURE_FLAGS_PROVIDER`.