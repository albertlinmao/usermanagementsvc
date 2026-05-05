import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from services.tenant_repo import TenantRepository

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_tenant(mock_session):
    repo = TenantRepository(mock_session)
    expected_id = uuid4()
    
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = expected_id
    mock_session.execute.return_value = mock_result
    
    result = await repo.create_tenant("Test Tenant")
    
    assert result == expected_id
    mock_session.execute.assert_called_once()
    
@pytest.mark.asyncio
async def test_create_user_profile(mock_session):
    repo = TenantRepository(mock_session)
    
    await repo.create_user_profile(uuid4(), "test@test.com", "First", "Last")
    
    mock_session.execute.assert_called_once()
    args, kwargs = mock_session.execute.call_args
    # The parameters dict is passed as the second positional argument
    assert "email" in args[1]
    assert args[1]["email"] == "test@test.com"

@pytest.mark.asyncio
async def test_create_membership(mock_session):
    repo = TenantRepository(mock_session)
    expected_role_id = uuid4()
    
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = expected_role_id
    mock_session.execute.return_value = mock_result
    
    await repo.create_membership(uuid4(), uuid4(), "Admin")
    
    assert mock_session.execute.call_count == 2

@pytest.mark.asyncio
async def test_get_tenant(mock_session):
    repo = TenantRepository(mock_session)
    mock_result = MagicMock()
    
    # Exists
    class MockRow:
        id = uuid4()
        name = "Test"
        status = "ACTIVE"
    mock_result.fetchone.return_value = MockRow()
    mock_session.execute.return_value = mock_result
    
    tenant = await repo.get_tenant(uuid4())
    assert tenant is not None
    assert tenant["name"] == "Test"
    
    # Not found
    mock_result.fetchone.return_value = None
    tenant2 = await repo.get_tenant(uuid4())
    assert tenant2 is None
