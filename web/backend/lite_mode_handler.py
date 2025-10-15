"""
Lite Mode Handler - 條件裁剪處理器
為手機/手錶版本提供輕量級功能
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException

class LiteModeHandler:
    """處理Lite Mode的功能裁剪"""
    
    def __init__(self, lite_mode: bool = False):
        self.lite_mode = lite_mode
    
    def check_feature_available(self, feature_name: str) -> bool:
        """檢查功能是否在Lite Mode中可用"""
        if not self.lite_mode:
            return True
            
        # Lite Mode允許的功能
        lite_features = {
            "text_generation",  # AI文本生成
            "auth",            # 身份驗證
            "health",          # 健康檢查
            "basic_nlp"        # 基礎NLP
        }
        
        return feature_name in lite_features
    
    def lite_response(self, message: str = "功能在Lite模式中不可用") -> Dict[str, Any]:
        """返回Lite Mode標準響應"""
        return {
            "error": "lite_mode_restriction",
            "message": message,
            "lite_mode": True,
            "suggestion": "請在桌面版本中使用完整功能"
        }
    
    def require_full_mode(self, feature_name: str):
        """裝飾器：要求完整模式"""
        if self.lite_mode:
            raise HTTPException(
                status_code=423,  # Locked
                detail=self.lite_response(f"{feature_name}功能需要完整版本")
            )

# Mock classes for Lite Mode
class MockTextSegmenter:
    def get_segments_with_metadata(self, text: str, strategy: str = "basic"):
        return {
            "segments": [text],
            "metadata": {"mode": "lite", "strategy": "simple"},
            "warning": "Lite模式：簡化文本分割"
        }

class MockTTSEngine:
    def text_to_speech(self, text: str, **kwargs):
        # 返回模擬的文件對象結構
        class MockFile:
            def read(self):
                return b"Mock audio data - TTS not available in lite mode"
        
        return MockFile()
    
    def get_available_voices(self):
        return ["lite_voice_only"]

class MockHapticsEmulator:
    def generate_from_text(self, text: str):
        return {
            "pattern": "simple_buzz",
            "duration": 100,
            "events": [{"type": "buzz", "duration": 100}],  # 添加events字段
            "message": "Lite模式：簡化觸覺反饋"
        }
    
    def generate_from_emotion(self, emotion: str, intensity: float):
        return {
            "pattern": "emotion_lite",
            "intensity": min(intensity, 0.5),
            "events": [{"type": emotion, "intensity": min(intensity, 0.5)}],
            "message": "Lite模式：限制強度"
        }
    
    def get_pattern(self, pattern_name: str):
        return {
            "name": pattern_name,
            "pattern": "lite_pattern",
            "message": "Lite模式：基礎觸覺模式"
        }

class MockImageSelector:
    def __init__(self):
        self.images_db = []  # 空數據庫用於兼容性
    
    def select_images_for_text(self, text: str, count: int = 3):
        return {
            "images": [],
            "emotion_analysis": {
                "emotion": "neutral",
                "intensity": 0.5,
                "keywords": ["lite", "mode"]
            },
            "message": "圖像選擇在Lite模式中不可用",
            "suggestion": "請使用桌面版本"
        }
    
    def analyze_text_emotion(self, text: str):
        return {
            "emotion": "neutral",
            "confidence": 0.5,
            "message": "Lite模式：基礎情感分析"
        }
    
    def get_images_by_emotion(self, emotion: str, count: int = 3, intensity: float = 0.5):
        return []
    
    def get_emotion_statistics(self):
        return {
            "total_images": 0,
            "emotions": {},
            "message": "統計數據在Lite模式中不可用"
        }

class MockImageCaptioner:
    def generate_caption(self, image_path: str):
        return {
            "caption": "圖像描述在Lite模式中不可用",
            "confidence": 0.0,
            "message": "請使用完整版本"
        }