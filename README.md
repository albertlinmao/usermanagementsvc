# Multi-Tenant User Management API

This is a production-grade, multi-tenant User Service API using FastAPI and Supabase.

## Dev Environment Setup

### Launching Supabase
This project uses a self-hosted Supabase Docker Compose setup to support local development. 

To launch the local Supabase stack, run the following command from the project root:
```bash
docker compose -f supabase/docker-compose.yml up -d
```
*(Note: If you are launching this for the first time, you may need to apply the migrations located in `supabase/migrations/` to the `supabase-db` instance)*

### Checking Data on Supabase
Once the Supabase stack is running, you have two primary ways to inspect the data:

1. **Supabase Studio (Web UI):**
   Open your browser and navigate to the local Studio dashboard:
   - **URL:** [http://localhost:8000](http://localhost:8000)
   - **Username:** `supabase`
   - **Password:** `84408ad96104d519167ff8e76be02b4ffdc97172` (or check `supabase/.env` for `DASHBOARD_PASSWORD`)

2. **Direct Postgres Connection:**
   You can connect your preferred database client (DBeaver, DataGrip, pgAdmin, etc.) directly to the local Postgres instance:
   - **Host:** `localhost`
   - **Port:** `5432`
   - **User:** `postgres`
   - **Password:** `d27096746169f71e6c16998af5dc5322c14c28a2` (or check `supabase/.env` for `POSTGRES_PASSWORD`)
   - **Database:** `postgres`

## Testing

Ensure your Python virtual environment is activated and dependencies are installed before running tests:
```bash
cd backend
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### Unit Test
To execute the unit tests (which do not require the database to be running):
```bash
cd backend
pytest tests/unit
```

### Integration Test
Integration tests require the local Supabase environment to be up and running as they verify database interactions, Edge gateway constraints, and PII encryption/decryption flows.

To execute the integration tests:
```bash
cd backend
pytest tests/integration
```
*(You can also append `-v` or `-s` to see detailed output logs during the integration tests).*

## API Smoke Testing

### Launching FastAPI locally
*Note: Make sure you have launched the Supabase stack first, as the FastAPI container connects to its network.*

You can launch the FastAPI backend locally via Docker Desktop for testing:
```bash
docker compose -f backend/docker-compose.yml up -d --build
```
This maps the FastAPI server to `http://localhost:8080`. You can verify it is running by hitting the health check endpoint: `http://localhost:8080/health` (should return `{"status":"ok"}`).

### 1. Create Tenant (POST)
For developers to quickly run a smoke test and create a tenant with encrypted PII via the onboarding endpoint, import the following cURL command into Postman (or run it directly in your terminal).

*This returns a response containing the new `tenant_id` and `admin_user_id`.*

```bash
curl -X POST http://localhost:8080/api/v1/tenants/ \
     -H "Content-Type: application/json" \
     -H "X-Internal-Secret: my_local_psk" \
     -d '{
       "tenant_name": "Smoke Test Tenant",
       "admin_email": "smoketest@example.com",
       "admin_first_name": "Smoke",
       "admin_last_name": "Test",
       "admin_password": "SmokeTestPassword123!"
     }'
```
*(Note: If you run this multiple times, make sure to change the `admin_email` to avoid unique constraint errors in the Supabase Auth database).*

### 2. Get Current Tenant (GET)
To verify the tenant was created, you can fetch its details. *Make sure to replace the `<tenant_id>` and `<user_id>` placeholders with the UUIDs returned from Step 1.*

```bash
curl -X GET http://localhost:8080/api/v1/tenants/ \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <user_id>"
```

### 3. Create Custom Role (POST)
To test the Granular RBAC feature (User Story 2), you can create a new role and map permissions to it.

```bash
curl -X POST http://localhost:8080/api/v1/roles/ \
     -H "Content-Type: application/json" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <user_id>" \
     -d '{
       "name": "Editor",
       "permissions": [
         {
           "resource": "articles",
           "action": "write"
         },
         {
           "resource": "articles",
           "action": "read"
         }
       ]
     }'
```

### 4. Get Roles (GET)
Verify the custom roles created under your specific tenant boundaries.

```bash
curl -X GET http://localhost:8080/api/v1/roles/ \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <user_id>"
```