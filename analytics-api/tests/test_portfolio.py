from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

VITALIK = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

def test_health():
    res = client.get("/health")
    assert res.status_code == 200

def test_invalid_address():
    res = client.get("/analytics/portfolio/notanaddress")
    assert res.status_code == 400

def test_portfolio_structure():
    with patch("services.portfolio_service.get_full_portfolio") as mock:
        mock.return_value = {
            "address": VITALIK,
            "total_value_usd": 1000.0,
            "holdings": [],
            "token_count": 0
        }
        res = client.get(f"/analytics/portfolio/{VITALIK}")
        assert res.status_code == 200
        data = res.json()
        assert "holdings" in data
        assert "total_value_usd" in data
