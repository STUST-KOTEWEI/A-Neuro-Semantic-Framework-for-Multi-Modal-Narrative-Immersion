"""Simple persistent RAG engine.

Features:
 - JSON file backed store (rag_store.json) under project root.
 - Upsert (auto id) / list / delete / query.
 - Naive scoring: token overlap count + optional length prior.
 - Embedding stub hook (future integration).
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Optional, Iterable

STORE_PATH = Path(__file__).resolve().parent.parent / "rag_store.json"


def _load() -> Dict:
    if not STORE_PATH.exists():
        return {"documents": []}
    try:
        return json.loads(STORE_PATH.read_text("utf-8"))
    except Exception:
        return {"documents": []}


def _save(data: Dict):
    STORE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")


def list_docs() -> List[Dict]:
    return _load().get("documents", [])


def upsert_doc(text: str, doc_id: Optional[str] = None, meta: Optional[Dict] = None) -> Dict:
    data = _load()
    docs = data.setdefault("documents", [])
    if doc_id:
        # replace if exists
        for d in docs:
            if d["id"] == doc_id:
                d.update({
                    "text": text,
                    "meta": meta or d.get("meta") or {},
                    "updated_at": int(time.time()),
                })
                _save(data)
                return d
    new_id = doc_id or str(uuid.uuid4())
    doc = {
        "id": new_id,
        "text": text,
        "meta": meta or {},
        "created_at": int(time.time()),
        "updated_at": int(time.time()),
    }
    docs.append(doc)
    _save(data)
    return doc


def delete_doc(doc_id: str) -> bool:
    data = _load()
    docs = data.get("documents", [])
    before = len(docs)
    docs = [d for d in docs if d["id"] != doc_id]
    data["documents"] = docs
    _save(data)
    return len(docs) != before


def _tokenize(s: str) -> List[str]:
    return [t for t in s.lower().replace("\n", " ").split() if t]


def query(q: str, top_k: int = 3) -> Dict:
    tokens = set(_tokenize(q))
    docs = list_docs()
    scored = []
    for d in docs:
        dtokens = set(_tokenize(d["text"]))
        overlap = len(tokens & dtokens)
        if overlap == 0:
            continue
        # simple heuristic: overlap + small bonus for shorter docs
        length_bonus = max(0.1, 100 / (len(d["text"]) + 10))
        score = overlap + length_bonus
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for score, d in scored[:top_k]:
        entry = {k: v for k, v in d.items()}
        entry["score"] = round(score, 4)
        results.append(entry)
    return {"query": q, "results": results, "count": len(results)}


__all__ = [
    "upsert_doc",
    "delete_doc",
    "list_docs",
    "query",
    "STORE_PATH",
]
