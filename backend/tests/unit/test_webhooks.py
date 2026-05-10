import pytest
import json
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from api.main import app
from db.session import get_db
from core.config import settings


# ─── Helpers ──────────────────────────────────────────────────────


def _make_client_and_session():
    """Create an AsyncClient with get_db overridden and return (client, mock_session)."""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    async def _override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = _override_get_db
    client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )
    return client, mock_session


def _auth_headers():
    return {"X-Internal-Secret": settings.GATEWAY_PSK}


# ─── handle_auth_webhook ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_auth_webhook_with_full_payload():
    """Full payload with type, record.id → uses real user_id for record_id and changed_by."""
    client, mock_session = _make_client_and_session()
    try:
        user_id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        payload = {
            "type": "LOGIN",
            "record": {"id": user_id, "email": "test@example.com"},
        }

        response = await client.post(
            "/api/v1/webhooks/auth", json=payload, headers=_auth_headers()
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        mock_session.execute.assert_called_once()
        params = mock_session.execute.call_args[0][1]
        assert params["table_name"] == "auth.users"
        assert params["record_id"] == user_id
        assert params["action"] == "LOGIN"
        assert params["changed_by"] == user_id
        assert json.loads(params["new_data"]) == {
            "id": user_id,
            "email": "test@example.com",
        }
        mock_session.commit.assert_called_once()
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_signup_event():
    """SIGNUP event type is passed through correctly."""
    client, mock_session = _make_client_and_session()
    try:
        user_id = "11111111-2222-3333-4444-555555555555"
        payload = {"type": "SIGNUP", "record": {"id": user_id}}

        response = await client.post(
            "/api/v1/webhooks/auth", json=payload, headers=_auth_headers()
        )

        assert response.status_code == 200
        params = mock_session.execute.call_args[0][1]
        assert params["action"] == "SIGNUP"
        assert params["record_id"] == user_id
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_missing_type_defaults_to_unknown():
    """When 'type' is absent, defaults to UNKNOWN_AUTH_EVENT."""
    client, mock_session = _make_client_and_session()
    try:
        payload = {"record": {"id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"}}

        response = await client.post(
            "/api/v1/webhooks/auth", json=payload, headers=_auth_headers()
        )

        assert response.status_code == 200
        params = mock_session.execute.call_args[0][1]
        assert params["action"] == "UNKNOWN_AUTH_EVENT"
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_missing_record_defaults_to_empty():
    """When 'record' is absent, user_id is None and record_id falls back to zeroed UUID."""
    client, mock_session = _make_client_and_session()
    try:
        payload = {"type": "LOGIN"}

        response = await client.post(
            "/api/v1/webhooks/auth", json=payload, headers=_auth_headers()
        )

        assert response.status_code == 200
        params = mock_session.execute.call_args[0][1]
        assert params["record_id"] == "00000000-0000-0000-0000-000000000000"
        assert params["changed_by"] is None
        assert json.loads(params["new_data"]) == {}
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_record_without_id():
    """When record exists but has no 'id', record_id uses fallback UUID."""
    client, mock_session = _make_client_and_session()
    try:
        payload = {"type": "LOGIN", "record": {"email": "no-id@example.com"}}

        response = await client.post(
            "/api/v1/webhooks/auth", json=payload, headers=_auth_headers()
        )

        assert response.status_code == 200
        params = mock_session.execute.call_args[0][1]
        assert params["record_id"] == "00000000-0000-0000-0000-000000000000"
        assert params["changed_by"] is None
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_empty_payload():
    """Completely empty payload still succeeds with defaults."""
    client, mock_session = _make_client_and_session()
    try:
        response = await client.post(
            "/api/v1/webhooks/auth", json={}, headers=_auth_headers()
        )

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        params = mock_session.execute.call_args[0][1]
        assert params["action"] == "UNKNOWN_AUTH_EVENT"
        assert params["record_id"] == "00000000-0000-0000-0000-000000000000"
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_rejects_missing_psk():
    """Request without X-Internal-Secret header is rejected."""
    client, mock_session = _make_client_and_session()
    try:
        payload = {"type": "LOGIN", "record": {"id": "some-id"}}

        response = await client.post("/api/v1/webhooks/auth", json=payload)

        assert response.status_code == 422  # missing required header
    finally:
        await client.aclose()
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_auth_webhook_rejects_invalid_psk():
    """Request with wrong X-Internal-Secret is rejected as 403."""
    client, mock_session = _make_client_and_session()
    try:
        payload = {"type": "LOGIN", "record": {"id": "some-id"}}

        response = await client.post(
            "/api/v1/webhooks/auth",
            json=payload,
            headers={"X-Internal-Secret": "wrong-secret"},
        )

        assert response.status_code == 403
    finally:
        await client.aclose()
        app.dependency_overrides.clear()
