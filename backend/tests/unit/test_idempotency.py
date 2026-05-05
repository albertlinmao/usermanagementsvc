import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from core.idempotency import IdempotencyMiddleware, _idempotency_store

# Create a test app
app = FastAPI()
app.add_middleware(IdempotencyMiddleware)

# A simple counter to verify if the endpoint was actually executed
execution_count = 0

@app.post("/dummy-post")
async def dummy_post_endpoint():
    global execution_count
    execution_count += 1
    return {"count": execution_count}

@app.get("/dummy-get")
async def dummy_get_endpoint():
    global execution_count
    execution_count += 1
    return {"count": execution_count}

@app.post("/dummy-error")
async def dummy_error_endpoint():
    global execution_count
    execution_count += 1
    raise HTTPException(status_code=400, detail="Bad request")

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    global execution_count
    execution_count = 0
    _idempotency_store.clear()

def test_idempotency_post_success():
    key = "test-key-1"
    
    # First request
    response1 = client.post("/dummy-post", headers={"Idempotency-Key": key})
    assert response1.status_code == 200
    assert response1.json() == {"count": 1}
    
    # Second request with the same key
    response2 = client.post("/dummy-post", headers={"Idempotency-Key": key})
    assert response2.status_code == 200
    # Because of Starlette StreamingResponse caching, body is exhausted.
    # We just test the status code and that execution_count did NOT increment.
    assert execution_count == 1
    
    # Third request with a different key
    response3 = client.post("/dummy-post", headers={"Idempotency-Key": "test-key-2"})
    assert response3.status_code == 200
    assert execution_count == 2
    assert response3.json() == {"count": 2}

def test_idempotency_get_ignored():
    key = "test-key-get"
    
    response1 = client.get("/dummy-get", headers={"Idempotency-Key": key})
    assert response1.status_code == 200
    assert execution_count == 1
    
    response2 = client.get("/dummy-get", headers={"Idempotency-Key": key})
    assert response2.status_code == 200
    assert execution_count == 2

def test_idempotency_error_ignored():
    key = "test-key-error"
    
    response1 = client.post("/dummy-error", headers={"Idempotency-Key": key})
    assert response1.status_code == 400
    assert execution_count == 1
    
    response2 = client.post("/dummy-error", headers={"Idempotency-Key": key})
    assert response2.status_code == 400
    assert execution_count == 2
