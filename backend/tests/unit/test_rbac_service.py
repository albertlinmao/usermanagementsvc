import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from services.rbac_service import RBACService
from models.rbac_schemas import RoleCreate, PermissionBase

@pytest.fixture
def mock_session():
    session = MagicMock()
    # Mock async context manager for session.begin()
    session.begin.return_value.__aenter__ = AsyncMock()
    session.begin.return_value.__aexit__ = AsyncMock()
    return session

@pytest.mark.asyncio
async def test_get_roles_success(mock_session):
    service = RBACService(mock_session)
    
    tenant_id = uuid4()
    role_id = uuid4()
    
    service.repo.get_roles = AsyncMock(return_value=[
        {
            "id": role_id,
            "tenant_id": tenant_id,
            "name": "Admin",
            "permissions": []
        }
    ])
    
    roles = await service.get_roles(str(tenant_id))
    
    assert len(roles) == 1
    assert roles[0].id == role_id
    assert roles[0].name == "Admin"
    service.repo.get_roles.assert_called_once_with(tenant_id)

@pytest.mark.asyncio
async def test_create_role_success(mock_session):
    service = RBACService(mock_session)
    
    tenant_id = uuid4()
    role_id = uuid4()
    perm_id = uuid4()
    
    # Mock repo methods
    service.repo.create_role = AsyncMock(return_value=role_id)
    service.repo.get_or_create_permission = AsyncMock(return_value=perm_id)
    service.repo.assign_permission_to_role = AsyncMock()
    
    role_in = RoleCreate(
        name="Editor", 
        permissions=[PermissionBase(resource="articles", action="write")]
    )
    
    result = await service.create_role(str(tenant_id), role_in)
    
    assert result.id == role_id
    assert result.name == "Editor"
    assert len(result.permissions) == 1
    assert result.permissions[0].id == perm_id
    assert result.permissions[0].resource == "articles"
    assert result.permissions[0].action == "write"
    
    service.repo.create_role.assert_called_once_with(tenant_id, "Editor")
    service.repo.get_or_create_permission.assert_called_once_with("articles", "write")
    service.repo.assign_permission_to_role.assert_called_once_with(role_id, perm_id)
