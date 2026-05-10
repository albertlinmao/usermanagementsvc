import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

from api.routers.audit import AuditService, get_audit_service


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def service(mock_session):
    return AuditService(mock_session)


def _make_audit_row(
    table_name="user_profile",
    action="UPDATE",
    old_data=None,
    new_data=None,
    changed_by=None,
):
    """Helper to create a mock audit log row."""
    row = MagicMock()
    row.id = uuid4()
    row.table_name = table_name
    row.record_id = uuid4()
    row.action = action
    row.old_data = old_data
    row.new_data = new_data
    row.changed_by = changed_by or uuid4()
    row.changed_at = datetime.now(timezone.utc)
    return row


# ─── get_audit_logs ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_audit_logs_no_cursor(service, mock_session):
    """Returns audit logs without cursor (no WHERE clause)."""
    row = _make_audit_row(old_data={"status": "ACTIVE"}, new_data={"status": "INACTIVE"})

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs(cursor=None, limit=50)

    assert len(result["data"]) == 1
    assert result["data"][0].table_name == "user_profile"
    assert result["data"][0].action == "UPDATE"
    assert result["data"][0].old_data == {"status": "ACTIVE"}
    assert result["data"][0].new_data == {"status": "INACTIVE"}
    assert result["has_more"] is False
    assert result["next_cursor"] is None
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_audit_logs_with_cursor(service, mock_session):
    """When cursor is provided, the WHERE clause filters by changed_at."""
    row = _make_audit_row()

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    cursor_value = "2026-01-01T00:00:00+00:00"
    result = await service.get_audit_logs(cursor=cursor_value, limit=50)

    assert len(result["data"]) == 1
    assert result["has_more"] is False

    # Verify the cursor was passed in the params
    call_args = mock_session.execute.call_args
    params = call_args[0][1]
    assert params["cursor"] == cursor_value


@pytest.mark.asyncio
async def test_get_audit_logs_empty_result(service, mock_session):
    """Returns empty data when no audit logs exist."""
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs()

    assert result["data"] == []
    assert result["has_more"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_audit_logs_has_more_true(service, mock_session):
    """When more rows than limit are returned, has_more is True and next_cursor is set."""
    limit = 2
    # Return limit + 1 rows to trigger has_more
    rows = [_make_audit_row() for _ in range(limit + 1)]

    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs(limit=limit)

    assert len(result["data"]) == limit
    assert result["has_more"] is True
    assert result["next_cursor"] == result["data"][-1].changed_at.isoformat()


@pytest.mark.asyncio
async def test_get_audit_logs_has_more_false_exact_boundary(service, mock_session):
    """When exactly `limit` rows are returned, has_more is False."""
    limit = 2
    rows = [_make_audit_row() for _ in range(limit)]

    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs(limit=limit)

    assert len(result["data"]) == limit
    assert result["has_more"] is False
    assert result["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_audit_logs_null_old_data(service, mock_session):
    """old_data=None maps to None in the response (falsy branch)."""
    row = _make_audit_row(old_data=None, new_data={"key": "val"})

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs()

    assert result["data"][0].old_data is None
    assert result["data"][0].new_data == {"key": "val"}


@pytest.mark.asyncio
async def test_get_audit_logs_null_new_data(service, mock_session):
    """new_data=None maps to None in the response (falsy branch)."""
    row = _make_audit_row(old_data={"key": "val"}, new_data=None)

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs()

    assert result["data"][0].old_data == {"key": "val"}
    assert result["data"][0].new_data is None


@pytest.mark.asyncio
async def test_get_audit_logs_both_data_null(service, mock_session):
    """Both old_data and new_data are None (e.g. INSERT with no prior state)."""
    row = _make_audit_row(old_data=None, new_data=None)

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs()

    assert result["data"][0].old_data is None
    assert result["data"][0].new_data is None


@pytest.mark.asyncio
async def test_get_audit_logs_both_data_present(service, mock_session):
    """Both old_data and new_data are populated dicts."""
    row = _make_audit_row(
        old_data={"status": "ACTIVE"}, new_data={"status": "SUSPENDED"}
    )

    mock_result = MagicMock()
    mock_result.fetchall.return_value = [row]
    mock_session.execute.return_value = mock_result

    result = await service.get_audit_logs()

    assert result["data"][0].old_data == {"status": "ACTIVE"}
    assert result["data"][0].new_data == {"status": "SUSPENDED"}


# ─── get_audit_service factory ────────────────────────────────────


@pytest.mark.asyncio
async def test_get_audit_service_returns_instance():
    """The factory function returns an AuditService with the given session."""
    mock_session = AsyncMock()
    svc = get_audit_service(session=mock_session)

    assert isinstance(svc, AuditService)
    assert svc.session is mock_session
