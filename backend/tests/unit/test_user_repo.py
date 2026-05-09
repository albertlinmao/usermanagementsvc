import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from services.user_repo import UserRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return UserRepository(mock_session)


def _make_user_row(user_id=None, email="test@example.com", first_name="First",
                   last_name="Last", status="ACTIVE"):
    """Helper to create a mock row object with user attributes."""
    row = MagicMock()
    row.id = user_id or uuid4()
    row.email = email
    row.first_name = first_name
    row.last_name = last_name
    row.status = status
    row.created_at = datetime.now(timezone.utc)
    row.updated_at = datetime.now(timezone.utc)
    return row


# ─── get_users ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_users_returns_data(repo, mock_session):
    user_row = _make_user_row()

    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = [user_row]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 1

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users()

    assert len(result["data"]) == 1
    assert result["data"][0]["email"] == "test@example.com"
    assert result["data"][0]["first_name"] == "First"
    assert result["data"][0]["status"] == "ACTIVE"
    assert result["has_more"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_users_empty_result(repo, mock_session):
    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = []

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users()

    assert result["data"] == []
    assert result["has_more"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_users_with_cursor_pagination(repo, mock_session):
    user_row = _make_user_row()

    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = [user_row]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 100  # many more results

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users(cursor="10", limit=10)

    assert result["has_more"] is True
    assert result["next_cursor"] == "20"  # 10 + 10


@pytest.mark.asyncio
async def test_get_users_with_non_digit_cursor_defaults_to_zero(repo, mock_session):
    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = []

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users(cursor="invalid")

    assert result["data"] == []
    # Verify offset defaulted to 0 — the call still succeeds
    assert mock_session.execute.call_count == 2


@pytest.mark.asyncio
async def test_get_users_with_none_cursor(repo, mock_session):
    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = []

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 0

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users(cursor=None)

    assert result["data"] == []


@pytest.mark.asyncio
async def test_get_users_count_returns_none_defaults_to_zero(repo, mock_session):
    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = []

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = None

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users()

    assert result["has_more"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_users_has_more_false_at_exact_boundary(repo, mock_session):
    """When offset + limit == total_count, has_more should be False."""
    user_row = _make_user_row()

    mock_data_result = MagicMock()
    mock_data_result.fetchall.return_value = [user_row]

    mock_count_result = MagicMock()
    mock_count_result.scalar.return_value = 20  # exactly offset(10) + limit(10)

    mock_session.execute.side_effect = [mock_data_result, mock_count_result]

    result = await repo.get_users(cursor="10", limit=10)

    assert result["has_more"] is False
    assert result["next_cursor"] is None


# ─── get_user ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_found(repo, mock_session):
    user_id = uuid4()
    user_row = _make_user_row(user_id=user_id, email="found@example.com")

    mock_result = MagicMock()
    mock_result.fetchone.return_value = user_row
    mock_session.execute.return_value = mock_result

    result = await repo.get_user(user_id)

    assert result is not None
    assert result["id"] == str(user_id)
    assert result["email"] == "found@example.com"
    assert result["status"] == "ACTIVE"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_user(uuid4())

    assert result is None


# ─── create_user ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_user_success(repo, mock_session):
    user_id = uuid4()
    now = datetime.now(timezone.utc)

    mock_row = MagicMock()
    mock_row.id = user_id
    mock_row.status = "ACTIVE"
    mock_row.created_at = now
    mock_row.updated_at = now

    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_session.execute.return_value = mock_result

    result = await repo.create_user(
        user_id=user_id,
        email="new@example.com",
        first_name="New",
        last_name="User",
    )

    assert result["id"] == str(user_id)
    assert result["email"] == "new@example.com"
    assert result["first_name"] == "New"
    assert result["last_name"] == "User"
    assert result["status"] == "ACTIVE"
    assert result["created_at"] == now
    assert result["updated_at"] == now
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_with_custom_status(repo, mock_session):
    user_id = uuid4()

    mock_row = MagicMock()
    mock_row.id = user_id
    mock_row.status = "PENDING"
    mock_row.created_at = datetime.now(timezone.utc)
    mock_row.updated_at = datetime.now(timezone.utc)

    mock_result = MagicMock()
    mock_result.fetchone.return_value = mock_row
    mock_session.execute.return_value = mock_result

    result = await repo.create_user(
        user_id=user_id,
        email="pending@example.com",
        first_name="Pending",
        last_name="User",
        status="PENDING",
    )

    assert result["status"] == "PENDING"


@pytest.mark.asyncio
async def test_create_user_failure_raises_exception(repo, mock_session):
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(Exception, match="Failed to create user"):
        await repo.create_user(
            user_id=uuid4(),
            email="fail@example.com",
            first_name="Fail",
            last_name="User",
        )


# ─── update_user ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_user_all_fields(repo, mock_session):
    user_id = uuid4()
    now = datetime.now(timezone.utc)

    # First call: get_user (inside update_user to check user exists)
    existing_row = _make_user_row(user_id=user_id)
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = existing_row

    # Second call: the UPDATE statement
    mock_update_result = MagicMock()

    # Third call: get_user again (to return updated data)
    updated_row = _make_user_row(user_id=user_id, first_name="Updated",
                                  last_name="Name", status="INACTIVE")
    mock_get_updated_result = MagicMock()
    mock_get_updated_result.fetchone.return_value = updated_row

    mock_session.execute.side_effect = [
        mock_get_result,       # get_user check
        mock_update_result,    # UPDATE
        mock_get_updated_result,  # get_user return
    ]

    result = await repo.update_user(user_id, {
        "first_name": "Updated",
        "last_name": "Name",
        "status": "INACTIVE",
    })

    assert result is not None
    assert result["first_name"] == "Updated"
    assert result["last_name"] == "Name"
    assert result["status"] == "INACTIVE"
    assert mock_session.execute.call_count == 3


@pytest.mark.asyncio
async def test_update_user_partial_first_name_only(repo, mock_session):
    user_id = uuid4()

    existing_row = _make_user_row(user_id=user_id)
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = existing_row

    mock_update_result = MagicMock()

    updated_row = _make_user_row(user_id=user_id, first_name="NewFirst")
    mock_get_updated_result = MagicMock()
    mock_get_updated_result.fetchone.return_value = updated_row

    mock_session.execute.side_effect = [
        mock_get_result,
        mock_update_result,
        mock_get_updated_result,
    ]

    result = await repo.update_user(user_id, {"first_name": "NewFirst"})

    assert result is not None
    assert result["first_name"] == "NewFirst"


@pytest.mark.asyncio
async def test_update_user_partial_status_only(repo, mock_session):
    user_id = uuid4()

    existing_row = _make_user_row(user_id=user_id)
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = existing_row

    mock_update_result = MagicMock()

    updated_row = _make_user_row(user_id=user_id, status="INACTIVE")
    mock_get_updated_result = MagicMock()
    mock_get_updated_result.fetchone.return_value = updated_row

    mock_session.execute.side_effect = [
        mock_get_result,
        mock_update_result,
        mock_get_updated_result,
    ]

    result = await repo.update_user(user_id, {"status": "INACTIVE"})

    assert result is not None
    assert result["status"] == "INACTIVE"


@pytest.mark.asyncio
async def test_update_user_no_fields_returns_current(repo, mock_session):
    """When update_data has no recognized fields, return current user unchanged."""
    user_id = uuid4()

    existing_row = _make_user_row(user_id=user_id)
    mock_get_result = MagicMock()
    mock_get_result.fetchone.return_value = existing_row
    mock_session.execute.return_value = mock_get_result

    result = await repo.update_user(user_id, {})

    assert result is not None
    assert result["id"] == str(user_id)
    # Only one execute call (the initial get_user), no UPDATE
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.fetchone.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.update_user(uuid4(), {"first_name": "Nope"})

    assert result is None


# ─── delete_user ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_user_success(repo, mock_session):
    mock_result = MagicMock()
    mock_result.rowcount = 1
    mock_session.execute.return_value = mock_result

    result = await repo.delete_user(uuid4())

    assert result is True
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_user_not_found(repo, mock_session):
    mock_result = MagicMock()
    mock_result.rowcount = 0
    mock_session.execute.return_value = mock_result

    result = await repo.delete_user(uuid4())

    assert result is False


@pytest.mark.asyncio
async def test_delete_user_no_rowcount_attribute(repo, mock_session):
    """Covers the getattr fallback when rowcount is missing."""
    mock_result = MagicMock(spec=[])  # spec=[] means no attributes
    mock_session.execute.return_value = mock_result

    result = await repo.delete_user(uuid4())

    assert result is False
