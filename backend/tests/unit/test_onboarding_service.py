import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from services.onboarding_service import OnboardingService
from models.schemas import TenantRegistrationRequest

@pytest.fixture
def mock_session():
    session = MagicMock()
    # Let's properly mock an async context manager that does NOT suppress exceptions
    class DummyContextManager:
        async def __aenter__(self):
            return session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False # Do not suppress exceptions
            
    session.begin.return_value = DummyContextManager()
    return session

@pytest.mark.asyncio
@patch("services.onboarding_service.create_client")
@patch("services.onboarding_service.TenantRepository")
async def test_register_tenant_success(mock_repo_class, mock_create_client, mock_session):
    # Setup Supabase client mock
    mock_supabase = MagicMock()
    mock_create_client.return_value = mock_supabase
    
    mock_auth_res = MagicMock()
    mock_auth_res.user.id = str(uuid4())
    mock_supabase.auth.admin.create_user.return_value = mock_auth_res
    mock_supabase.auth.admin.update_user_by_id.return_value = None
    
    # Setup Repo mock
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo
    
    tenant_id = uuid4()
    mock_repo.create_tenant = AsyncMock(return_value=tenant_id)
    mock_repo.create_user_profile = AsyncMock()
    mock_repo.create_membership = AsyncMock()
    
    service = OnboardingService(mock_session)
    
    request = TenantRegistrationRequest(
        tenant_name="Test Tenant",
        admin_email="test@test.com",
        admin_first_name="First",
        admin_last_name="Last",
        admin_password="Password123"
    )
    
    response = await service.register_tenant(request)
    
    assert response.id == tenant_id
    assert response.name == "Test Tenant"
    assert str(response.admin_user_id) == mock_auth_res.user.id
    
    # Verify calls
    mock_supabase.auth.admin.create_user.assert_called_once()
    mock_repo.create_tenant.assert_called_once_with("Test Tenant")
    mock_supabase.auth.admin.update_user_by_id.assert_called_once()
    mock_repo.create_user_profile.assert_called_once()
    mock_repo.create_membership.assert_called_once()


@pytest.mark.asyncio
@patch("services.onboarding_service.create_client")
async def test_register_tenant_auth_failure(mock_create_client, mock_session):
    mock_supabase = MagicMock()
    mock_create_client.return_value = mock_supabase
    
    # Simulate auth failure
    mock_supabase.auth.admin.create_user.side_effect = Exception("User already exists")
    
    service = OnboardingService(mock_session)
    
    request = TenantRegistrationRequest(
        tenant_name="Test Tenant",
        admin_email="test@test.com",
        admin_first_name="First",
        admin_last_name="Last",
        admin_password="Password123"
    )
    
    with pytest.raises(ValueError) as exc:
        await service.register_tenant(request)
        
    assert "Failed to create user in Auth" in str(exc.value)

@pytest.mark.asyncio
@patch("services.onboarding_service.TenantRepository")
async def test_get_tenant_success(mock_repo_class, mock_session):
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo
    
    tid = uuid4()
    mock_repo.get_tenant = AsyncMock(return_value={"id": tid, "name": "Test", "status": "ACTIVE"})
    
    service = OnboardingService(mock_session)
    res = await service.get_tenant(tid)
    assert res.id == tid
    assert res.name == "Test"

@pytest.mark.asyncio
@patch("services.onboarding_service.TenantRepository")
async def test_get_tenant_not_found(mock_repo_class, mock_session):
    mock_repo = MagicMock()
    mock_repo_class.return_value = mock_repo
    mock_repo.get_tenant = AsyncMock(return_value=None)
    
    service = OnboardingService(mock_session)
    with pytest.raises(ValueError):
        await service.get_tenant(uuid4())
