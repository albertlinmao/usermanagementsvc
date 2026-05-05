import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.fixture
def test_user_payload():
    return {
        "email": "test_user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "middle_name": "M",
        "role_ids": [str(uuid.uuid4())],
    }


@pytest.fixture
def test_user_update_payload():
    return {"first_name": "Updated", "last_name": "User", "status": "active"}


@pytest.mark.asyncio
@patch("api.routers.users.UserService")
async def test_create_user(
    mock_user_service_class, authenticated_client: AsyncClient, test_user_payload: dict
):
    mock_service_instance = MagicMock()
    mock_user_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())

    from models.schemas import UserProfileResponse
    from datetime import datetime

    mock_service_instance.create_user = AsyncMock(
        return_value=UserProfileResponse(
            id=mock_user_id,
            email=test_user_payload["email"],
            first_name=test_user_payload["first_name"],
            last_name=test_user_payload["last_name"],
            status="ACTIVE",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    response = await authenticated_client.post("/api/v1/users/", json=test_user_payload)
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["email"] == test_user_payload["email"]
    assert data["first_name"] == test_user_payload["first_name"]
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
@patch("api.routers.users.UserService")
async def test_get_users(mock_user_service_class, authenticated_client: AsyncClient):
    mock_service_instance = MagicMock()
    mock_user_service_class.return_value = mock_service_instance

    from models.schemas import UserProfileResponse
    from datetime import datetime

    mock_service_instance.get_users = AsyncMock(
        return_value={
            "data": [
                UserProfileResponse(
                    id=str(uuid.uuid4()),
                    email="user@example.com",
                    first_name="First",
                    last_name="Last",
                    status="ACTIVE",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ],
            "next_cursor": None,
            "has_more": False,
        }
    )

    response = await authenticated_client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["email"] == "user@example.com"
    assert "next_cursor" in data


@pytest.mark.asyncio
@patch("api.routers.users.UserService")
async def test_get_user(mock_user_service_class, authenticated_client: AsyncClient):
    mock_service_instance = MagicMock()
    mock_user_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())
    from models.schemas import UserProfileResponse
    from datetime import datetime

    mock_service_instance.get_user = AsyncMock(
        return_value=UserProfileResponse(
            id=mock_user_id,
            email="user@example.com",
            first_name="First",
            last_name="Last",
            status="ACTIVE",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    response = await authenticated_client.get(f"/api/v1/users/{mock_user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == mock_user_id
    assert data["email"] == "user@example.com"


@pytest.mark.asyncio
@patch("api.routers.users.UserService")
async def test_update_user(
    mock_user_service_class,
    authenticated_client: AsyncClient,
    test_user_update_payload: dict,
):
    mock_service_instance = MagicMock()
    mock_user_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())
    from models.schemas import UserProfileResponse
    from datetime import datetime

    mock_service_instance.update_user = AsyncMock(
        return_value=UserProfileResponse(
            id=mock_user_id,
            email="user@example.com",
            first_name=test_user_update_payload["first_name"],
            last_name=test_user_update_payload["last_name"],
            status=test_user_update_payload["status"].upper(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    )

    response = await authenticated_client.put(
        f"/api/v1/users/{mock_user_id}", json=test_user_update_payload
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == mock_user_id
    assert data["first_name"] == test_user_update_payload["first_name"]


@pytest.mark.asyncio
@patch("api.routers.users.UserService")
async def test_delete_user(mock_user_service_class, authenticated_client: AsyncClient):
    mock_service_instance = MagicMock()
    mock_user_service_class.return_value = mock_service_instance

    mock_user_id = str(uuid.uuid4())
    mock_service_instance.delete_user = AsyncMock(return_value=True)

    response = await authenticated_client.delete(f"/api/v1/users/{mock_user_id}")
    assert response.status_code == 204
