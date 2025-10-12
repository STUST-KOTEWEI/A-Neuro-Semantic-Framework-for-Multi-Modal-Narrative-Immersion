from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any, List, Optional

# 將專案根目錄加入 Python 路徑，以便引用 holo 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 匯入 holo 專案的核心功能
try:
    from holo.vision import GoogleVisionAnalyzer, OCRProcessor
    from holo.generation import GPTGenerator
except ImportError as e:
    print(f"警告：無法匯入 holo 模組：{e}")
    GoogleVisionAnalyzer = None
    OCRProcessor = None
    GPTGenerator = None

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


# 建立處理器實例
vision_analyzer = GoogleVisionAnalyzer() if GoogleVisionAnalyzer else None
ocr_processor = OCRProcessor(lang='ch') if OCRProcessor else None
gpt_generator = GPTGenerator() if GPTGenerator else None


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

# 影像分析請求模型
class ImageAnalysisRequest(BaseModel):
    use_ocr: bool = True
    use_vision: bool = True

# 內容生成請求模型
class ContentGenerationRequest(BaseModel):
    text: str
    content_type: str = 'summary'  # summary, analysis, continuation, emoticon, podcast
    style: Optional[str] = 'narrative'
    duration_minutes: Optional[int] = 5

@app.post("/analyze_image", summary="影像識別與分析", description="上傳圖片進行情緒檢測、標籤識別和文字提取")
async def analyze_image(
    file: UploadFile = File(...),
    use_ocr: bool = True,
    use_vision: bool = True
):
    """
    分析上傳的圖片
    
    - **file**: 要分析的圖片文件
    - **use_ocr**: 是否使用 OCR 提取文字
    - **use_vision**: 是否使用 Vision API 檢測情緒和標籤
    """
    try:
        # 讀取圖片內容
        image_bytes = await file.read()
        
        result = {
            'filename': file.filename,
            'content_type': file.content_type
        }
        
        # 使用 Google Vision API 分析
        if use_vision and vision_analyzer:
            vision_result = vision_analyzer.analyze_image(image_bytes)
            result['vision_analysis'] = vision_result
        
        # 使用 PaddleOCR 提取文字
        if use_ocr and ocr_processor:
            ocr_result = ocr_processor.extract_text(image_bytes)
            result['ocr_result'] = ocr_result
        
        return result
    
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }

@app.post("/generate_content", summary="生成式 AI 內容生成", description="使用 GPT-4 生成表情文字、播客腳本等內容")
async def generate_content(request: ContentGenerationRequest):
    """
    生成各種 AI 內容
    
    - **text**: 輸入文本
    - **content_type**: 內容類型（summary, analysis, continuation, emoticon, podcast）
    - **style**: 風格（用於播客）
    - **duration_minutes**: 時長（用於播客）
    """
    if not gpt_generator:
        return {
            'error': 'GPT 生成器未初始化',
            'success': False
        }
    
    try:
        if request.content_type == 'emoticon':
            # 生成表情文字
            result = gpt_generator.generate_emoticon(
                emotion=request.text,
                context=request.style or ''
            )
        elif request.content_type == 'podcast':
            # 生成播客腳本
            result = gpt_generator.generate_podcast_script(
                text=request.text,
                style=request.style or 'narrative',
                duration_minutes=request.duration_minutes or 5
            )
        else:
            # 生成其他內容
            result = gpt_generator.generate_story_content(
                text=request.text,
                content_type=request.content_type
            )
        
        return result
    
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }

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
