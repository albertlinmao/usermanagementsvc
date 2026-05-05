import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from services.rbac_repo import RBACRepository

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_role(mock_session):
    repo = RBACRepository(mock_session)
    
    expected_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = expected_id
    mock_session.execute.return_value = mock_result
    
    result = await repo.create_role(uuid4(), "Admin")
    
    assert result == expected_id
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_roles(mock_session):
    repo = RBACRepository(mock_session)
    
    tenant_id = uuid4()
    role_id = uuid4()
    perm_id = uuid4()
    
    # Mock row object
    class MockRow:
        def __init__(self, r_id, t_id, r_name, p_id, res, act):
            self.role_id = r_id
            self.tenant_id = t_id
            self.role_name = r_name
            self.perm_id = p_id
            self.resource = res
            self.action = act
            
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MockRow(role_id, tenant_id, "Editor", perm_id, "articles", "write"),
        MockRow(role_id, tenant_id, "Editor", None, None, None) # simulate duplicate or empty
    ]
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_roles(tenant_id)
    
    assert len(result) == 1
    assert result[0]["id"] == role_id
    assert result[0]["name"] == "Editor"
    assert len(result[0]["permissions"]) == 1
    assert result[0]["permissions"][0]["resource"] == "articles"

@pytest.mark.asyncio
async def test_get_or_create_permission_exists(mock_session):
    repo = RBACRepository(mock_session)
    
    expected_id = uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = expected_id
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_or_create_permission("articles", "read")
    
    assert result == expected_id
    mock_session.execute.assert_called_once() # Only check query was executed

@pytest.mark.asyncio
async def test_get_or_create_permission_new(mock_session):
    repo = RBACRepository(mock_session)
    
    expected_id = uuid4()
    
    # First call returns None (not found), second returns ID (inserted)
    mock_result_1 = MagicMock()
    mock_result_1.scalar_one_or_none.return_value = None
    
    mock_result_2 = MagicMock()
    mock_result_2.scalar_one.return_value = expected_id
    
    mock_session.execute.side_effect = [mock_result_1, mock_result_2]
    
    result = await repo.get_or_create_permission("articles", "read")
    
    assert result == expected_id
    assert mock_session.execute.call_count == 2

@pytest.mark.asyncio
async def test_assign_permission_to_role(mock_session):
    repo = RBACRepository(mock_session)
    
    await repo.assign_permission_to_role(uuid4(), uuid4())
    
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_permissions(mock_session):
    repo = RBACRepository(mock_session)
    
    class MockPermRow:
        def __init__(self, res, act):
            self.resource = res
            self.action = act
            
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        MockPermRow("articles", "read"),
        MockPermRow("articles", "write")
    ]
    mock_session.execute.return_value = mock_result
    
    result = await repo.get_user_permissions(uuid4(), uuid4())
    
    assert len(result) == 2
    assert result[0]["resource"] == "articles"
    assert result[1]["action"] == "write"
