import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def mock_supabase():
    client = MagicMock()
    client.auth.admin.update_user_by_id = MagicMock()
    return client


@pytest.fixture
def service(mock_session, mock_supabase):
    """Create GdprService with create_client and settings patched."""
    with patch("services.gdpr_service.create_client", return_value=mock_supabase), \
         patch("services.gdpr_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "http://test-supabase"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test-key"
        from services.gdpr_service import GdprService
        svc = GdprService(mock_session)
    return svc


# ─── hard_delete_user ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_hard_delete_user_not_found(service, mock_session):
    """When user doesn't exist, returns False without modifying anything."""
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    result = await service.hard_delete_user(str(uuid4()))

    assert result is False
    # Only the SELECT was executed, no UPDATE or commit
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_hard_delete_user_success(service, mock_session, mock_supabase):
    """Happy path: user found, supabase updated, DB scrubbed, returns True."""
    user_id = str(uuid4())

    # First call: SELECT check — user exists
    mock_check_result = MagicMock()
    mock_check_result.fetchone.return_value = MagicMock(id=user_id)

    # Second call: UPDATE statement
    mock_update_result = MagicMock()

    mock_session.execute.side_effect = [mock_check_result, mock_update_result]

    result = await service.hard_delete_user(user_id)

    assert result is True

    # Supabase auth admin was called to anonymize the auth record
    mock_supabase.auth.admin.update_user_by_id.assert_called_once()
    call_args = mock_supabase.auth.admin.update_user_by_id.call_args
    assert call_args[0][0] == user_id  # first positional arg is user_id
    assert "redacted.local" in call_args[1]["email"]
    assert call_args[1]["user_metadata"] == {"deleted": True}

    # DB was updated and committed
    assert mock_session.execute.call_count == 2
    mock_session.commit.assert_called_once()

    # Verify the UPDATE params contain the anonymized email and user_id
    update_call_params = mock_session.execute.call_args_list[1][0][1]
    assert "redacted.local" in update_call_params["anon_email"]
    assert update_call_params["user_id"] == user_id


@pytest.mark.asyncio
async def test_hard_delete_user_supabase_error_still_scrubs_db(
    service, mock_session, mock_supabase
):
    """When supabase auth update fails, DB scrub still proceeds and returns True."""
    user_id = str(uuid4())

    # User exists
    mock_check_result = MagicMock()
    mock_check_result.fetchone.return_value = MagicMock(id=user_id)

    mock_update_result = MagicMock()
    mock_session.execute.side_effect = [mock_check_result, mock_update_result]

    # Supabase call raises an exception
    mock_supabase.auth.admin.update_user_by_id.side_effect = Exception(
        "Supabase unavailable"
    )

    result = await service.hard_delete_user(user_id)

    # Should still return True — DB scrub happened despite Supabase failure
    assert result is True
    assert mock_session.execute.call_count == 2
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_hard_delete_user_generates_unique_anon_email(service, mock_session):
    """Each call generates a unique anonymized email."""
    user_id = str(uuid4())

    emails = []

    async def capture_execute(stmt, params=None):
        if params and "anon_email" in params:
            emails.append(params["anon_email"])
        mock_result = MagicMock()
        mock_result.fetchone.return_value = MagicMock(id=user_id)
        return mock_result

    mock_session.execute = AsyncMock(side_effect=capture_execute)

    await service.hard_delete_user(user_id)

    mock_session.execute = AsyncMock(side_effect=capture_execute)
    await service.hard_delete_user(user_id)

    assert len(emails) == 2
    assert emails[0] != emails[1]  # Each call gets a unique anon email
    assert all("deleted-" in e and "@redacted.local" in e for e in emails)


# ─── __init__ ─────────────────────────────────────────────────────


def test_gdpr_service_init_creates_supabase_client(mock_session):
    """Constructor initializes session and calls create_client with settings."""
    with patch("services.gdpr_service.create_client") as mock_create, \
         patch("services.gdpr_service.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "http://test-url"
        mock_settings.SUPABASE_SERVICE_ROLE_KEY = "test-role-key"
        mock_create.return_value = MagicMock()

        from services.gdpr_service import GdprService
        svc = GdprService(mock_session)

        assert svc.session is mock_session
        mock_create.assert_called_once_with("http://test-url", "test-role-key")
        assert svc.supabase is mock_create.return_value
