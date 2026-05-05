import pytest
import json
import logging
from unittest.mock import MagicMock, AsyncMock
from fastapi import Request, Response
from core.logging import JsonFormatter, TraceIdMiddleware

def test_json_formatter_standard():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="test.py", lineno=1,
        msg="Test message", args=(), exc_info=None
    )
    # add custom attributes that the formatter checks
    record.trace_id = "test-trace"
    record.tenant_id = "tenant-1"
    record.user_id = "user-1"
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert data["level"] == "INFO"
    assert data["message"] == "Test message"
    assert data["trace_id"] == "test-trace"
    assert data["tenant_id"] == "tenant-1"
    assert data["user_id"] == "user-1"
    assert "time" in data
    assert "exc_info" not in data

def test_json_formatter_with_exception():
    formatter = JsonFormatter()
    try:
        raise ValueError("Error happened")
    except Exception as e:
        import sys
        exc_info = sys.exc_info()
        
    record = logging.LogRecord(
        name="test", level=logging.ERROR, pathname="test.py", lineno=1,
        msg="Error message", args=(), exc_info=exc_info
    )
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert data["level"] == "ERROR"
    assert data["message"] == "Error message"
    assert "exc_info" in data
    assert "ValueError: Error happened" in data["exc_info"]

@pytest.mark.asyncio
async def test_trace_id_middleware():
    app = MagicMock()
    middleware = TraceIdMiddleware(app)
    
    request = MagicMock(spec=Request)
    request.headers = {
        "X-Trace-Id": "req-trace-1",
        "X-Tenant-Id": "req-tenant-1",
        "X-User-Id": "req-user-1",
    }
    
    mock_response = Response()
    call_next = AsyncMock(return_value=mock_response)
    
    response = await middleware.dispatch(request, call_next)
    
    assert request.state.trace_id == "req-trace-1"
    assert response.headers["X-Trace-Id"] == "req-trace-1"
    call_next.assert_called_once_with(request)
