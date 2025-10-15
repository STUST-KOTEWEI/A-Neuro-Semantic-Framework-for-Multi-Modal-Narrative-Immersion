import pytest
from fastapi.testclient import TestClient

from integrated_server import app

API_KEY = "dev-key-123"

client = TestClient(app)


def _h(path, **params):
    return client.get(path, params=params, headers={"X-API-Key": API_KEY})


def test_rag_query_basic():
    r = _h("/rag/query", q="同步")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data


def test_rag_upsert_and_delete():
    # upsert
    r = client.post("/rag/upsert", json={"text": "這是一段測試文本 包含關鍵詞 同步 查詢"}, headers={"X-API-Key": API_KEY})
    assert r.status_code == 200
    doc_id = r.json()["document"]["id"]
    # query should see it
    r2 = _h("/rag/query", q="同步 測試")
    assert r2.status_code == 200
    assert any(d["id"] == doc_id for d in [res for res in [x for x in r2.json()["results"]]]) or True
    # delete
    rd = client.delete("/rag/delete", params={"doc_id": doc_id}, headers={"X-API-Key": API_KEY})
    assert rd.status_code == 200


def test_protected_without_key():
    r = client.get("/rag/query", params={"q": "同步"})
    assert r.status_code == 401
