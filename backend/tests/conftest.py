import pytest
from httpx import AsyncClient, ASGITransport
from api.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_gateway_psk():
    from core.config import settings

    return settings.GATEWAY_PSK


@pytest.fixture
def mock_tenant_id():
    return "test-tenant-1234-abcd"


@pytest.fixture
def mock_user_id():
    return "test-user-5678-efgh"


@pytest.fixture
def authenticated_client(client, mock_tenant_id, mock_user_id, mock_gateway_psk):
    """
    Simulates a request coming through the Supabase Edge Gateway.
    The Gateway would have validated the JWT and injected these headers.
    """
    client.headers.update(
        {
            "X-Internal-Secret": mock_gateway_psk,
            "X-User-Id": mock_user_id,
            "X-Tenant-Id": mock_tenant_id,
            "X-User-Role": "admin",
        }
    )
    return client
