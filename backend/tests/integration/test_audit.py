import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@patch("api.routers.audit.AuditService", new_callable=MagicMock)
async def test_get_audit_logs(
    mock_audit_service_class, authenticated_client: AsyncClient
):
    """
    Test retrieving audit logs.
    This test mocks the AuditService which will be implemented in T035.
    """
    mock_service_instance = MagicMock()
    mock_audit_service_class.return_value = mock_service_instance

    from datetime import datetime, timezone

    mock_service_instance.get_audit_logs = AsyncMock(
        return_value={
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "table_name": "user_profile",
                    "record_id": str(uuid.uuid4()),
                    "action": "UPDATE",
                    "old_data": {"status": "ACTIVE"},
                    "new_data": {
                        "status": "SUSPENDED",
                        "email": "[REDACTED_PII]",
                        "first_name": "[REDACTED_PII]",
                        "last_name": "[REDACTED_PII]",
                    },
                    "changed_by": str(uuid.uuid4()),
                    "changed_at": datetime.now(timezone.utc).isoformat(),
                }
            ],
            "next_cursor": None,
            "has_more": False,
        }
    )

    response = await authenticated_client.get("/api/v1/audit/")

    # In pure TDD, this endpoint will return 404 until T035 is done.
    # The assert will fail if the endpoint isn't implemented.
    # We wrap it in a try-except or just let it fail naturally.
    # We will let it fail naturally as expected.
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["table_name"] == "user_profile"
    assert data["data"][0]["new_data"]["email"] == "[REDACTED_PII]"


@pytest.mark.asyncio
@patch("api.routers.users.GdprService", new_callable=MagicMock)
async def test_gdpr_hard_delete_user(
    mock_gdpr_service_class, authenticated_client: AsyncClient
):
    """
    Test GDPR hard deletion of a user.
    This test mocks the GdprService which will be implemented in T036 and T037.
    """
    mock_service_instance = MagicMock()
    mock_gdpr_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())
    mock_service_instance.hard_delete_user = AsyncMock(return_value=True)

    response = await authenticated_client.delete(f"/api/v1/users/{mock_user_id}/hard")

    # This assert will fail until T037 is completed.
    assert response.status_code == 204


@pytest.mark.asyncio
@patch("api.routers.users.GdprService", new_callable=MagicMock)
async def test_gdpr_hard_delete_user_not_found(
    mock_gdpr_service_class, authenticated_client: AsyncClient
):
    """
    Test GDPR hard deletion for a non-existent user.
    """
    mock_service_instance = MagicMock()
    mock_gdpr_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())
    mock_service_instance.hard_delete_user = AsyncMock(return_value=False)

    response = await authenticated_client.delete(f"/api/v1/users/{mock_user_id}/hard")

    # If the user doesn't exist, we expect a 404.
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "User not found"
