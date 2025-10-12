from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any, List

# 將專案根目錄加入 Python 路徑，以便引用 holo 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the orchestrator
from holo.orchestrator import Orchestrator

app = FastAPI(
    title="Project-HOLO API",
    description="提供神經語意框架的多模態敘事沉浸體驗 API",
    version="0.1.0",
)

# 設定 CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # React 前端開發伺服器
    "capacitor://localhost",  # Capacitor App
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize the orchestrator
orchestrator_config = {
    'connectors': {
        'textPreprocessor': {'type': 'http', 'url': 'https://your-backend/api/preprocess'},
        'vectorDB': {'type': 'pinecone', 'index': 'user_sessions'},
        'emotionModelAPI': {'type': 'http', 'url': 'https://your-backend/api/emotion/predict'},
        'TTS': {'type': 'http', 'url': 'https://api.elevenlabs.io/v1/text-to-speech'},
        'bhapticsSDK': {'type': 'http', 'url': 'https://your-backend/api/device/haptics'},
        'aromajoinAPI': {'type': 'http', 'url': 'https://your-backend/api/device/scent'},
        'postgres': {'type': 'sql', 'connection': 'postgres://...'}
    }
}
orchestrator = Orchestrator(orchestrator_config)


class NarrativeRequest(BaseModel):
    text: str
    user_profile: Dict[str, Any] = {}


class ImmersionResponse(BaseModel):
    auditory_output: Dict[str, Any]
    sensory_output: Dict[str, Any]
    knowledge_graph: Dict[str, Any]


@app.get("/", summary="API 根目錄", description="檢查 API 是否正常運作")
async def read_root():
    return {"message": "歡迎使用 Project-HOLO API"}

@app.post("/generate_immersion", response_model=ImmersionResponse, summary="生成沉浸式體驗", description="輸入敘事文本，生成對應的聽覺、感官與知識圖譜輸出")
async def generate_immersion(request: NarrativeRequest):
    """
    接收一段敘事文本，並回傳一個多模態的沉浸式體驗資料。

    - **text**: 必要，要處理的敘事文本。
    - **user_profile**: 可選，使用者的個人化設定。
    """
    # --- 在這裡呼叫您 holo 專案的核心邏輯 ---
    # 範例:
    # results = processor.process(request.text, request.user_profile)
    # auditory_data = results.get("auditory")
    # sensory_data = results.get("sensory")
    # kg_data = results.get("knowledge_graph")
    # -----------------------------------------

    # 模擬回傳資料
    auditory_data = {"soundscape": "forest_night.wav", "effects": ["wind", "crickets"]}
    sensory_data = {"haptic": "gentle_breeze", "neuro": "calm_alpha_wave"}
    kg_data = {
        "nodes": ["forest", "night"],
        "edges": [("forest", "has_ambience", "night")],
    }

    return ImmersionResponse(
        auditory_output=auditory_data,
        sensory_output=sensory_data,
        knowledge_graph=kg_data,
    )

# 若要直接執行此檔案進行測試: uvicorn main:app --reload

from fastapi import Response
from gtts import gTTS
import io

class TTSRequest(BaseModel):
    text: str
    lang: str = 'en'

@app.post("/tts", summary="Text-to-Speech", description="Converts text to speech and returns an audio file.")
async def text_to_speech(request: TTSRequest):
    """
    Converts text to speech.

    - **text**: The text to convert.
    - **lang**: The language of the text.
    """
    tts = gTTS(text=request.text, lang=request.lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return Response(fp.read(), media_type="audio/mpeg")


# ========== Orchestrator Endpoints ==========

class PlayRequest(BaseModel):
    text: str
    user_id: str = "default"


class PlayResponse(BaseModel):
    playback_url: str
    metadata: Dict[str, Any]


@app.post("/orchestrator/play", response_model=PlayResponse, summary="開始播放", description="開始播放文本並生成多感官體驗")
async def orchestrator_play(request: PlayRequest):
    """
    Start playback of text with multisensory experience.
    
    - **text**: The text content to play
    - **user_id**: User identifier for preferences
    """
    result = await orchestrator.play(request.text, request.user_id)
    
    if 'error' in result:
        return {"playback_url": "", "metadata": {"error": result['error']}}
    
    return result


class PauseResponse(BaseModel):
    status: str
    current_segment: int
    is_playing: bool


@app.post("/orchestrator/pause", response_model=PauseResponse, summary="暫停播放", description="暫停當前播放")
async def orchestrator_pause():
    """
    Pause current playback.
    """
    result = await orchestrator.pause()
    return result


class SeekRequest(BaseModel):
    segment_index: int


class SeekResponse(BaseModel):
    status: str
    current_segment: int
    playback_url: str
    segment_text: str
    segment_duration: float


@app.post("/orchestrator/seek", response_model=SeekResponse, summary="跳轉到段落", description="跳轉到指定的文本段落")
async def orchestrator_seek(request: SeekRequest):
    """
    Seek to a specific segment.
    
    - **segment_index**: Index of the segment to seek to
    """
    result = await orchestrator.seek(request.segment_index)
    
    if 'error' in result:
        return {
            "status": "error",
            "current_segment": result.get('current_segment', 0),
            "playback_url": "",
            "segment_text": "",
            "segment_duration": 0.0
        }
    
    return result


class SummaryResponse(BaseModel):
    summary: str
    total_segments: int
    total_highlights: int
    emotion: str
    current_position: int
    is_playing: bool


@app.get("/orchestrator/summary", response_model=SummaryResponse, summary="獲取摘要", description="獲取當前會話的摘要信息")
async def orchestrator_summary():
    """
    Get summary of current session.
    """
    result = await orchestrator.summary()
    return result
