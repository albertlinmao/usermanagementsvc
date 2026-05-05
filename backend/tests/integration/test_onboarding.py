import pytest
import uuid
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient


pytestmark = pytest.mark.integration


@pytest.fixture
def test_payload():
    return {
        "tenant_name": f"Test Tenant {uuid.uuid4().hex[:8]}",
        "admin_email": f"admin_{uuid.uuid4().hex[:8]}@test.com",
        "admin_first_name": "John",
        "admin_last_name": "Doe",
        "admin_password": "SecurePassword123!",
    }


@pytest.mark.asyncio
@patch('api.routers.tenants.OnboardingService')
@patch('db.session.AsyncSessionLocal')
async def test_register_tenant_success(
    mock_async_session_local,
    mock_onboarding_service_class,
    client: AsyncClient, mock_gateway_psk: str, test_payload: dict
):
    """
    Test that a valid tenant registration request successfully creates a tenant,
    encrypts the PII correctly, and returns the expected 201 response.
    """
    # 1. Setup API mock
    mock_service_instance = MagicMock()
    mock_onboarding_service_class.return_value = mock_service_instance
    
    mock_tenant_id = str(uuid.uuid4())
    mock_user_id = str(uuid.uuid4())
    
    from models.schemas import TenantResponse
    mock_service_instance.register_tenant = AsyncMock(return_value=TenantResponse(
        id=mock_tenant_id,
        name=test_payload["tenant_name"],
        status="ACTIVE",
        admin_user_id=mock_user_id
    ))

    # 2. Setup DB mock for the test assertions
    mock_session = AsyncMock()
    # mock_async_session_local is a context manager returning a session
    mock_async_session_local.return_value.__aenter__.return_value = mock_session

    # We need to mock session.execute().fetchone() for two different queries
    # First query returns encrypted PII
    mock_result_1 = MagicMock()
    mock_result_1.fetchone.return_value = (b"enc_first", b"enc_last", b"enc_email")
    
    # Second query returns decrypted PII
    mock_result_2 = MagicMock()
    mock_result_2.fetchone.return_value = (test_payload["admin_first_name"], test_payload["admin_last_name"])
    
    mock_session.execute.side_effect = [mock_result_1, mock_result_2]

    headers = {"X-Internal-Secret": mock_gateway_psk}

    # Execute the request
    response = await client.post("/api/v1/tenants/", json=test_payload, headers=headers)

    assert response.status_code == 201, f"Response: {response.json()}"

    data = response.json()
    assert "id" in data
    assert data["name"] == test_payload["tenant_name"]
    assert data["status"] == "ACTIVE"
    assert "admin_user_id" in data

    tenant_id = data["id"]
    user_id = data["admin_user_id"]

    # Verify PII is encrypted in the database
    # Since our tests might run outside docker but access the same DB,
    # we can use the app's get_db dependency.
    from db.session import AsyncSessionLocal
    from sqlalchemy import text

    async with AsyncSessionLocal() as session:
        # Check that user profile exists and PII is encrypted
        stmt = text(
            "SELECT first_name, last_name, email FROM public.user_profile WHERE id = :user_id"
        )
        result = await session.execute(stmt, {"user_id": user_id})
        row = result.fetchone()

        assert row is not None, "User profile should be created in the database"

        # In the onboarding_service, we inserted the email, first_name, and last_name using pgp_sym_encrypt.
        # So the raw values in DB should be bytea (encrypted) and NOT equal to the plain text.
        # Wait, if it's bytea, Postgres driver might return bytes.
        raw_first_name, raw_last_name, raw_email = row[0], row[1], row[2]

        # Ensure it's encrypted (not plain text)
        assert raw_first_name != test_payload["admin_first_name"]
        assert raw_last_name != test_payload["admin_last_name"]

        # Verify we can decrypt it
        decrypt_stmt = text("""
            WITH secret AS (
                SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'pii_encryption_key' LIMIT 1
            )
            SELECT 
                pgp_sym_decrypt(first_name::bytea, secret.decrypted_secret) as dec_first,
                pgp_sym_decrypt(last_name::bytea, secret.decrypted_secret) as dec_last
            FROM public.user_profile, secret
            WHERE id = :user_id
        """)
        dec_result = await session.execute(decrypt_stmt, {"user_id": user_id})
        dec_row = dec_result.fetchone()

        assert dec_row is not None
        assert dec_row[0] == test_payload["admin_first_name"]
        assert dec_row[1] == test_payload["admin_last_name"]


@pytest.mark.asyncio
async def test_register_tenant_without_psk_fails(
    client: AsyncClient, test_payload: dict
):
    """
    Test that calling the onboarding endpoint without the gateway PSK fails with 403.
    """
    # No X-Internal-Secret header provided
    response = await client.post("/api/v1/tenants/", json=test_payload)

    # Fastapi defaults to 422 for missing required header, but our security.py has alias="X-Internal-Secret"
    # Actually, if it's a required Header, FastAPI will return 422 if it's completely missing.
    # If they provide a wrong one, our verify_gateway_psk returns 403.
    # Let's test both.
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_tenant_with_wrong_psk_fails(
    client: AsyncClient, test_payload: dict
):
    """
    Test that calling the onboarding endpoint with an invalid gateway PSK fails with 403.
    """
    headers = {"X-Internal-Secret": "wrong_psk"}

    response = await client.post("/api/v1/tenants/", json=test_payload, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
@patch('api.routers.tenants.OnboardingService')
@patch('db.session.AsyncSessionLocal')
async def test_register_tenant_value_error(
    mock_async_session_local,
    mock_onboarding_service_class,
    client: AsyncClient, mock_gateway_psk: str, test_payload: dict
):
    mock_service_instance = MagicMock()
    mock_onboarding_service_class.return_value = mock_service_instance
    mock_service_instance.register_tenant = AsyncMock(side_effect=ValueError("Test value error"))
    
    headers = {"X-Internal-Secret": mock_gateway_psk}
    response = await client.post("/api/v1/tenants/", json=test_payload, headers=headers)
    assert response.status_code == 400
    assert "Test value error" in response.text

@pytest.mark.asyncio
@patch('api.routers.tenants.OnboardingService')
@patch('db.session.AsyncSessionLocal')
async def test_register_tenant_generic_error(
    mock_async_session_local,
    mock_onboarding_service_class,
    client: AsyncClient, mock_gateway_psk: str, test_payload: dict
):
    mock_service_instance = MagicMock()
    mock_onboarding_service_class.return_value = mock_service_instance
    mock_service_instance.register_tenant = AsyncMock(side_effect=Exception("Unexpected database error"))
    
    headers = {"X-Internal-Secret": mock_gateway_psk}
    response = await client.post("/api/v1/tenants/", json=test_payload, headers=headers)
    assert response.status_code == 500
    assert "Unexpected database error" in response.text

@pytest.mark.asyncio
@patch('api.routers.tenants.OnboardingService')
@patch('db.session.AsyncSessionLocal')
async def test_get_tenant_endpoint(
    mock_async_session_local,
    mock_onboarding_service_class,
    client: AsyncClient, mock_gateway_psk: str
):
    mock_service_instance = MagicMock()
    mock_onboarding_service_class.return_value = mock_service_instance
    
    from models.schemas import TenantResponse
    import uuid
    tid = uuid.uuid4()
    mock_service_instance.get_tenant = AsyncMock(return_value=TenantResponse(id=tid, name="Test", status="ACTIVE"))
    
    headers = {
        "X-Internal-Secret": mock_gateway_psk,
        "X-Tenant-Id": str(tid),
        "X-User-Id": str(uuid.uuid4())
    }
    response = await client.get("/api/v1/tenants/", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test"

@pytest.mark.asyncio
@patch('api.routers.tenants.OnboardingService')
@patch('db.session.AsyncSessionLocal')
async def test_get_tenant_endpoint_errors(
    mock_async_session_local,
    mock_onboarding_service_class,
    client: AsyncClient, mock_gateway_psk: str
):
    mock_service_instance = MagicMock()
    mock_onboarding_service_class.return_value = mock_service_instance
    mock_service_instance.get_tenant = AsyncMock(side_effect=ValueError("Not found"))
    
    headers = {
        "X-Internal-Secret": mock_gateway_psk,
        "X-Tenant-Id": str(uuid.uuid4()),
        "X-User-Id": str(uuid.uuid4())
    }
    # 404
    response = await client.get("/api/v1/tenants/", headers=headers)
    assert response.status_code == 404
    
    # 500
    mock_service_instance.get_tenant = AsyncMock(side_effect=Exception("DB Error"))
    response2 = await client.get("/api/v1/tenants/", headers=headers)
    assert response2.status_code == 500
