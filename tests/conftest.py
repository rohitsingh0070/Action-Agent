import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.store.memory_store import memory_store

@pytest.fixture(autouse=True)
def reset_store():
    memory_store.reset()
    yield
    memory_store.reset()

@pytest.fixture
def client():
    return TestClient(app)
