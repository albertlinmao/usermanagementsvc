import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from fastapi import HTTPException
from api.deps import RequirePermissions, TenantContext

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.mark.asyncio
@patch('services.rbac_repo.RBACRepository')
async def test_require_permissions_success(mock_repo_class, mock_session):
    mock_repo = MagicMock()
    mock_repo.get_user_permissions = AsyncMock(return_value=[
        {"resource": "articles", "action": "write"}
    ])
    mock_repo_class.return_value = mock_repo
    
    context = TenantContext(
        user_id=str(uuid4()),
        tenant_id=str(uuid4())
    )
    
    dep = RequirePermissions("articles", "write")
    
    result = await dep(context=context, session=mock_session)
    
    assert result == context
    mock_repo.get_user_permissions.assert_called_once()

@pytest.mark.asyncio
@patch('services.rbac_repo.RBACRepository')
async def test_require_permissions_forbidden(mock_repo_class, mock_session):
    mock_repo = MagicMock()
    mock_repo.get_user_permissions = AsyncMock(return_value=[
        {"resource": "articles", "action": "read"}
    ])
    mock_repo_class.return_value = mock_repo
    
    context = TenantContext(
        user_id=str(uuid4()),
        tenant_id=str(uuid4())
    )
    
    dep = RequirePermissions("articles", "write")
    
    with pytest.raises(HTTPException) as exc:
        await dep(context=context, session=mock_session)
        
    assert exc.value.status_code == 403
    assert "Missing required permission: articles:write" in exc.value.detail

from fastapi import HTTPException
from api.deps import get_tenant_context

def test_get_tenant_context_empty_headers():
    with pytest.raises(HTTPException) as exc:
        get_tenant_context(x_user_id="", x_tenant_id="")
    assert exc.value.status_code == 400
    assert "Missing required identity headers" in exc.value.detail

def test_get_tenant_context_success():
    context = get_tenant_context(x_user_id="user-1", x_tenant_id="tenant-1", x_trace_id="trace-1")
    assert context.user_id == "user-1"
    assert context.tenant_id == "tenant-1"
    assert context.trace_id == "trace-1"
