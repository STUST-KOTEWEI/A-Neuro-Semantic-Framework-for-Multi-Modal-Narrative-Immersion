from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any, List

# 將專案根目錄加入 Python 路徑，以便引用 holo 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 這裡可以匯入您 holo 專案的核心功能
# from holo.main import HoloProcessor # 假設這是您的主要處理類別

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


# 建立一個處理器實例 (請根據您的實際架構調整)
# processor = HoloProcessor()


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
