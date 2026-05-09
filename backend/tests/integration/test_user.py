import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock

from services.user_service import UserService
from models.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserProfileResponse,
    PaginatedUserResponse,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.begin = MagicMock()
    session.begin.return_value.__aenter__ = AsyncMock()
    session.begin.return_value.__aexit__ = AsyncMock()
    return session


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_get_users(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    mock_repo.get_users = AsyncMock(
        return_value={
            "data": [
                {
                    "id": str(uuid.uuid4()),
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "status": "ACTIVE",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            ],
            "next_cursor": None,
            "has_more": False,
        }
    )

    service = UserService(mock_session)
    result = await service.get_users(cursor=None, limit=10)

    assert isinstance(result, PaginatedUserResponse)
    assert len(result.data) == 1
    assert result.data[0].email == "test@example.com"
    assert result.has_more is False
    mock_repo.get_users.assert_called_once_with(None, 10)


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_get_user_found(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    mock_repo.get_user = AsyncMock(
        return_value={
            "id": user_id,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "status": "ACTIVE",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    service = UserService(mock_session)
    result = await service.get_user(user_id)

    assert isinstance(result, UserProfileResponse)
    assert str(result.id) == user_id
    mock_repo.get_user.assert_called_once_with(uuid.UUID(user_id))


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_get_user_not_found(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    mock_repo.get_user = AsyncMock(return_value=None)

    service = UserService(mock_session)
    result = await service.get_user(user_id)

    assert result is None
    mock_repo.get_user.assert_called_once_with(uuid.UUID(user_id))


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_create_user(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    created_id = str(uuid.uuid4())
    mock_repo.create_user = AsyncMock(
        return_value={
            "id": created_id,
            "email": "new@example.com",
            "first_name": "New",
            "last_name": "User",
            "status": "ACTIVE",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    service = UserService(mock_session)
    req = UserCreateRequest(email="new@example.com", first_name="New", last_name="User")
    result = await service.create_user(req)

    assert isinstance(result, UserProfileResponse)
    assert str(result.id) == created_id
    mock_repo.create_user.assert_called_once()
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_update_user(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    mock_repo.update_user = AsyncMock(
        return_value={
            "id": user_id,
            "email": "test@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "status": "INACTIVE",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    service = UserService(mock_session)
    req = UserUpdateRequest(first_name="Updated", status="INACTIVE")
    result = await service.update_user(user_id, req)

    assert isinstance(result, UserProfileResponse)
    assert result.first_name == "Updated"
    assert result.status == "INACTIVE"
    mock_repo.update_user.assert_called_once_with(
        uuid.UUID(user_id), {"first_name": "Updated", "status": "INACTIVE"}
    )
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_delete_user(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    mock_repo.delete_user = AsyncMock(return_value=True)

    service = UserService(mock_session)
    result = await service.delete_user(user_id)

    assert result is True
    mock_repo.delete_user.assert_called_once_with(uuid.UUID(user_id))
    mock_session.begin.assert_called_once()


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_update_user_empty_data(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    
    # Mock get_user since it is called when update_dict is empty
    mock_repo.get_user = AsyncMock(
        return_value={
            "id": user_id,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "status": "ACTIVE",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    service = UserService(mock_session)
    # Empty update request
    req = UserUpdateRequest()
    result = await service.update_user(user_id, req)

    assert isinstance(result, UserProfileResponse)
    assert result.first_name == "Test"
    mock_repo.update_user.assert_not_called()
    mock_repo.get_user.assert_called_once_with(uuid.UUID(user_id))


@pytest.mark.asyncio
@patch("services.user_service.UserRepository")
async def test_update_user_not_found(mock_repo_class, mock_session):
    mock_repo = mock_repo_class.return_value
    user_id = str(uuid.uuid4())
    
    # Mock update_user to return None
    mock_repo.update_user = AsyncMock(return_value=None)

    service = UserService(mock_session)
    req = UserUpdateRequest(first_name="Updated")
    result = await service.update_user(user_id, req)

    assert result is None
    mock_repo.update_user.assert_called_once_with(
        uuid.UUID(user_id), {"first_name": "Updated"}
    )
    mock_session.begin.assert_called_once()
