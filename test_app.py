import pytest
from app import app, perform_calculation

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ============================================================================
# 1. Unit Tests: Pure Mathematical & Business Logic
# ============================================================================
class TestMathLogic:
    def test_addition(self):
        result, expr = perform_calculation(15, "+", 25)
        assert result == 40
        assert "15.0 + 25.0 = 40" in expr

    def test_subtraction(self):
        result, expr = perform_calculation(100, "-", 45)
        assert result == 55

    def test_multiplication(self):
        result, expr = perform_calculation(12, "*", 8)
        assert result == 96

    def test_division(self):
        result, expr = perform_calculation(100, "/", 4)
        assert result == 25

    def test_division_precision(self):
        result, _ = perform_calculation(10, "/", 3)
        assert result == 3.3333

    def test_divide_by_zero_raises_error(self):
        with pytest.raises(ZeroDivisionError):
            perform_calculation(50, "/", 0)

    def test_modulo(self):
        result, _ = perform_calculation(17, "%", 5)
        assert result == 2

    def test_power(self):
        result, _ = perform_calculation(2, "^", 8)
        assert result == 256

    def test_invalid_operator_raises_error(self):
        with pytest.raises(ValueError):
            perform_calculation(10, "INVALID", 5)

    def test_invalid_numbers_raise_error(self):
        with pytest.raises(ValueError):
            perform_calculation("abc", "+", 5)

# ============================================================================
# 2. Integration Tests: REST API Endpoints
# ============================================================================
class TestApiEndpoints:
    def test_api_calculate_success(self, client):
        payload = {"num1": 25, "op": "*", "num2": 4}
        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["result"] == 100

    def test_api_calculate_divide_by_zero(self, client):
        payload = {"num1": 10, "op": "/", "num2": 0}
        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Cannot divide by zero" in data["error"]

    def test_api_calculate_missing_fields(self, client):
        payload = {"num1": 10}
        response = client.post("/api/calculate", json=payload)
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert "Missing required fields" in data["error"]

    def test_health_endpoint_response_structure(self, client):
        response = client.get("/health")
        assert response.is_json
        data = response.get_json()
        assert "status" in data
        assert "database" in data

# ============================================================================
# 3. Web UI Route Tests
# ============================================================================
class TestWebRoutes:
    def test_index_route(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Task" in response.data and b"Pipeline Dashboard" in response.data
        assert b"Live Calculator" in response.data
