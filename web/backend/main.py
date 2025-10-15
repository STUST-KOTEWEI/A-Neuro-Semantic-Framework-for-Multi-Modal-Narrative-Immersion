from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import uvicorn
import os as _os

# Lite mode flag (for mobile/watch optimization)
LITE_MODE = _os.getenv("LITE_MODE", "0") == "1"

# Load environment variables
load_dotenv()

# 將專案根目錄加入 Python 路徑，以便引用 holo 模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import lite mode handler
from backend.lite_mode_handler import (
    LiteModeHandler, 
    MockTextSegmenter, 
    MockTTSEngine, 
    MockHapticsEmulator,
    MockImageSelector, 
    MockImageCaptioner
)

# Conditional imports based on LITE_MODE
if not LITE_MODE:
    # Full features for desktop/web
    try:
        from holo.ingestion.text_segmenter import TextSegmenter
        from holo.auditory.elevenlabs_tts import get_tts_engine
        from holo.sensory.haptics_emulator import HapticsEmulator
        from backend.ai_image_selector import AIImageSelector
        from backend.ai_image_captioner import AIImageCaptioner
    except ImportError as e:
        print(f"Warning: Full features not available: {e}")
        LITE_MODE = True

# Always import essential modules
from backend.ai_text_generator import AITextGenerator
from backend.user_auth_dual import UserManager, UserRegistration, UserLogin, SubscriptionTier
from backend.cleanup_utils import clear_all

app = FastAPI(
    title="Project-HOLO API",
    description="提供神經語意框架的多模態敘事沉浸體驗 API",
    version="0.1.0",
)


@app.on_event("shutdown")
async def _shutdown_cleanup():  # pragma: no cover
    try:
        _ = clear_all(restart_ollama=True, clear_torch=True)
    except Exception:
        # 靜默錯誤，避免關閉流程阻塞
        pass

@app.get("/health", summary="健康檢查", tags=["system"])
async def health_check():
    return {
        "status": "ok",
        "lite_mode": LITE_MODE,
        "version": "0.1.0"
    }

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


# Initialize components based on LITE_MODE
lite_handler = LiteModeHandler(LITE_MODE)

if not LITE_MODE:
    # Full features for desktop/web
    text_segmenter = TextSegmenter()
    tts_engine = get_tts_engine()
    haptics_emulator = HapticsEmulator()
    ai_image_selector = AIImageSelector()
    ai_image_captioner = AIImageCaptioner()
else:
    # Lite alternatives for mobile/watch
    text_segmenter = MockTextSegmenter()
    tts_engine = MockTTSEngine()
    haptics_emulator = MockHapticsEmulator()
    ai_image_selector = MockImageSelector()
    ai_image_captioner = MockImageCaptioner()

# Always initialize essential components
ai_text_generator = AITextGenerator()
user_manager = UserManager()
security = HTTPBearer()

# Mount static files for serving images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount frontend files - fix the directory path
app.mount("/frontend", StaticFiles(directory="web/frontend"), name="frontend")


# 清理端點類型與路由將置於 get_current_user 定義之後，避免靜態分析未定義。


# Serve the new reader.html as default - dynamic path to project root
@app.get("/", summary="首頁", description="提供 AI 多感官閱讀器介面")
async def read_root():
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    html_path = os.path.join(project_root, "web", "frontend", "reader.html")
    if not os.path.exists(html_path):
        return FileResponse(path=os.path.join(project_root, "static", "404.html"), status_code=404) if os.path.exists(os.path.join(project_root, "static", "404.html")) else HTTPException(status_code=404, detail="HTML file not found")
    return FileResponse(html_path)


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    payload = user_manager.verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_manager.get_user_by_id(payload['user_id'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Optional authentication dependency
async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Optional authentication - returns None if no valid token provided
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


class NarrativeRequest(BaseModel):
    text: str
    user_profile: Dict[str, Any] = {}


class ImmersionResponse(BaseModel):
    auditory_output: Dict[str, Any]
    sensory_output: Dict[str, Any]
    image_output: Dict[str, Any]
    enhanced_text: Dict[str, Any]
    knowledge_graph: Dict[str, Any]


class ClearCacheRequest(BaseModel):
    restart_ollama: bool = True
    clear_torch: bool = True


@app.post("/admin/clear_cache", summary="Clear AI caches (VRAM)", description="Stops Ollama models, restarts service on macOS, and clears PyTorch CUDA/MPS cache if available.")
async def admin_clear_cache(request: ClearCacheRequest, _user=Depends(get_current_user)):
    report = clear_all(restart_ollama=request.restart_ollama, clear_torch=request.clear_torch)
    return {"success": True, "report": report}


@app.post("/generate_immersion", response_model=ImmersionResponse, summary="生成沉浸式體驗", description="輸入敘事文本，生成對應的聽覺、感官、視覺與知識圖譜輸出")
async def generate_immersion(request: NarrativeRequest):
    """
    接收一段敘事文本，並回傳一個多模態的沉浸式體驗資料。

    - **text**: 必要，要處理的敘事文本。
    - **user_profile**: 可選，使用者的個人化設定。
    """
    # Use Week 1 Sprint features: text segmentation and haptics
    segments_data = text_segmenter.get_segments_with_metadata(request.text)
    haptic_pattern = haptics_emulator.generate_from_text(request.text)
    
    # AI-enhanced text generation
    enhanced_text_result = ai_text_generator.enhance_narrative_text(
        request.text, 
        style="immersive", 
        use_google=True
    )
    
    # AI image selection based on emotion
    image_selection_result = ai_image_selector.select_images_for_text(
        request.text, 
        count=3
    )
    
    # Build auditory output with TTS info
    auditory_data = {
        "tts_engine": "ElevenLabs" if not hasattr(tts_engine, 'is_fallback') else "gTTS (fallback)",
        "segments": segments_data["total_segments"],
        "available_voices": tts_engine.get_available_voices(),
        "processing_time": "estimated_2s"
    }
    
    # Build sensory output with haptics
    haptic_events = haptic_pattern.get("events", []) if isinstance(haptic_pattern, dict) else []
    emotion_analysis = image_selection_result.get("emotion_analysis", {})
    sensory_data = {
        "haptic_pattern": haptic_pattern,
        "haptic_events_count": len(haptic_events) if isinstance(haptic_events, list) else 0,
        "emotion_detected": emotion_analysis.get("emotion", "neutral") if isinstance(emotion_analysis, dict) else "neutral",
        "emotion_intensity": emotion_analysis.get("intensity", 0.5) if isinstance(emotion_analysis, dict) else 0.5,
        "neuro": "calm_alpha_wave"
    }
    
    # Build image output with AI-selected images
    image_data = {
        "selected_images": image_selection_result["selected_images"],
        "emotion_analysis": image_selection_result["emotion_analysis"],
        "total_available": image_selection_result["total_available"],
        "selection_criteria": "emotion_based"
    }
    
    # Enhanced text data
    enhanced_text_data = {
        "original_text": request.text,
        "enhanced_text": enhanced_text_result.get("generated_text", request.text),
        "enhancement_success": enhanced_text_result.get("success", False),
        "enhancement_style": enhanced_text_result.get("enhancement_style", "immersive"),
        "model_used": enhanced_text_result.get("model", "unknown")
    }
    
    # Knowledge graph (enhanced with AI data)
    segments = segments_data.get("segments", [])
    segments_list = segments[:3] if isinstance(segments, list) else []
    keywords = emotion_analysis.get("keywords", []) if isinstance(emotion_analysis, dict) else []
    kg_data = {
        "segments": segments_list,  # First 3 segments as example
        "text_length": segments_data.get("total_length", 0),
        "processing_strategy": segments_data.get("strategy_used", "unknown"),
        "detected_themes": keywords,
        "ai_enhancement_available": enhanced_text_result.get("success", False)
    }

    return ImmersionResponse(
        auditory_output=auditory_data,
        sensory_output=sensory_data,
        image_output=image_data,
        enhanced_text=enhanced_text_data,
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
    Converts text to speech using available TTS engine.

    - **text**: The text to convert.
    - **lang**: The language of the text.
    """
    # Use the TTS engine (ElevenLabs if available, gTTS as fallback)
    fp = tts_engine.text_to_speech(request.text)
    return Response(fp.read(), media_type="audio/mpeg")


class SegmentRequest(BaseModel):
    text: str
    strategy: str = "adaptive"


@app.post("/segment_text", summary="Segment Text", description="Segments narrative text into chunks for processing.")
async def segment_text(request: SegmentRequest):
    """
    Segments text into meaningful chunks.
    
    - **text**: The text to segment.
    - **strategy**: Segmentation strategy ("sentences", "paragraphs", "adaptive").
    """
    result = text_segmenter.get_segments_with_metadata(request.text, strategy=request.strategy)
    return result


class HapticRequest(BaseModel):
    text: Optional[str] = None
    emotion: Optional[str] = None
    intensity: float = 0.5


@app.post("/generate_haptics", summary="Generate Haptic Patterns", description="Generates haptic feedback patterns based on text or emotion.")
async def generate_haptics(request: HapticRequest):
    """
    Generates haptic patterns from text or specific emotions.
    
    - **text**: Text to analyze for haptic generation.
    - **emotion**: Direct emotion specification.
    - **intensity**: Emotion intensity (0.0-1.0).
    """
    if request.text:
        result = haptics_emulator.generate_from_text(request.text)
    elif request.emotion:
        result = haptics_emulator.generate_from_emotion(request.emotion, request.intensity)
    else:
        raise HTTPException(status_code=400, detail="Either text or emotion must be provided")
    
    return result


# New AI-powered endpoints

class TextGenerationRequest(BaseModel):
    text: str
    style: str = "immersive"
    use_google: bool = True
    max_tokens: int = 1000


@app.post("/ai/enhance_text", summary="AI Text Enhancement", description="Enhance narrative text using AI for better immersion.")
async def ai_enhance_text(request: TextGenerationRequest):
    """
    Enhance text using AI for better narrative immersion.
    
    - **text**: Original text to enhance.
    - **style**: Enhancement style (immersive, dramatic, poetic).
    - **use_google**: Use Google Gemini (true) or Ollama (false).
    - **max_tokens**: Maximum tokens to generate.
    """
    result = ai_text_generator.enhance_narrative_text(
        request.text,
        style=request.style,
        use_google=request.use_google
    )
    return result


class EmotionAnalysisRequest(BaseModel):
    text: str


@app.post("/ai/analyze_emotion", summary="AI Emotion Analysis", description="Analyze emotional content in text.")
async def ai_analyze_emotion(request: EmotionAnalysisRequest):
    """
    Analyze emotional content and intensity in text.
    
    - **text**: Text to analyze for emotional content.
    """
    result = ai_image_selector.analyze_text_emotion(request.text)
    return {
        "emotion_analysis": result,
        "timestamp": "2024-01-01T12:00:00Z"
    }


class ImageSelectionRequest(BaseModel):
    text: Optional[str] = None
    emotion: Optional[str] = None
    intensity: Optional[float] = None
    count: int = 3


@app.post("/ai/select_images", summary="AI Image Selection", description="Select appropriate images based on text or emotion.")
async def ai_select_images(request: ImageSelectionRequest):
    """
    Select images based on emotional analysis of text.
    
    - **text**: Text to analyze for image selection.
    - **emotion**: Direct emotion specification.
    - **intensity**: Emotion intensity filter.
    - **count**: Number of images to return.
    """
    if request.text:
        result = ai_image_selector.select_images_for_text(request.text, request.count)
    elif request.emotion:
        intensity_value = float(request.intensity) if request.intensity is not None else 0.5
        images = ai_image_selector.get_images_by_emotion(
            request.emotion, 
            int(request.count), 
            intensity_value
        )
        result = {
            "selected_images": images,
            "emotion_analysis": {
                "emotion": request.emotion,
                "intensity": request.intensity or 0.5
            },
            "total_available": len(ai_image_selector.images_db)
        }
    else:
        raise HTTPException(status_code=400, detail="Either text or emotion must be provided")
    
    return result


class EmotionalDescriptionRequest(BaseModel):
    emotion: str
    intensity: float = 0.5
    context: str = ""
    use_google: bool = True


@app.post("/ai/generate_emotion_description", summary="Generate Emotional Description", description="Generate vivid descriptions for specific emotions.")
async def ai_generate_emotion_description(request: EmotionalDescriptionRequest):
    """
    Generate descriptive text for specific emotions.
    
    - **emotion**: Target emotion to describe.
    - **intensity**: Emotion intensity (0.0-1.0).
    - **context**: Additional context for generation.
    - **use_google**: Use Google Gemini (true) or Ollama (false).
    """
    result = ai_text_generator.generate_emotional_description(
        request.emotion,
        request.intensity,
        request.context,
        request.use_google
    )
    return result


class ImagePromptsRequest(BaseModel):
    text: str
    count: int = 3
    style: str = "realistic"
    use_google: bool = True


@app.post("/ai/generate_image_prompts", summary="Generate Image Prompts", description="Generate prompts for AI image generation.")
async def ai_generate_image_prompts(request: ImagePromptsRequest):
    """
    Generate image prompts for AI image generation tools.
    
    - **text**: Source text for prompt generation.
    - **count**: Number of prompts to generate.
    - **style**: Image style preference.
    - **use_google**: Use Google Gemini (true) or Ollama (false).
    """
    result = ai_text_generator.generate_image_prompts(
        request.text,
        request.count,
        request.style,
        request.use_google
    )
    return result


@app.get("/ai/image_database_stats", summary="Image Database Statistics", description="Get statistics about the image database.")
async def ai_image_database_stats():
    """
    Get comprehensive statistics about the available image database.
    """
    stats = ai_image_selector.get_emotion_statistics()
    return stats


@app.get("/ai/status", summary="AI Services Status", description="Check the status of all AI services.")
async def ai_services_status():
    """
    Check the status and availability of all AI services.
    """
    # Check Ollama status
    ollama_status = ai_text_generator.check_ollama_status()
    
    # Check Google API availability
    google_available = ai_text_generator.gemini_model is not None
    
    # Check image database
    image_db_stats = ai_image_selector.get_emotion_statistics()
    available_emotions = image_db_stats.get("available_emotions", [])
    emotions_count = len(available_emotions) if isinstance(available_emotions, list) else 0
    
    return {
        "ollama": ollama_status,
        "google_gemini": {
            "available": google_available,
            "api_key_configured": ai_text_generator.google_api_key is not None
        },
        "image_database": {
            "total_images": image_db_stats.get("total_images", 0),
            "emotions_available": emotions_count
        },
        "services": {
            "text_generation": "online" if google_available or ollama_status["status"] == "online" else "limited",
            "image_selection": "online",
            "emotion_analysis": "online"
        }
    }


@app.post("/generate_haptics", summary="Generate Haptic Pattern", description="Generates haptic feedback patterns from text or emotion.")
async def generate_haptics(request: HapticRequest):
    """
    Generates haptic patterns for immersive feedback.
    
    - **text**: Text to generate haptics from (optional).
    - **emotion**: Emotion to generate haptics from (optional).
    - **intensity**: Emotion intensity (0.0-1.0).
    - **pattern_name**: Name of predefined pattern to retrieve (optional).
    """
    if request.pattern_name:
        pattern = haptics_emulator.get_pattern(request.pattern_name)
        if not pattern:
            return {"error": "Pattern not found"}
        return pattern
    elif request.text:
        return haptics_emulator.generate_from_text(request.text)
    elif request.emotion:
        return haptics_emulator.generate_from_emotion(request.emotion, request.intensity)
    else:
        return {"error": "Must provide text, emotion, or pattern_name"}


@app.get("/haptic_patterns", summary="List Haptic Patterns", description="Lists all available haptic patterns.")
async def list_haptic_patterns():
    """
    Lists all available predefined and custom haptic patterns.
    """
    patterns = haptics_emulator.get_all_patterns()
    return {
        "patterns": list(patterns.keys()),
        "total": len(patterns)
    }


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/auth/register", summary="User Registration", description="Register a new user account with subscription tier.")
async def register(registration: UserRegistration):
    """
    Register a new user account.
    
    - **email**: User's email address
    - **username**: Unique username
    - **password**: User's password
    - **subscription_tier**: free/edu/plus/pro (default: free)
    - **role**: user/student/educator/admin (default: user)
    - **school_email**: Required for EDU subscription
    """
    result = user_manager.register_user(registration)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return {
        "message": "Registration successful",
        "user": result["user"],
        "token": result["token"],
        "subscription_limits": result["subscription_limits"]
    }


@app.post("/auth/login", summary="User Login", description="Authenticate user and get access token.")
async def login(login_data: UserLogin):
    """
    Authenticate user and return access token.
    
    - **email**: User's email address
    - **password**: User's password
    """
    result = user_manager.login_user(login_data)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["error"]
        )
    
    return {
        "message": "Login successful",
        "user": result["user"],
        "token": result["token"],
        "subscription_limits": result["subscription_limits"]
    }


@app.get("/auth/me", summary="Current User Info", description="Return the authenticated user's basic info and subscription limits.")
async def auth_me(current_user: dict = Depends(get_current_user)):
    """Simple endpoint to return current authenticated user."""
    sub_limits = user_manager.subscription_limits.get(
        SubscriptionTier(current_user["subscription_tier"]) if isinstance(current_user["subscription_tier"], str) else current_user["subscription_tier"],
        {}
    )
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "username": current_user.get("username"),
            "subscription_tier": current_user.get("subscription_tier"),
            "role": current_user.get("role")
        },
        "subscription_limits": sub_limits
    }


@app.get("/auth/profile", summary="Get User Profile", description="Get current user's profile and subscription info.")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile and subscription information.
    Requires authentication.
    """
    subscription_info = user_manager.get_subscription_info(current_user['id'])
    
    return {
        "user": {
            "id": current_user['id'],
            "email": current_user['email'],
            "username": current_user['username'],
            "subscription_tier": current_user['subscription_tier'],
            "role": current_user['role'],
            "created_at": current_user['created_at'],
            "last_login": current_user['last_login']
        },
        "subscription": subscription_info
    }


@app.get("/auth/check", summary="Check Authentication Status", description="Verify if token is valid.")
async def check_auth(current_user: dict = Depends(get_current_user)):
    """
    Check if the current token is valid and return user info.
    """
    return {
        "authenticated": True,
        "user": {
            "id": current_user['id'],
            "username": current_user['username'],
            "subscription_tier": current_user['subscription_tier']
        }
    }


# ===== PROTECTED ENDPOINTS WITH USAGE TRACKING =====

@app.post("/generate_text_protected", summary="Generate Text (Protected)", description="Generate text with usage tracking and limits.")
async def generate_text_protected(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Protected text generation with subscription limits and usage tracking.
    """
    # Check usage limits
    usage_check = user_manager.check_usage_limits(current_user['id'], "api_call")
    if not usage_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Usage limit exceeded: {usage_check['error']}"
        )
    
    # Check text length limits based on subscription
    text = request.get("text", "")
    if isinstance(text, list):
        text = " ".join(text)  # Convert list to string if needed
    
    subscription_tier = SubscriptionTier(current_user['subscription_tier'])
    limits = user_manager.subscription_limits[subscription_tier]
    
    max_length_value = limits["max_text_length"]
    if isinstance(max_length_value, int):
        max_length = max_length_value
    else:
        max_length = -1  # Default to unlimited if type is unexpected
        
    text_length = len(str(text))
    if max_length != -1 and text_length > max_length:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Text too long. Maximum length for {subscription_tier.value}: {max_length}"
        )
    
    try:
        # Generate text using existing logic
        if request.get("use_ollama", False):
            result = ai_text_generator.generate_text_with_ollama(
                prompt=text,
                model=request.get("model", "phi:3-mini-128k"),
                max_tokens=request.get("max_tokens", 500)
            )
        else:
            result = ai_text_generator.generate_text_with_gemini(
                prompt=text,
                max_tokens=request.get("max_tokens", 500),
                temperature=request.get("temperature", 0.7)
            )
        
        # Increment usage counter
        user_manager.increment_usage(current_user['id'], "api_call", 1)
        
        return {
            "result": result,
            "usage": user_manager.check_usage_limits(current_user['id'], "api_call")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text generation failed: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
