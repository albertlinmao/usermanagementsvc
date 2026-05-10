import json
import uuid

file_path = "user-management-service.postman.collection.json"

with open(file_path, "r") as f:
    collection = json.load(f)

# Keep existing items inside a "Roles (Phase 4)" folder if they aren't already
if len(collection["item"]) > 0 and not collection["item"][0].get("item"):
    # Current items are flat, move them to a folder
    roles_folder = {"name": "Roles (Phase 4)", "item": collection["item"]}
    collection["item"] = [roles_folder]

# Define base headers
headers = [
    {"key": "X-Internal-Secret", "value": "my_local_psk", "type": "text"},
    {
        "key": "X-Tenant-Id",
        "value": "00000000-0000-0000-0000-000000000001",
        "type": "text",
    },
    {
        "key": "X-User-Id",
        "value": "00000000-0000-0000-0000-000000000002",
        "type": "text",
    },
    {"key": "Content-Type", "value": "application/json", "type": "text"},
]

headers_no_body = [
    {"key": "X-Internal-Secret", "value": "my_local_psk", "type": "text"},
    {
        "key": "X-Tenant-Id",
        "value": "00000000-0000-0000-0000-000000000001",
        "type": "text",
    },
    {
        "key": "X-User-Id",
        "value": "00000000-0000-0000-0000-000000000002",
        "type": "text",
    },
]

# Phase 5 Items
users_items = [
    {
        "name": "Create User (POST)",
        "request": {
            "method": "POST",
            "header": headers,
            "body": {
                "mode": "raw",
                "raw": '{\n  "email": "john.doe@example.com",\n  "first_name": "John",\n  "last_name": "Doe",\n  "middle_name": "A",\n  "role_ids": []\n}',
            },
            "url": {
                "raw": "http://localhost:8080/api/v1/users/",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", ""],
            },
        },
    },
    {
        "name": "Get Users (GET)",
        "request": {
            "method": "GET",
            "header": headers_no_body,
            "url": {
                "raw": "http://localhost:8080/api/v1/users/?limit=10",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", ""],
                "query": [{"key": "limit", "value": "10"}],
            },
        },
    },
    {
        "name": "Get User (GET)",
        "request": {
            "method": "GET",
            "header": headers_no_body,
            "url": {
                "raw": "http://localhost:8080/api/v1/users/{{user_id}}",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", "{{user_id}}"],
            },
        },
    },
    {
        "name": "Update User (PUT)",
        "request": {
            "method": "PUT",
            "header": headers,
            "body": {
                "mode": "raw",
                "raw": '{\n  "first_name": "Johnny",\n  "last_name": "Doe",\n  "status": "active"\n}',
            },
            "url": {
                "raw": "http://localhost:8080/api/v1/users/{{user_id}}",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", "{{user_id}}"],
            },
        },
    },
    {
        "name": "Soft Delete User (DELETE)",
        "request": {
            "method": "DELETE",
            "header": headers_no_body,
            "url": {
                "raw": "http://localhost:8080/api/v1/users/{{user_id}}",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", "{{user_id}}"],
            },
        },
    },
]

# Phase 6 Items
audit_webhooks_items = [
    {
        "name": "Get Audit Logs (GET)",
        "request": {
            "method": "GET",
            "header": headers_no_body,
            "url": {
                "raw": "http://localhost:8080/api/v1/audit/?limit=50",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "audit", ""],
                "query": [{"key": "limit", "value": "50"}],
            },
        },
    },
    {
        "name": "Hard Delete User - GDPR (DELETE)",
        "request": {
            "method": "DELETE",
            "header": headers_no_body,
            "url": {
                "raw": "http://localhost:8080/api/v1/users/{{user_id}}/hard",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "users", "{{user_id}}", "hard"],
            },
        },
    },
    {
        "name": "Auth Webhook Event (POST)",
        "request": {
            "method": "POST",
            "header": headers,
            "body": {
                "mode": "raw",
                "raw": '{\n  "type": "INSERT",\n  "table": "users",\n  "record": {\n    "id": "123e4567-e89b-12d3-a456-426614174000",\n    "email": "webhook.test@example.com"\n  },\n  "schema": "auth",\n  "old_record": null\n}',
            },
            "url": {
                "raw": "http://localhost:8080/api/v1/webhooks/auth",
                "protocol": "http",
                "host": ["localhost"],
                "port": "8080",
                "path": ["api", "v1", "webhooks", "auth"],
            },
        },
    },
]

# Add folders to collection
collection["item"].append({"name": "Users (Phase 5)", "item": users_items})

collection["item"].append(
    {"name": "Audit & Compliance (Phase 6)", "item": audit_webhooks_items}
)

# Save collection
with open(file_path, "w") as f:
    json.dump(collection, f, indent=2)

print("Collection updated successfully.")
