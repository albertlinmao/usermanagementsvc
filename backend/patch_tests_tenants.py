with open("tests/unit/test_tenant_repo.py", "r") as f:
    content = f.read()

new_test = """
@pytest.mark.asyncio
async def test_get_tenant(mock_session):
    repo = TenantRepository(mock_session)
    mock_result = MagicMock()
    
    # Exists
    class MockRow:
        id = uuid4()
        name = "Test"
        status = "ACTIVE"
    mock_result.fetchone.return_value = MockRow()
    mock_session.execute.return_value = mock_result
    
    tenant = await repo.get_tenant(uuid4())
    assert tenant is not None
    assert tenant["name"] == "Test"
    
    # Not found
    mock_result.fetchone.return_value = None
    tenant2 = await repo.get_tenant(uuid4())
    assert tenant2 is None
"""

content += new_test
with open("tests/unit/test_tenant_repo.py", "w") as f:
    f.write(content)


with open("tests/unit/test_onboarding_service.py", "r") as f:
    content2 = f.read()

new_service_test = """
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
"""

content2 += new_service_test
with open("tests/unit/test_onboarding_service.py", "w") as f:
    f.write(content2)


with open("tests/integration/test_onboarding.py", "r") as f:
    content3 = f.read()

new_integration_test = """
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
"""

content3 += new_integration_test
with open("tests/integration/test_onboarding.py", "w") as f:
    f.write(content3)
