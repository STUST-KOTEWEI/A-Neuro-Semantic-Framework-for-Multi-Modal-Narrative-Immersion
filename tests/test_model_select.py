import pytest
from fastapi.testclient import TestClient
from integrated_server import app

API_KEY = "dev-key-123"
client = TestClient(app)


def _h(params):
    return client.get("/ai/model-select", params=params, headers={"X-API-Key": API_KEY})


def test_mobile_low_memory_uses_lite():
    r = _h({"device": "mobile", "memory_mb": 512})
    assert r.status_code == 200
    data = r.json()
    assert data["chosen"].endswith("Lite")
    assert "device-class" in data["reasons"] or "low-memory" in data["reasons"]


def test_watch_battery_saver():
    r = _h({"device": "watch", "memory_mb": 1024, "battery_saver": True})
    assert r.status_code == 200
    data = r.json()
    assert data["chosen"].endswith("Lite")
    assert "battery-saver" in data["reasons"] or "device-class" in data["reasons"]


def test_desktop_quality_override():
    # prefer_quality True with enough memory should pick full model
    r = _h({"device": "desktop", "memory_mb": 8192, "prefer_quality": True})
    assert r.status_code == 200
    data = r.json()
    assert data["chosen"].endswith("Reader") and not data["chosen"].endswith("Lite")
    assert "quality-override" in data["reasons"]


def test_model_select_requires_auth():
    r = client.get("/ai/model-select", params={"device": "mobile"})
    assert r.status_code == 401
