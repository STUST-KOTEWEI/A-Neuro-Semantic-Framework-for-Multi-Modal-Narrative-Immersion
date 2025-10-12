from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any, List, Optional

# 將專案根目錄加入 Python 路徑，以便引用 holo 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 匯入整合系統
from holo.integration import AIReaderIntegration

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


# 建立整合系統實例
integration = AIReaderIntegration()


class NarrativeRequest(BaseModel):
    text: str
    user_profile: Dict[str, Any] = {}


class ImmersionResponse(BaseModel):
    auditory_output: Dict[str, Any]
    sensory_output: Dict[str, Any]
    knowledge_graph: Dict[str, Any]


@app.get("/", summary="API 根目錄", description="檢查 API 是否正常運作")
async def read_root():
    return {"message": "歡迎使用 Project-HOLO API", "version": "0.2.0"}

@app.get("/subsystems/status", summary="子系統狀態", description="獲取所有子系統的運作狀態")
async def get_subsystem_status():
    """
    返回四個子系統的狀態：
    1. Image Recognition (圖像識別)
    2. AI Content Generation (內容生成)
    3. Multi-sensory Output (多感官輸出)
    4. UI & Control (使用者介面控制)
    """
    return integration.get_subsystem_status()

@app.post("/generate_immersion", response_model=ImmersionResponse, summary="生成沉浸式體驗", description="輸入敘事文本，生成對應的聽覺、感官與知識圖譜輸出")
async def generate_immersion(request: NarrativeRequest):
    """
    接收一段敘事文本，並回傳一個多模態的沉浸式體驗資料。

    - **text**: 必要，要處理的敘事文本。
    - **user_profile**: 可選，使用者的個人化設定。
    """
    # 使用整合系統生成完整體驗
    result = integration.generate_immersive_experience(
        request.text,
        request.user_profile
    )
    
    # 將結果轉換為回應格式
    auditory_data = {
        "podcast_script": result['content_generation']['podcast_script'],
        "background_music": result['multi_sensory']['background_music']
    }
    sensory_data = {
        "subtitles": result['multi_sensory']['subtitles'][:3],  # 返回前3條字幕作為示例
        "illustrations": result['multi_sensory']['illustrations']
    }
    kg_data = {
        "summary": result['content_generation']['summary'],
        "metadata": result['metadata']
    }

    return ImmersionResponse(
        auditory_output=auditory_data,
        sensory_output=sensory_data,
        knowledge_graph=kg_data,
    )

# 新增書籍掃描端點
class BookScanRequest(BaseModel):
    image_base64: str
    language: str = 'zh-TW'
    user_profile: Dict[str, Any] = {}

class BookScanResponse(BaseModel):
    ocr_result: Dict[str, Any]
    classification: Dict[str, Any]
    book_detection: Dict[str, Any]
    enriched_data: Dict[str, Any]
    status: str

@app.post("/scan_book", response_model=BookScanResponse, summary="掃描書籍", description="掃描書籍封面，識別文字並獲取書籍資訊")
async def scan_book(request: BookScanRequest):
    """
    掃描書籍封面圖像
    - **image_base64**: Base64編碼的圖像數據
    - **language**: OCR語言
    - **user_profile**: 使用者配置
    """
    import base64
    # 解碼base64圖像
    image_data = base64.b64decode(request.image_base64)
    
    # 使用整合系統處理書籍掃描
    result = integration.process_book_scan(image_data, request.user_profile)
    
    return BookScanResponse(**result)

@app.post("/upload_book_image", summary="上傳書籍圖像", description="上傳書籍封面圖像並進行識別")
async def upload_book_image(file: UploadFile = File(...)):
    """
    上傳書籍封面圖像文件
    """
    image_data = await file.read()
    result = integration.process_book_scan(image_data)
    return result

# 內容生成端點
class GenerateScriptRequest(BaseModel):
    content: str
    style: str = 'conversational'
    language: str = 'zh-TW'
    duration_minutes: int = 10

@app.post("/generate/script", summary="生成播客腳本", description="為書籍內容生成播客腳本")
async def generate_script(request: GenerateScriptRequest):
    """
    生成播客腳本
    """
    script = integration.script_generator.generate_podcast_script(
        request.content,
        request.style,
        request.language,
        request.duration_minutes
    )
    return script

class GenerateSummaryRequest(BaseModel):
    content: str
    summary_type: str = 'brief'
    language: str = 'zh-TW'
    max_length: int = 500

@app.post("/generate/summary", summary="生成摘要", description="為書籍內容生成摘要")
async def generate_summary(request: GenerateSummaryRequest):
    """
    生成書籍摘要
    """
    summary = integration.summary_generator.generate_summary(
        request.content,
        request.summary_type,
        request.language,
        request.max_length
    )
    return summary

# 個人化設定端點
class PersonalizationRequest(BaseModel):
    user_id: str
    settings: Optional[Dict[str, Any]] = None

@app.get("/personalization/{user_id}", summary="獲取個人化設定", description="獲取使用者的個人化設定")
async def get_personalization(user_id: str):
    """
    獲取使用者個人化設定
    """
    profile = integration.personalization_manager.get_user_profile(user_id)
    return profile

@app.post("/personalization/update", summary="更新個人化設定", description="更新使用者的個人化設定")
async def update_personalization(request: PersonalizationRequest):
    """
    更新個人化設定
    """
    if request.settings:
        success = integration.personalization_manager.import_settings(request.settings)
        return {"success": success, "settings": integration.personalization_manager.export_settings()}
    return {"success": False, "message": "No settings provided"}

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
