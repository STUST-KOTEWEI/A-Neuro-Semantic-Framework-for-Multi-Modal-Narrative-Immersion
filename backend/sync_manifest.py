"""Sync Manifest utilities.

提供給前端 (Web/UI) 與多平台 App 的檔案同步機制：

核心理念：
1. 只暴露白名單檔案 (安全)
2. 回傳摘要 (sha256, mtime, size) 與分類，客戶端據此決定是否需拉取內容
3. 透過 etag（所有檔案 hash 合併再 hash）支援快取
4. 可增量請求單一檔案內容 (/sync/file)

客戶端策略建議：
1. 啟動時：GET /sync/manifest -> 比對本地 cache -> 下載需要更新的檔案
2. 定期（例如每 5 分鐘）輪詢 manifest 或使用 WebSocket (未來擴充)
3. 離線優先：若失敗使用本地快取
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
import os
import time

BASE_DIR = Path(__file__).resolve().parent.parent  # 專案根目錄 (推估)

# 可同步的檔案白名單 (相對於專案根目錄)
ALLOWED_SYNC_PATHS: List[str] = [
    "backend/lite_mode_handler.py",
    "backend/user_auth_dual.py",
    "models/ModernReader.modelfile",
    "models/ModernReaderLite.modelfile",
    "apps/watch/apple_watch_app.swift",
    "apps/watch/wear_os_app.kt",
    "apps/mobile/ios_app.swift",
    "apps/mobile/android_app.kt",
    "apps/desktop/macos_app.swift",
    "apps/desktop/windows_app.cs",
    "apps/desktop/linux_app.rs",
    "mobile/examples/flutter_app.dart",
    "mobile/examples/react_native_app.js",
    "mobile/examples/api_client.py",
    "clients/sync_client.py",
    "rag_store.json",
]

# 分類對應 (供 UI 分群顯示)
CATEGORY_MAP = {
    "backend": "server",
    "models": "model",
    "apps": "app",
    "mobile": "client-example",
    "rag_store.json": "rag",
}


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _classify(rel_path: str) -> str:
    top = rel_path.split("/", 1)[0]
    return CATEGORY_MAP.get(top, "misc")


def build_manifest(paths: Optional[List[str]] = None) -> Dict:
    """建構 manifest.

    :param paths: 若提供，僅處理此子集；必須屬於 ALLOWED_SYNC_PATHS
    :return: dict manifest
    """
    target_paths = paths if paths else ALLOWED_SYNC_PATHS
    invalid = [p for p in target_paths if p not in ALLOWED_SYNC_PATHS]
    if invalid:
        raise ValueError(f"Paths not allowed: {invalid}")

    files_meta = []
    combined = hashlib.sha256()
    for rel in target_paths:
        abs_path = BASE_DIR / rel
        if not abs_path.exists():
            # 可選：略過或標記 missing
            continue
        stat = abs_path.stat()
        file_hash = _file_sha256(abs_path)
        combined.update(file_hash.encode())
        files_meta.append(
            {
                "path": rel,
                "sha256": file_hash,
                "mtime": int(stat.st_mtime),
                "size": stat.st_size,
                "category": _classify(rel),
            }
        )

    etag = combined.hexdigest()
    return {
        "version": int(time.time()),  # 簡單使用時間戳為版本（避免快取混淆）
        "etag": etag,
        "file_count": len(files_meta),
        "files": files_meta,
    }


def get_feature_flags() -> Dict:
    """回傳功能旗標，未來可從設定或資料庫動態載入。"""
    return {
        "lite_mode": True,
        "dual_backend_auth": True,
        "custom_model_modern_reader": True,
        "custom_model_modern_reader_lite": True,
        "platforms": {
            "mobile": ["flutter", "react_native", "ios", "android"],
            "desktop": ["macos", "windows", "linux"],
            "watch": ["apple_watch", "wear_os"],
        },
        "sync_manifest": True,
    }


def read_file_content(rel_path: str) -> Dict:
    """讀取單一檔案內容並回傳文字 (UTF-8) 或 base64 (若二進位)。

    目前假設所有白名單檔案為文字檔。
    """
    if rel_path not in ALLOWED_SYNC_PATHS:
        raise ValueError("Path not allowed")
    abs_path = BASE_DIR / rel_path
    if not abs_path.exists():
        raise FileNotFoundError(rel_path)
    content = abs_path.read_text("utf-8")
    return {
        "path": rel_path,
        "content": content,
        "sha256": _file_sha256(abs_path),
        "mtime": int(abs_path.stat().st_mtime),
    }


__all__ = [
    "ALLOWED_SYNC_PATHS",
    "build_manifest",
    "get_feature_flags",
    "read_file_content",
]
