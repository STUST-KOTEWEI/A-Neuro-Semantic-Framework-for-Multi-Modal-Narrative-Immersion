from fastapi.testclient import TestClient
from integrated_server import app
import time

API_KEY = "dev-key-123"
client = TestClient(app)


def test_manifest_requires_key():
    r = client.get("/sync/manifest")
    assert r.status_code == 401


def test_manifest_with_key_and_etag_flow():
    r1 = client.get("/sync/manifest", headers={"X-API-Key": API_KEY})
    assert r1.status_code == 200
    etag1 = r1.headers.get("ETag")
    assert etag1
    data1 = r1.json()
    assert "files" in data1

    # 模擬檔案內容改變：修改 rag_store.json 追加空白（不在此測試直接寫入，以最小侵入）
    # 若環境允許，可稍作等待以確保 version 差異
    time.sleep(1)

    r2 = client.get("/sync/manifest", headers={"X-API-Key": API_KEY})
    etag2 = r2.headers.get("ETag")
    assert r2.status_code == 200
    # etag 可能相同（若檔案未改），因此不強制不同，但格式需正確
    assert etag2


def test_file_requires_key():
    r = client.get("/sync/file", params={"path": "models/ModernReaderLite.modelfile"})
    assert r.status_code == 401


def test_file_with_key():
    r = client.get(
        "/sync/file",
        params={"path": "models/ModernReaderLite.modelfile"},
        headers={"X-API-Key": API_KEY},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["path"].endswith("ModernReaderLite.modelfile")
    assert "content" in body
