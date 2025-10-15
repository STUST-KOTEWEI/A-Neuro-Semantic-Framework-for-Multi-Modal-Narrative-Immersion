"""
Voice Engine - TTS (Text-to-Speech) & STT (Speech-to-Text)
支援多種語音引擎：OpenAI, ElevenLabs, Google, Azure
"""

import os
import json
import time
import base64
from typing import Optional, Dict, Any, List
import requests
from pathlib import Path


class TTSEngine:
    """文字轉語音引擎"""
    
    def __init__(
        self, 
        provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        初始化 TTS 引擎
        
        Args:
            provider: 語音提供商 (openai, elevenlabs, google, azure)
            api_key: API 金鑰
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key(provider)
        
    def _get_api_key(self, provider: str) -> str:
        """從環境變數獲取 API Key"""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "elevenlabs": "ELEVENLABS_API_KEY",
            "google": "GOOGLE_CLOUD_API_KEY",
            "azure": "AZURE_SPEECH_KEY"
        }
        return os.getenv(key_map.get(provider, ""), "")
    
    def text_to_speech(
        self, 
        text: str,
        voice: str = "alloy",
        emotion: Optional[str] = None,
        speed: float = 1.0,
        output_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        將文字轉換為語音
        
        Args:
            text: 要轉換的文字
            voice: 語音名稱
            emotion: 情緒（如果支援）
            speed: 語速 (0.5-2.0)
            output_format: 輸出格式 (mp3, wav, opus)
            
        Returns:
            {
                "audio_url": "https://...",
                "audio_base64": "...",
                "duration": 5.2,
                "format": "mp3"
            }
        """
        if self.provider == "openai":
            return self._openai_tts(text, voice, speed, output_format)
        elif self.provider == "elevenlabs":
            return self._elevenlabs_tts(text, voice, emotion, output_format)
        elif self.provider == "google":
            return self._google_tts(text, voice, speed, output_format)
        else:
            # 回傳模擬數據
            return self._mock_tts(text, voice, speed, output_format)
    
    def _openai_tts(self, text: str, voice: str, speed: float, output_format: str) -> Dict:
        """使用 OpenAI TTS API"""
        if not self.api_key:
            return self._mock_tts(text, voice, speed, output_format)
        
        try:
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": voice,  # alloy, echo, fable, onyx, nova, shimmer
                "speed": speed,
                "response_format": output_format
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 儲存音檔
            audio_data = response.content
            filename = f"tts_{int(time.time())}.{output_format}"
            output_path = Path("static/audio") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            return {
                "audio_url": f"/static/audio/{filename}",
                "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
                "duration": len(text) / 15.0,  # 估算
                "format": output_format,
                "provider": "openai",
                "voice": voice,
                "text": text
            }
            
        except Exception as e:
            print(f"OpenAI TTS 錯誤: {e}")
            return self._mock_tts(text, voice, speed, output_format)
    
    def _elevenlabs_tts(self, text: str, voice: str, emotion: Optional[str], output_format: str) -> Dict:
        """使用 ElevenLabs TTS API（支援情緒）"""
        if not self.api_key:
            return self._mock_tts(text, voice, 1.0, output_format)
        
        try:
            # ElevenLabs 支援情緒驅動的語音
            voice_id = voice or "21m00Tcm4TlvDq8ikWAM"  # Rachel 預設
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            # 根據情緒調整語音參數
            emotion_settings = self._get_emotion_voice_settings(emotion)
            
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": emotion_settings
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            audio_data = response.content
            filename = f"tts_elevenlabs_{int(time.time())}.{output_format}"
            output_path = Path("static/audio") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            return {
                "audio_url": f"/static/audio/{filename}",
                "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
                "duration": len(text) / 15.0,
                "format": output_format,
                "provider": "elevenlabs",
                "voice": voice_id,
                "emotion": emotion,
                "text": text
            }
            
        except Exception as e:
            print(f"ElevenLabs TTS 錯誤: {e}")
            return self._mock_tts(text, voice, 1.0, output_format)
    
    def _get_emotion_voice_settings(self, emotion: Optional[str]) -> Dict:
        """根據情緒返回語音設定"""
        emotion_map = {
            "happy": {"stability": 0.3, "similarity_boost": 0.8, "style": 0.7},
            "sad": {"stability": 0.7, "similarity_boost": 0.6, "style": 0.3},
            "angry": {"stability": 0.4, "similarity_boost": 0.9, "style": 0.8},
            "fear": {"stability": 0.6, "similarity_boost": 0.7, "style": 0.4},
            "surprise": {"stability": 0.2, "similarity_boost": 0.8, "style": 0.9},
            "neutral": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.5}
        }
        if not emotion or emotion not in emotion_map:
            return emotion_map["neutral"]
        return emotion_map[emotion]
    
    def _google_tts(self, text: str, voice: str, speed: float, output_format: str) -> Dict:
        """使用 Google Cloud TTS API"""
        # 實作類似 OpenAI，這裡簡化
        return self._mock_tts(text, voice, speed, output_format)
    
    def _mock_tts(self, text: str, voice: str, speed: float, output_format: str) -> Dict:
        """模擬 TTS 輸出"""
        return {
            "audio_url": f"/static/audio/mock_tts_{int(time.time())}.{output_format}",
            "audio_base64": "",
            "duration": len(text) / (15.0 * speed),
            "format": output_format,
            "provider": "mock",
            "voice": voice,
            "text": text,
            "note": "模擬數據 - 請設定 API Key 以使用真實 TTS"
        }


class STTEngine:
    """語音轉文字引擎"""
    
    def __init__(
        self, 
        provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """
        初始化 STT 引擎
        
        Args:
            provider: 語音提供商 (openai, google, azure)
            api_key: API 金鑰
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key(provider)
    
    def _get_api_key(self, provider: str) -> str:
        """從環境變數獲取 API Key"""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_CLOUD_API_KEY",
            "azure": "AZURE_SPEECH_KEY"
        }
        return os.getenv(key_map.get(provider, ""), "")
    
    def speech_to_text(
        self, 
        audio_data: bytes,
        language: str = "zh-TW",
        audio_format: str = "webm"
    ) -> Dict[str, Any]:
        """
        將語音轉換為文字
        
        Args:
            audio_data: 音訊數據（bytes）
            language: 語言代碼
            audio_format: 音訊格式
            
        Returns:
            {
                "text": "轉換後的文字",
                "confidence": 0.95,
                "language": "zh-TW",
                "duration": 3.2
            }
        """
        if self.provider == "openai":
            return self._openai_stt(audio_data, language)
        elif self.provider == "google":
            return self._google_stt(audio_data, language)
        else:
            return self._mock_stt(audio_data, language)
    
    def _openai_stt(self, audio_data: bytes, language: str) -> Dict:
        """使用 OpenAI Whisper API"""
        if not self.api_key:
            return self._mock_stt(audio_data, language)
        
        try:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            files = {
                "file": ("audio.webm", audio_data, "audio/webm")
            }
            data = {
                "model": "whisper-1",
                "language": language.split("-")[0]  # zh-TW -> zh
            }
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "text": result.get("text", ""),
                "confidence": 0.95,  # Whisper 不返回置信度
                "language": language,
                "duration": len(audio_data) / 16000,  # 估算
                "provider": "openai"
            }
            
        except Exception as e:
            print(f"OpenAI STT 錯誤: {e}")
            return self._mock_stt(audio_data, language)
    
    def _google_stt(self, audio_data: bytes, language: str) -> Dict:
        """使用 Google Cloud Speech-to-Text API"""
        # 實作類似 OpenAI
        return self._mock_stt(audio_data, language)
    
    def _mock_stt(self, audio_data: bytes, language: str) -> Dict:
        """模擬 STT 輸出"""
        return {
            "text": "這是模擬的語音轉文字結果",
            "confidence": 0.85,
            "language": language,
            "duration": len(audio_data) / 16000,
            "provider": "mock",
            "note": "模擬數據 - 請設定 API Key 以使用真實 STT"
        }


class VoiceController:
    """語音控制器 - 整合 TTS 和 STT"""
    
    def __init__(self):
        self.tts_engine = TTSEngine()
        self.stt_engine = STTEngine()
    
    def speak(
        self, 
        text: str, 
        emotion: Optional[str] = None,
        voice: str = "alloy"
    ) -> Dict[str, Any]:
        """
        將文字轉為語音並播放
        
        Args:
            text: 要說的文字
            emotion: 情緒（影響語調）
            voice: 語音名稱
        """
        return self.tts_engine.text_to_speech(
            text=text,
            voice=voice,
            emotion=emotion
        )
    
    def listen(self, audio_data: bytes) -> Dict[str, Any]:
        """
        聽取語音並轉為文字
        
        Args:
            audio_data: 錄音數據
        """
        return self.stt_engine.speech_to_text(audio_data)
    
    def conversation_loop(
        self,
        user_audio: bytes,
        system_response_text: str,
        emotion: str = "neutral"
    ) -> Dict[str, Any]:
        """
        完整對話循環：聽 → 處理 → 說
        
        Args:
            user_audio: 用戶語音
            system_response_text: 系統回應文字
            emotion: 回應情緒
            
        Returns:
            {
                "user_text": "用戶說的話",
                "system_audio": "系統語音",
                "emotion": "neutral"
            }
        """
        # 1. STT: 聽取用戶語音
        stt_result = self.listen(user_audio)
        
        # 2. TTS: 生成系統回應語音
        tts_result = self.speak(system_response_text, emotion)
        
        return {
            "user_text": stt_result["text"],
            "user_confidence": stt_result["confidence"],
            "system_text": system_response_text,
            "system_audio_url": tts_result["audio_url"],
            "system_audio_base64": tts_result["audio_base64"],
            "emotion": emotion,
            "timestamp": int(time.time())
        }


# 全局實例
voice_controller = VoiceController()


if __name__ == "__main__":
    # 測試 TTS
    controller = VoiceController()
    
    print("🎤 測試 TTS (文字轉語音)")
    result = controller.speak(
        text="你好！這是一個測試訊息。今天天氣真好！",
        emotion="happy",
        voice="alloy"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n🔊 測試 STT (語音轉文字)")
    # 模擬音訊數據
    mock_audio = b"mock_audio_data"
    result = controller.listen(mock_audio)
    print(json.dumps(result, indent=2, ensure_ascii=False))
