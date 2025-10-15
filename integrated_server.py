"""Integrated FastAPI server exposing sync & feature flag endpoints.

此伺服器聚合：
1. 檔案同步 manifest (/sync/manifest)
2. 檔案內容擷取 (/sync/file)
3. 功能旗標 (/sync/feature-flags)

未來可整合：
- Lite Mode 檢測與切換
- AI 模型推論路由
- 使用者認證 (dual backend)
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect, Depends, Body, Header
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Set, Dict, Any
import asyncio
import hashlib
import time

from backend.sync_manifest import (
	build_manifest,
	get_feature_flags,
	read_file_content,
	ALLOWED_SYNC_PATHS,
)
from backend.config import ApiKeyDependency
from backend.rag_engine import query as rag_query_engine, upsert_doc, delete_doc, list_docs
from backend.user_auth_dual import DualBackendUserManager, UserRegistration, UserLogin, SubscriptionTier
from backend.cleanup_utils import clear_all

# Initialize user manager (JSON by default, SQL if enabled)
user_manager = DualBackendUserManager()


app = FastAPI(title="Modern Reader Integrated Server", version="0.1.0")

# 啟用 CORS，允許本地測試跨域請求
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # 本地測試用，生產環境應改為具體網域
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# --------------------------------------------------
# Static web frontend (serve files under ./web/frontend)
# --------------------------------------------------
try:  # 若目錄存在即掛載，否則忽略
	import os
	WEB_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'web', 'frontend')
	if os.path.isdir(WEB_FRONTEND_DIR):
		app.mount("/web", StaticFiles(directory=WEB_FRONTEND_DIR, html=True), name="web-frontend")
except Exception:  # pragma: no cover
	pass

# --------------------------------------------------
# WebSocket Sync Manager
# --------------------------------------------------
class SyncBroadcaster:
	def __init__(self):
		self.connections: Set[WebSocket] = set()
		self.last_etag: Optional[str] = None
		self.lock = asyncio.Lock()

	async def connect(self, ws: WebSocket):
		await ws.accept()
		self.connections.add(ws)
		# 初次傳送最新 manifest 摘要 (僅 etag)
		try:
			manifest = build_manifest()
			self.last_etag = manifest["etag"]
			await ws.send_json({"type": "welcome", "etag": self.last_etag, "file_count": manifest["file_count"]})
		except Exception as e:  # pragma: no cover
			await ws.send_json({"type": "error", "message": str(e)})

	def disconnect(self, ws: WebSocket):
		self.connections.discard(ws)

	async def broadcast(self, payload: dict):
		living = set()
		for ws in self.connections:
			try:
				await ws.send_json(payload)
				living.add(ws)
			except Exception:
				# 忽略失敗連線
				pass
		self.connections = living


broadcaster = SyncBroadcaster()


async def watch_changes(interval: float = 3.0):
	"""背景任務：週期性重建 manifest，etag 改變則廣播。"""
	await asyncio.sleep(1)  # 等待應用完全啟動
	while True:
		try:
			manifest = build_manifest()
			etag = manifest["etag"]
			if broadcaster.last_etag and etag != broadcaster.last_etag:
				await broadcaster.broadcast({
					"type": "update",
					"etag": etag,
					"changed": True,
					"ts": int(time.time()),
				})
			broadcaster.last_etag = etag
		except Exception as e:  # pragma: no cover
			# 可選：log 錯誤
			pass
		await asyncio.sleep(interval)


@app.on_event("startup")
async def _startup():  # pragma: no cover (啟動路徑通常不測試)
	asyncio.create_task(watch_changes())


@app.on_event("shutdown")
async def _shutdown():  # pragma: no cover
	try:
		_ = clear_all(restart_ollama=True, clear_torch=True)
	except Exception:
		# 靜默失敗，避免關閉流程卡住
		pass

@app.get("/health")
async def health():
	return {"status": "ok"}


@app.get("/sync/manifest")
async def sync_manifest(
	paths: Optional[str] = Query(None, description="逗號分隔的相對路徑子集"),
	_auth: str = ApiKeyDependency,
):
	try:
		subset: Optional[List[str]] = None
		if paths:
			subset = [p.strip() for p in paths.split(",") if p.strip()]
		manifest = build_manifest(subset)
		return JSONResponse(manifest, headers={"ETag": manifest["etag"]})
	except ValueError as ve:
		raise HTTPException(status_code=400, detail=str(ve))
	except Exception as e:  # pragma: no cover
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/file")
async def sync_file(
	path: str = Query(..., description="相對路徑 (白名單內)"),
	_auth: str = ApiKeyDependency,
):
	try:
		data = read_file_content(path)
		return data
	except ValueError as ve:
		raise HTTPException(status_code=400, detail=str(ve))
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as e:  # pragma: no cover
		raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/feature-flags")
async def feature_flags(_auth: str = ApiKeyDependency):
	return get_feature_flags()


@app.get("/sync/allowed-paths")
async def allowed_paths(_auth: str = ApiKeyDependency):
	return {"allowed": ALLOWED_SYNC_PATHS}


# --------------------------------------------------
# Model selection endpoint (auto downgrade logic)
# --------------------------------------------------
@app.get("/ai/model-select")
async def model_select(
	device: str = Query("desktop", description="device type: desktop|mobile|watch"),
	memory_mb: int = Query(4096, ge=64, description="Approx available RAM"),
	battery_saver: bool = Query(False),
	prefer_quality: bool = Query(False),
	_auth: str = ApiKeyDependency,
):
	flags = get_feature_flags()
	full_model = "ModernReader"
	lite_model = "ModernReaderLite"
	use_lite = False
	reasons = []
	if device in ("mobile", "watch"):
		use_lite = True
		reasons.append("device-class")
	if memory_mb < 2048:
		use_lite = True
		reasons.append("low-memory")
	if battery_saver:
		use_lite = True
		reasons.append("battery-saver")
	if prefer_quality and not battery_saver and memory_mb >= 4096:
		# Override to full if user explicitly prefers quality and resources sufficient
		use_lite = False
		reasons.append("quality-override")
	chosen = lite_model if use_lite and flags.get("custom_model_modern_reader_lite") else full_model
	return {
		"chosen": chosen,
		"fallback": lite_model if chosen == full_model else full_model,
		"reasons": reasons,
		"flags": {
			"lite": flags.get("custom_model_modern_reader_lite"),
			"full": flags.get("custom_model_modern_reader"),
		},
	}


# --------------------------------------------------
@app.get("/rag/query")
async def rag_query(q: str = Query(..., min_length=1), top_k: int = Query(3, ge=1, le=20), _auth: str = ApiKeyDependency):
	result = rag_query_engine(q, top_k=top_k)
	return result


@app.get("/rag/list")
async def rag_list(_auth: str = ApiKeyDependency):
	return {"documents": list_docs(), "count": len(list_docs())}


@app.post("/rag/upsert")
async def rag_upsert(
	text: str = Body(..., embed=True, description="Document text"),
	doc_id: str | None = Body(None),
	meta: dict | None = Body(None),
	_auth: str = ApiKeyDependency,
):
	doc = upsert_doc(text=text, doc_id=doc_id, meta=meta)
	return {"success": True, "document": doc}


@app.delete("/rag/delete")
async def rag_delete(doc_id: str = Query(...), _auth: str = ApiKeyDependency):
	ok = delete_doc(doc_id)
	if not ok:
		raise HTTPException(status_code=404, detail="Document not found")
	return {"success": True, "deleted": doc_id}


if __name__ == "__main__":  # 本地開發啟動
	import uvicorn

	uvicorn.run("integrated_server:app", host="0.0.0.0", port=8010, reload=True)


@app.websocket("/ws/sync")
async def ws_sync(ws: WebSocket):
	await broadcaster.connect(ws)
	try:
		while True:
			# 目前僅保持連線，可擴充客戶端訊息類型
			_ = await ws.receive_text()
			await ws.send_json({"type": "pong"})
	except WebSocketDisconnect:
		broadcaster.disconnect(ws)
	except Exception:
		broadcaster.disconnect(ws)


# --------------------------------------------------
# ModernReader Feature APIs - 從 SQL 讀取實際數據
# --------------------------------------------------
import sqlite3
import json

def get_db_connection():
	"""建立資料庫連線"""
	return sqlite3.connect("modernreader.db")

@app.get("/data/users")
async def data_users():
	"""查詢用戶數據"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, email, username, subscription_tier FROM users LIMIT 10")
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","email","username","subscription_tier"], r)) for r in rows]}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/book-covers")
async def data_book_covers():
	"""查詢書籍封面數據 (ISBN)"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, isbn, title, author, cover_image_url, description FROM book_covers")
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","isbn","title","author","cover_image_url","description"], r)) for r in rows]}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/podcasts")
async def data_podcasts():
	"""查詢播客內容數據 (TTS)"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, title, content, audio_url, duration FROM podcast_contents")
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","title","content","audio_url","duration"], r)) for r in rows]}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/emotions")
async def data_emotions():
	"""查詢情感偵測數據 (STT)"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, audio_text, emotion, confidence, timestamp FROM emotion_detections ORDER BY timestamp DESC")
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","audio_text","emotion","confidence","timestamp"], r)) for r in rows]}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/nlp")
async def data_nlp():
	"""查詢 NLP 分析結果"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, text, analysis_type, result FROM nlp_analyses")
		rows = cur.fetchall()
		conn.close()
		data = []
		for r in rows:
			item = dict(zip(["id","text","analysis_type","result"], r))
			try:
				item["result"] = json.loads(item["result"])
			except:
				pass
			data.append(item)
		return {"data": data}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/rag-images")
async def data_rag_images():
	"""查詢 RAG 搜圖結果"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		cur.execute("SELECT id, query, image_url, description, relevance_score FROM rag_images")
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","query","image_url","description","relevance_score"], r)) for r in rows]}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/data/rag-images/search")
async def data_rag_images_search(q: str = Query(..., min_length=1), top_k: int = Query(1, ge=1, le=50)):
	"""根據關鍵字搜尋 RAG 圖像，預設回傳 1 張代表圖。"""
	try:
		conn = get_db_connection()
		cur = conn.cursor()
		# 以 relevance_score 排序，LIKE 模糊匹配 query 與 description
		cur.execute(
			"""
			SELECT id, query, image_url, description, relevance_score
			FROM rag_images
			WHERE (query LIKE ? OR description LIKE ?)
			ORDER BY relevance_score DESC
			LIMIT ?
			""",
			(f"%{q}%", f"%{q}%", top_k),
		)
		rows = cur.fetchall()
		conn.close()
		return {"data": [dict(zip(["id","query","image_url","description","relevance_score"], r)) for r in rows], "count": len(rows), "q": q}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 保留舊的 /data/sql 端點以相容性
@app.get("/data/sql")
async def data_sql():
	"""Demo: 查詢用戶數據（相容舊端點）"""
	return await data_users()
from pydantic import BaseModel
from pydantic import EmailStr
from uuid import uuid4


"""
注意：上方的認證 stub 已移除。請使用下方整合 DualBackendUserManager 的正式 /auth/* 端點。
"""


@app.post("/admin/clear_cache")
async def admin_clear_cache(
	restart_ollama: bool = True,
	clear_torch: bool = True,
	_auth: str = ApiKeyDependency,
):
	"""手動觸發清理快取（VRAM/服務/torch）。需要 API 金鑰。"""
	report = clear_all(restart_ollama=restart_ollama, clear_torch=clear_torch)
	return {"success": True, "report": report}

# --------------------------------------------------
# Emotion-Based Content Generation API
# --------------------------------------------------
class EmotionDetectRequest(BaseModel):
	image_base64: str


class CompleteGenerationRequest(BaseModel):
	"""已廢除：完整內容生成流程請求模型（保留型別以相容，但端點已移除）。"""
	camera_image_base64: str
	query: str
	total_count: int = 100


@app.post("/api/detect-emotion")
async def api_detect_emotion(payload: EmotionDetectRequest):
	"""
	檢測鏡頭捕獲圖像中的表情情緒
	"""
	try:
		from backend.emotion_based_generator import EmotionBasedGenerator
		generator = EmotionBasedGenerator()
		emotion_data = generator.detect_emotion_from_camera(payload.image_base64)
		return emotion_data
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Emotion detection error: {str(e)}")


@app.post("/api/generate-complete")
async def api_generate_complete(_: CompleteGenerationRequest):  # pragma: no cover
	"""
	此端點已停用：依您的需求，先專注於 RAG 資料庫，移除生成內容流程。
	回覆 410 Gone 以告知前端此功能暫不提供。
	"""
	raise HTTPException(status_code=410, detail="/api/generate-complete 已停用。請改用 /rag/* 檢索與資料管理端點。")


# --------------------------------------------------
# Auth API (register/login/me) & Billing
# --------------------------------------------------
class RegisterRequest(BaseModel):
	email: EmailStr
	username: str
	password: str
	subscription_tier: str | None = None


class LoginRequest(BaseModel):
	email: Optional[EmailStr] = None
	username: Optional[str] = None
	password: str


class SubscribeRequest(BaseModel):
	tier: str


def get_current_user(authorization: str = Header(default="")) -> Dict[str, Any]:
	"""Extract current user from Bearer token"""
	if not authorization.startswith("Bearer "):
		raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
	token = authorization.split(" ", 1)[1].strip()
	payload = user_manager.verify_jwt_token(token)
	if not payload:
		raise HTTPException(status_code=401, detail="Invalid or expired token")
	user = user_manager.get_user_by_id(payload.get("user_id", ""))
	if not user:
		raise HTTPException(status_code=401, detail="User not found")
	return user


@app.post("/auth/register")
async def auth_register(payload: RegisterRequest):
	try:
		reg = UserRegistration(
			email=payload.email,
			username=payload.username,
			password=payload.password,
			subscription_tier=SubscriptionTier(payload.subscription_tier) if payload.subscription_tier else SubscriptionTier.FREE
		)
		result = user_manager.register_user(reg)
		return result
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Register failed: {str(e)}")


@app.post("/auth/login")
async def auth_login(payload: LoginRequest):
	try:
		login = UserLogin(email=payload.email, username=payload.username, password=payload.password)
		result = user_manager.login_user(login)
		return result
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Login failed: {str(e)}")


@app.get("/auth/me")
async def auth_me(current_user: Dict[str, Any] = Depends(get_current_user)):
	return {"user": current_user}


@app.post("/billing/subscribe")
async def billing_subscribe(payload: SubscribeRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
	tier = payload.tier.lower()
	allowed = {"free", "edu", "plus", "pro"}
	if tier not in allowed:
		raise HTTPException(status_code=400, detail="Invalid tier")
	# Update in JSON backend (demo). SQL not fully implemented in manager, so we mutate here.
	user_id = current_user["id"]
	updated = False
	for u in user_manager.users_db:
		if u["id"] == user_id:
			u["subscription_tier"] = tier
			updated = True
			break
	if updated:
		user_manager._save_users_db()  # type: ignore
		return {"success": True, "new_tier": tier}
	raise HTTPException(status_code=500, detail="Failed to update subscription")


# --------------------------------------------------
# Chat plugin API (session, send, history, emotion stream)
# --------------------------------------------------
from backend.chat_plugin import ChatService
chat_service = ChatService(db_path="modernreader.db")


class ChatStartRequest(BaseModel):
	topic: Optional[str] = None


class ChatSendRequest(BaseModel):
	session_id: int
	text: str
	emotion: Optional[str] = None
	intensity: Optional[float] = None


class ChatEmotionPushRequest(BaseModel):
	session_id: int
	emotion: str
	intensity: float
	source: str = "camera"


@app.post("/chat/start")
async def chat_start(payload: ChatStartRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
	session_id = chat_service.start_session(user_id=current_user["id"], topic=payload.topic)
	return {"session_id": session_id}


@app.post("/chat/send")
async def chat_send(payload: ChatSendRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
	reply = chat_service.handle_message(
		session_id=payload.session_id,
		user_id=current_user["id"],
		text=payload.text,
		emotion=payload.emotion,
		intensity=payload.intensity
	)
	return reply


@app.get("/chat/history")
async def chat_history(session_id: int, limit: int = 50, current_user: Dict[str, Any] = Depends(get_current_user)):
	messages = chat_service.get_history(session_id=session_id, user_id=current_user["id"], limit=limit)
	return {"messages": messages}


@app.post("/chat/emotion")
async def chat_push_emotion(payload: ChatEmotionPushRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
	chat_service.push_emotion(
		session_id=payload.session_id,
		user_id=current_user["id"],
		emotion=payload.emotion,
		intensity=payload.intensity,
		source=payload.source
	)
	return {"success": True}


# --------------------------------------------------
# Voice Engine API - TTS & STT
# --------------------------------------------------
class TTSRequest(BaseModel):
	text: str
	voice: str = "alloy"
	emotion: str | None = None
	speed: float = 1.0


class STTRequest(BaseModel):
	audio_base64: str
	language: str = "zh-TW"


@app.post("/api/tts")
async def api_text_to_speech(payload: TTSRequest):
	"""
	文字轉語音 (TTS)
	"""
	try:
		from backend.voice_engine import voice_controller
		result = voice_controller.speak(
			text=payload.text,
			emotion=payload.emotion,
			voice=payload.voice
		)
		return result
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@app.post("/api/stt")
async def api_speech_to_text(payload: STTRequest):
	"""
	語音轉文字 (STT)
	"""
	try:
		import base64
		from backend.voice_engine import voice_controller
		
		audio_data = base64.b64decode(payload.audio_base64)
		result = voice_controller.listen(audio_data)
		return result
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")


# --------------------------------------------------
# Multi-Sensory Hub API
# --------------------------------------------------
class BroadcastRequest(BaseModel):
	emotion: str
	intensity: float
	devices: List[str]
	content: Dict[str, Any] | None = None


@app.post("/api/broadcast-to-devices")
async def api_broadcast_to_devices(payload: BroadcastRequest):
	"""
	合作預留區：多感官設備廣播。
	目前僅回傳占位資訊，尚未與任何外部廠商或硬體做實際串接。
	"""
	return {
		"placeholder": True,
		"message": "多感官設備為合作預留區，尚未啟用實體廣播。",
		"requested": {
			"emotion": payload.emotion,
			"intensity": payload.intensity,
			"devices": payload.devices,
			"content": payload.content or {},
		},
		"next_step": "待與校內圖書館或外部廠商確認合作後再開啟。"
	}


@app.get("/api/devices/connected")
async def api_get_connected_devices():
	"""
	合作預留區：目前未實際連接外部設備，回傳空清單與說明。
	"""
	return {"devices": [], "count": 0, "placeholder": True, "message": "設備連接為合作預留區，尚未啟用。"}


