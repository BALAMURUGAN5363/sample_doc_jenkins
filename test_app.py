import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index page loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Task" in response.data and b"Pipeline Dashboard" in response.data

def test_health_endpoint_response_structure(client):
    """Test the health check endpoint returns JSON."""
    response = client.get("/health")
    assert response.is_json
    data = response.get_json()
    assert "status" in data
    assert "database" in data
