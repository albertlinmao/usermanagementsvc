with open("../README.md", "r") as f:
    content = f.read()

new_smoke_tests = r"""### 1. Create Tenant (POST)
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
```"""

import re
pattern = re.compile(r"### 1\. Create Tenant.*", re.DOTALL)
content = pattern.sub(new_smoke_tests, content)

with open("../README.md", "w") as f:
    f.write(content)
