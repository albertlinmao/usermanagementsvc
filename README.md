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

### 5. Create User (POST)
To test the User Lifecycle Management feature (User Story 3), create a new user profile inside your tenant.

```bash
curl -X POST http://localhost:8080/api/v1/users/ \
     -H "Content-Type: application/json" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>" \
     -d '{
       "email": "user.smoke@example.com",
       "first_name": "Smoke",
       "last_name": "User",
       "middle_name": "Test",
       "role_ids": []
     }'
```
*(This will return the new user's `<user_id>` needed for subsequent steps).*

### 6. Get Users (GET)
Fetch a paginated list of all users within your tenant.

```bash
curl -X GET "http://localhost:8080/api/v1/users/?limit=10" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>"
```

### 7. Get User Details (GET)
Fetch details for a specific user using their `<user_id>`.

```bash
curl -X GET "http://localhost:8080/api/v1/users/<user_id>" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>"
```

### 8. Update User (PUT)
Update a user's details, for example, changing their status to "active".

```bash
curl -X PUT "http://localhost:8080/api/v1/users/<user_id>" \
     -H "Content-Type: application/json" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>" \
     -d '{
       "first_name": "Updated Smoke",
       "last_name": "User",
       "status": "active"
     }'
```

### 9. Soft Delete User (DELETE)
Soft delete a user by changing their status without wiping their underlying records.

```bash
curl -X DELETE "http://localhost:8080/api/v1/users/<user_id>" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>"
```

### 10. Get Audit Logs (GET)
To verify Audit Tracking (User Story 4) captures state-mutating events. This returns immutable, paginated logs of system actions.

```bash
curl -X GET "http://localhost:8080/api/v1/audit/?limit=50" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>"
```

### 11. Auth Webhook Event (POST)
Test the webhook endpoint used to securely log Supabase Auth events.

```bash
curl -X POST "http://localhost:8080/api/v1/webhooks/auth" \
     -H "Content-Type: application/json" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>" \
     -d '{
       "type": "INSERT",
       "table": "users",
       "record": {
         "id": "<user_id>",
         "email": "webhook.test@example.com"
       },
       "schema": "auth",
       "old_record": null
     }'
```

### 12. GDPR Hard Delete (DELETE)
Trigger a GDPR compliance erasure on a user's profile. This replaces their PII with `[REDACTED_PII]` stubs inside the DB while preserving structural UUID integrity for the audit logs.

```bash
curl -X DELETE "http://localhost:8080/api/v1/users/<user_id>/hard" \
     -H "X-Internal-Secret: my_local_psk" \
     -H "X-Tenant-Id: <tenant_id>" \
     -H "X-User-Id: <admin_user_id>"
```

## Debug with me
If you're using an AI Assistant (like AntiGravity) and run into issues while testing the Create User API (or any other API), you can simply ask the assistant to debug it with you!

Here are some ways the AI can help debug:

### 1. Reproduce the Request and Analyze the Response
If you are getting a 4xx or 5xx error, the AI can run a `curl` command directly from its environment against your local server to see the exact error response and traceback. Just tell it the payload you are sending or the error you are receiving.

### 2. Inspect the Backend Logs
If the API is failing silently or returning a 500 error, the AI can inspect your local backend logs to find the exact stack trace by running `docker compose` log commands or by temporarily injecting `print()` statements or structured logging into `backend/src/services/user_service.py` to trace the data flow (e.g., verifying if the Supabase Auth call is failing or if the database `INSERT` is throwing a unique constraint violation).

 $ docker compose -f backend/docker-compose.yml logs --tail 50 backend

### 3. Check Database & Supabase State
Since the `create_user` API coordinates between **Supabase Auth** (identity) and **PostgreSQL** (`user_profile` table), desyncs often happen here (e.g., a user exists in Auth but not in the DB). 
The AI can use its tools to execute SQL queries directly against your local Postgres database to check the state of the tables.

### 4. Run the Integration Tests
The project already has an integration test suite. The AI can run specific test cases in isolation, for example:
```bash
cd backend && python -m pytest tests/integration/test_users.py::test_create_user -v
```

Just say "Help me debug the create user API" or paste your error message, and the assistant can immediately run the tools to investigate!