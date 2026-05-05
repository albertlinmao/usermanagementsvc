import pytest
from fastapi import Request, HTTPException
from core.exceptions import APIError, custom_exception_handler
from unittest.mock import MagicMock

@pytest.fixture
def mock_request():
    req = MagicMock(spec=Request)
    req.state.trace_id = "test-trace-id"
    req.url.path = "/test"
    return req

@pytest.mark.asyncio
async def test_api_error_handler(mock_request):
    error = APIError(
        code="CUSTOM_ERROR",
        message="A custom message",
        status_code=422,
        details={"field": "invalid"}
    )
    
    response = await custom_exception_handler(mock_request, error)
    
    assert response.status_code == 422
    data = response.body.decode()
    assert "CUSTOM_ERROR" in data
    assert "A custom message" in data
    assert "test-trace-id" in data
    assert "invalid" in data

@pytest.mark.asyncio
async def test_http_exception_handler(mock_request):
    error = HTTPException(status_code=403, detail="Forbidden area")
    
    response = await custom_exception_handler(mock_request, error)
    
    assert response.status_code == 403
    data = response.body.decode()
    assert "HTTP_EXCEPTION" in data
    assert "Forbidden area" in data

@pytest.mark.asyncio
async def test_generic_exception_handler(mock_request):
    error = ValueError("Something broke")
    
    response = await custom_exception_handler(mock_request, error)
    
    assert response.status_code == 500
    data = response.body.decode()
    assert "INTERNAL_SERVER_ERROR" in data
    assert "unexpected error occurred" in data
    assert "test-trace-id" in data
