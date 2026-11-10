import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    # HTTP tests run FastAPI's normal handlers against the real Docker PostgreSQL.
    with TestClient(app) as test_client:
        yield test_client
