import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient

pytestmark = pytest.mark.integration

@pytest.fixture
def test_role_payload():
    return {
        "name": "Editor",
        "permissions": [{"resource": "articles", "action": "write"}]
    }

@pytest.mark.asyncio
@patch('api.routers.roles.RBACService')
async def test_create_role_success(mock_rbac_service_class, authenticated_client: AsyncClient, test_role_payload: dict):
    # Setup mock
    mock_service_instance = MagicMock()
    mock_rbac_service_class.return_value = mock_service_instance
    
    mock_role_id = str(uuid.uuid4())
    
    # We expect a RoleResponse
    from models.rbac_schemas import RoleResponse, PermissionResponse
    mock_service_instance.create_role = AsyncMock(return_value=RoleResponse(
        id=mock_role_id,
        tenant_id=authenticated_client.headers["X-Tenant-Id"],
        name=test_role_payload["name"],
        permissions=[
            PermissionResponse(id=str(uuid.uuid4()), resource="articles", action="write")
        ]
    ))
    
    response = await authenticated_client.post("/api/v1/roles/", json=test_role_payload)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["name"] == "Editor"
    assert len(data["permissions"]) == 1
    assert data["permissions"][0]["resource"] == "articles"

@pytest.mark.asyncio
@patch('api.routers.roles.RBACService')
async def test_get_roles_success(mock_rbac_service_class, authenticated_client: AsyncClient):
    mock_service_instance = MagicMock()
    mock_rbac_service_class.return_value = mock_service_instance
    
    from models.rbac_schemas import RoleResponse
    mock_service_instance.get_roles = AsyncMock(return_value=[
        RoleResponse(id=str(uuid.uuid4()), tenant_id=authenticated_client.headers["X-Tenant-Id"], name="Admin", permissions=[])
    ])
    
    response = await authenticated_client.get("/api/v1/roles/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "Admin"

@pytest.mark.asyncio
@patch('api.routers.roles.RBACService')
async def test_create_role_error(mock_rbac_service_class, authenticated_client: AsyncClient, test_role_payload: dict):
    mock_service_instance = MagicMock()
    mock_rbac_service_class.return_value = mock_service_instance
    mock_service_instance.create_role = AsyncMock(side_effect=Exception("Database error generating role"))
    
    response = await authenticated_client.post("/api/v1/roles/", json=test_role_payload)
    assert response.status_code == 400
    assert "Database error generating role" in response.text
