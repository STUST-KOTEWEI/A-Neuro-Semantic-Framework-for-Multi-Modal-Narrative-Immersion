"""Simple CLI sync client for Modern Reader.

用法：
    python clients/sync_client.py --base http://localhost:8010 \
        --dest .cache/synced --interval 300

特性：
- 取得 /sync/manifest 比對差異
- 下載需要更新的檔案 /sync/file
- 儲存本地 manifest.json 供下次快啟
- 支援 ETag / If-None-Match
- 可選擇長輪詢或 WebSocket 即時更新
"""
from __future__ import annotations

import argparse
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys
import threading

import requests

try:
    import websocket  # type: ignore
except Exception:  # pragma: no cover
    websocket = None  # noqa

MANIFEST_FILENAME = "manifest.json"


def sha256_text(text: str) -> str:
    import hashlib
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return h


def load_local_manifest(dest: Path) -> Optional[Dict]:
    path = dest / MANIFEST_FILENAME
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return None


def save_local_manifest(dest: Path, manifest: Dict):
    (dest / MANIFEST_FILENAME).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), "utf-8")


def fetch_manifest(base: str, etag: Optional[str], api_key: Optional[str]) -> Tuple[Optional[Dict], Optional[str], int]:
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    if etag:
        headers["If-None-Match"] = etag
    r = requests.get(f"{base}/sync/manifest", headers=headers, timeout=20)
    if r.status_code == 304:
        return None, etag, r.status_code
    r.raise_for_status()
    new_etag = r.headers.get("ETag")
    return r.json(), new_etag, r.status_code


def fetch_file(base: str, path: str, api_key: Optional[str]) -> Dict:
    headers = {}
    if api_key:
        headers["X-API-Key"] = api_key
    r = requests.get(f"{base}/sync/file", params={"path": path}, headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def sync_once(base: str, dest: Path, api_key: Optional[str] = None, verbose: bool = True):
    ensure_dir(dest)
    local_manifest = load_local_manifest(dest)
    local_index = {f["path"]: f for f in local_manifest.get("files", [])} if local_manifest else {}
    prev_etag = local_manifest.get("etag") if local_manifest else None

    manifest, etag, status = fetch_manifest(base, prev_etag, api_key)
    if manifest is None:
        if verbose:
            print("[sync] 304 Not Modified - no changes")
        return

    if verbose:
        print(f"[sync] fetched manifest etag={etag} files={manifest['file_count']}")

    updated = []
    for f in manifest["files"]:
        lp = local_index.get(f["path"])  # type: ignore
        if (not lp) or lp.get("sha256") != f["sha256"]:
            # download file
            data = fetch_file(base, f["path"], api_key)
            target_file = dest / f["path"]
            ensure_dir(target_file.parent)
            target_file.write_text(data["content"], "utf-8")
            updated.append(f["path"])
            if verbose:
                print(f"  - updated {f['path']}")
    # Save manifest
    manifest_copy = manifest.copy()
    save_local_manifest(dest, manifest_copy)
    if verbose:
        print(f"[sync] done. updated={len(updated)}")


def ws_loop(base: str, dest: Path, api_key: Optional[str]):  # pragma: no cover - 互動迴圈
    if websocket is None:
        print("[ws] websocket-client 未安裝，跳過 WebSocket 模式。 pip install websocket-client")
        return

    url = base.replace("http", "ws") + "/ws/sync"
    # WebSocket 尚未驗證 API Key（若需可在 query 或 header 擴充）
    print(f"[ws] connecting {url}")

    def on_message(ws, message):  # type: ignore
        import json as _json
        try:
            data = _json.loads(message)
        except Exception:
            print("[ws] invalid message")
            return
        if data.get("type") == "update":
            print(f"[ws] update signal etag={data.get('etag')} -> syncing...")
            try:
                sync_once(base, dest, api_key=api_key)
            except Exception as e:
                print("[ws] sync error:", e)

    def on_error(ws, error):  # type: ignore
        print("[ws] error", error)

    def on_close(ws, *_):  # type: ignore
        print("[ws] closed. retry in 5s...")
        time.sleep(5)
        ws_loop(base, dest, api_key)

    def on_open(ws):  # type: ignore
        print("[ws] opened")

    ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever(ping_interval=30, ping_timeout=10)


def main():
    parser = argparse.ArgumentParser(description="Modern Reader Sync Client")
    parser.add_argument("--base", default="http://localhost:8010", help="Base URL of server")
    parser.add_argument("--dest", default=".sync-cache", help="Local dest directory")
    parser.add_argument("--interval", type=int, default=0, help="Polling interval seconds (0=once)")
    parser.add_argument("--ws", action="store_true", help="Enable WebSocket listen mode for push updates")
    parser.add_argument("--api-key", default=None, help="API Key for protected endpoints")
    args = parser.parse_args()

    dest = Path(args.dest)
    try:
        sync_once(args.base, dest, api_key=args.api_key)
    except Exception as e:
        print("Initial sync error:", e)
        sys.exit(1)

    if args.ws:
        t = threading.Thread(target=ws_loop, args=(args.base, dest, args.api_key), daemon=True)
        t.start()

    if args.interval > 0:
        try:
            while True:
                time.sleep(args.interval)
                sync_once(args.base, dest, api_key=args.api_key)
        except KeyboardInterrupt:
            print("bye")
    else:
        if args.ws:
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("bye")
if __name__ == "__main__":
    main()
