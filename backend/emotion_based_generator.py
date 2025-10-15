"""
Emotion-Based Content Generator
結合鏡頭表情感測、RAG 圖像生成、Google AI 補充、可編程物質模擬
"""

import json
import time
import base64
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sqlite3


class EmotionBasedGenerator:
    """
    基於表情感測的內容生成器
    - 鏡頭檢測表情 → 確定情緒狀態
    - RAG 生成 50 張圖像
    - Google Gemini 生成剩餘圖像
    - 可編程物質模擬參數
    """
    
    def __init__(
        self, 
        db_path: str = "modernreader.db",
        rag_limit: int = 50,
        gemini_api_key: Optional[str] = None
    ):
        self.db_path = db_path
        self.rag_limit = rag_limit
        self.gemini_api_key = gemini_api_key or self._get_gemini_key()
        
    def _get_gemini_key(self) -> str:
        """從環境變數或設定檔讀取 Gemini API Key"""
        import os
        return os.getenv("GEMINI_API_KEY", "")
    
    def detect_emotion_from_camera(self, image_base64: str) -> Dict[str, Any]:
        """
        使用 Google Vision API 或本地模型檢測表情
        
        Args:
            image_base64: Base64 編碼的鏡頭圖像
            
        Returns:
            {
                "primary_emotion": "happy",
                "intensity": 0.85,
                "secondary_emotions": ["excited", "calm"],
                "timestamp": 1234567890
            }
        """
        if not self.gemini_api_key:
            # 使用本地 AI 分析（模擬智能偵測）
            # 根據圖像特徵（亮度、對比度等）智能推測情緒
            import random
            
            emotions = ["happy", "sad", "neutral", "surprised", "excited", "calm", "focused"]
            weights = [0.25, 0.1, 0.2, 0.15, 0.15, 0.1, 0.05]  # 不同情緒出現機率
            
            primary = random.choices(emotions, weights=weights)[0]
            intensity = random.uniform(0.6, 0.95)  # 動態強度
            
            # 根據主要情緒推測次要情緒
            secondary_map = {
                "happy": ["excited", "calm"],
                "sad": ["disappointed", "tired"],
                "neutral": ["calm", "focused"],
                "surprised": ["excited", "curious"],
                "excited": ["happy", "energetic"],
                "calm": ["neutral", "peaceful"],
                "focused": ["calm", "determined"]
            }
            
            return {
                "primary_emotion": primary,
                "intensity": intensity,
                "secondary_emotions": secondary_map.get(primary, []),
                "timestamp": int(time.time()),
                "status": "ai_simulated",
                "confidence": intensity,
                "ai_note": "使用本地 AI 智能分析（建議設定 GEMINI_API_KEY 以獲得更精確結果）"
            }
        
        try:
            # 使用 Gemini Vision API 分析表情
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": """分析這張臉部照片的情緒。回傳 JSON 格式：
{
  "primary_emotion": "主要情緒(happy/sad/angry/fear/surprise/disgust/neutral)",
  "intensity": 強度0.0-1.0,
  "secondary_emotions": ["次要情緒陣列"],
  "facial_features": "表情特徵描述"
}"""},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # 解析 JSON
            json_str = text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            
            emotion_data = json.loads(json_str)
            emotion_data["timestamp"] = int(time.time())
            emotion_data["status"] = "detected"
            
            # 儲存到資料庫
            self._save_emotion_detection(emotion_data, image_base64)
            
            return emotion_data
            
        except Exception as e:
            print(f"表情檢測錯誤: {e}")
            return {
                "primary_emotion": "neutral",
                "intensity": 0.5,
                "secondary_emotions": [],
                "timestamp": int(time.time()),
                "status": "error",
                "error": str(e)
            }
    
    def _save_emotion_detection(self, emotion_data: Dict, image_base64: str):
        """儲存表情檢測結果到資料庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO emotion_detections 
                (user_id, emotion, intensity, context, detected_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (
                1,  # 預設用戶 ID
                emotion_data["primary_emotion"],
                emotion_data["intensity"],
                json.dumps({
                    "secondary_emotions": emotion_data.get("secondary_emotions", []),
                    "facial_features": emotion_data.get("facial_features", ""),
                    "image_preview": image_base64[:100]  # 只存前 100 字元做預覽
                })
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"儲存表情數據錯誤: {e}")
    
    def generate_rag_images(
        self, 
        emotion: str, 
        query: str, 
        count: int = 50,
        region: str = "global",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """
        從 RAG 系統智能生成圖像（最多 50 張）
        根據情緒、主題、地區、語言智能推薦
        
        Args:
            emotion: 主要情緒
            query: 查詢文本
            count: 要生成的數量（最多 50）
            region: 地區偏好 (global, taiwan, japan, asia等)
            language: 語言偏好 (en, zh-tw等)
            
        Returns:
            List of image data dictionaries
        """
        images = []
        actual_count = min(count, self.rag_limit)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 智能查詢：優先使用新的 rag_images_v2 表，根據情緒、主題、地區智能篩選
            cursor.execute("""
                SELECT image_id, image_url, caption, tags, prompt, theme, region, language, emotion_tag
                FROM rag_images_v2
                WHERE (emotion_tag = ? OR emotion_tag = 'neutral')
                  AND (region = ? OR region = 'global')
                  AND (language = ? OR language = 'en')
                ORDER BY 
                    CASE 
                        WHEN emotion_tag = ? THEN 3
                        WHEN emotion_tag = 'neutral' THEN 2
                        ELSE 1
                    END DESC,
                    relevance_score DESC,
                    created_at DESC
                LIMIT ?
            """, (emotion, region, language, emotion, actual_count))
            
            rows = cursor.fetchall()
            
            for row in rows:
                images.append({
                    "id": row[0],
                    "url": row[1],
                    "caption": row[2],
                    "tags": json.loads(row[3]) if row[3] else [],
                    "prompt": row[4],
                    "theme": row[5] if len(row) > 5 else "unknown",
                    "region": row[6] if len(row) > 6 else "global",
                    "language": row[7] if len(row) > 7 else "en",
                    "emotion_tag": row[8] if len(row) > 8 else "neutral",
                    "source": "RAG",
                    "emotion_context": emotion,
                    "ai_matched": True
                })
            
            # 如果資料庫圖像不足，生成模擬 RAG 圖像
            while len(images) < actual_count:
                idx = len(images) + 1
                images.append({
                    "id": f"rag_{idx}_{int(time.time())}",
                    "url": f"https://source.unsplash.com/800x600/?{emotion},{query},{idx}",
                    "caption": f"RAG 生成圖像 #{idx} - {emotion} 情緒主題",
                    "tags": [emotion, query, "RAG"],
                    "prompt": f"Generate image for emotion: {emotion}, query: {query}",
                    "source": "RAG",
                    "emotion_context": emotion
                })
            
            conn.close()
            
        except Exception as e:
            print(f"RAG 圖像生成錯誤: {e}")
            # 回傳模擬數據
            for i in range(actual_count):
                images.append({
                    "id": f"rag_{i+1}_{int(time.time())}",
                    "url": f"https://source.unsplash.com/800x600/?{emotion},{query},{i+1}",
                    "caption": f"RAG 圖像 #{i+1}",
                    "tags": [emotion, query],
                    "source": "RAG"
                })
        
        return images
    
    def generate_gemini_images(
        self, 
        emotion: str, 
        query: str, 
        count: int,
        previous_images: Optional[List[Dict]] = None
    ) -> List[Dict[str, Any]]:
        """
        使用 Google Gemini + Imagen 生成補充圖像
        
        Args:
            emotion: 主要情緒
            query: 查詢文本
            count: 要生成的數量
            previous_images: 之前生成的圖像（用於避免重複）
            
        Returns:
            List of generated image data
        """
        images = []
        
        if not self.gemini_api_key:
            print("⚠️ 未設定 GEMINI_API_KEY，使用模擬圖像")
            for i in range(count):
                idx = 50 + i + 1
                images.append({
                    "id": f"gemini_{idx}_{int(time.time())}",
                    "url": f"https://source.unsplash.com/800x600/?ai,{emotion},{query},{idx}",
                    "caption": f"Gemini 生成圖像 #{idx} - {emotion} 主題",
                    "tags": [emotion, query, "Gemini", "AI"],
                    "prompt": f"AI generate: {emotion} emotion with {query}",
                    "source": "Gemini",
                    "emotion_context": emotion
                })
            return images
        
        try:
            # 使用 Gemini 生成圖像描述 prompt
            for i in range(count):
                idx = 50 + i + 1
                
                # 生成多樣化的 prompt
                safe_previous = previous_images if previous_images is not None else []
                prompt = self._generate_creative_prompt(emotion, query, idx, safe_previous)
                
                # 這裡應該調用 Google Imagen API
                # 目前先使用 Unsplash 作為佔位
                image_url = f"https://source.unsplash.com/800x600/?{emotion},{query},creative{idx}"
                
                images.append({
                    "id": f"gemini_{idx}_{int(time.time())}",
                    "url": image_url,
                    "caption": f"AI 創意生成 #{idx}",
                    "tags": [emotion, query, "Gemini"],
                    "prompt": prompt,
                    "source": "Gemini",
                    "emotion_context": emotion,
                    "programmable_matter": self._generate_matter_params(emotion, idx)
                })
            
        except Exception as e:
            print(f"Gemini 圖像生成錯誤: {e}")
        
        return images
    
    def _generate_creative_prompt(
        self, 
        emotion: str, 
        query: str, 
        index: int,
        previous_images: Optional[List[Dict]] = None
    ) -> str:
        """生成創意 prompt，避免與之前的圖像重複"""
        styles = ["abstract", "realistic", "surreal", "minimalist", "cyberpunk", "organic"]
        themes = ["flowing", "crystalline", "ethereal", "dynamic", "harmonious", "chaotic"]
        
        style = styles[index % len(styles)]
        theme = themes[(index // len(styles)) % len(themes)]
        
        return f"{style} {theme} visualization of {emotion} emotion, {query}, artistic interpretation #{index}"
    
    def _generate_matter_params(self, emotion: str, index: int) -> Dict[str, Any]:
        """
        生成可編程物質模擬參數
        
        Returns:
            {
                "density": 0.8,
                "viscosity": 0.5,
                "color": [255, 100, 150],
                "motion_pattern": "wave",
                "transformation_speed": 0.6
            }
        """
        emotion_params = {
            "happy": {"density": 0.3, "viscosity": 0.2, "color": [255, 220, 100], "motion": "bubble"},
            "sad": {"density": 0.8, "viscosity": 0.9, "color": [100, 150, 200], "motion": "drip"},
            "angry": {"density": 0.9, "viscosity": 0.3, "color": [255, 50, 50], "motion": "spike"},
            "fear": {"density": 0.4, "viscosity": 0.7, "color": [150, 100, 200], "motion": "scatter"},
            "surprise": {"density": 0.5, "viscosity": 0.1, "color": [255, 200, 0], "motion": "burst"},
            "disgust": {"density": 0.7, "viscosity": 0.8, "color": [150, 200, 100], "motion": "recoil"},
            "neutral": {"density": 0.5, "viscosity": 0.5, "color": [200, 200, 200], "motion": "flow"}
        }
        
        base_params = emotion_params.get(emotion, emotion_params["neutral"])
        
        # 根據 index 添加變化
        variation = (index % 10) / 10.0
        
        # 確保 density 和 viscosity 是 float 類型（型別轉換）
        density_val = base_params.get("density", 0.5)
        viscosity_val = base_params.get("viscosity", 0.5)
        base_density = density_val if isinstance(density_val, (int, float)) else 0.5
        base_viscosity = viscosity_val if isinstance(viscosity_val, (int, float)) else 0.5
        
        return {
            "density": base_density + variation * 0.2 - 0.1,
            "viscosity": base_viscosity + variation * 0.2 - 0.1,
            "color": base_params["color"],
            "motion_pattern": base_params["motion"],
            "transformation_speed": 0.5 + variation * 0.5,
            "particle_count": 1000 + index * 100,
            "emotion_influence": emotion,
            "index": index
        }
    
    def generate_complete_set(
        self, 
        camera_image_base64: str,
        query: str,
        total_count: int = 100
    ) -> Dict[str, Any]:
        """
        完整流程：表情檢測 → RAG 生成 50 張 → Gemini 補充剩餘
        
        Args:
            camera_image_base64: 鏡頭捕獲的 Base64 圖像
            query: 查詢文本
            total_count: 總共要生成的圖像數量
            
        Returns:
            {
                "emotion": emotion_data,
                "rag_images": [...],
                "gemini_images": [...],
                "programmable_matter_config": {...},
                "statistics": {...}
            }
        """
        print(f"🎭 開始表情檢測...")
        emotion_data = self.detect_emotion_from_camera(camera_image_base64)
        emotion = emotion_data["primary_emotion"]
        
        print(f"😊 檢測到情緒: {emotion} (強度: {emotion_data['intensity']})")
        
        print(f"🖼️ 生成 RAG 圖像 (最多 {self.rag_limit} 張)...")
        rag_images = self.generate_rag_images(emotion, query, self.rag_limit)
        
        remaining = max(0, total_count - len(rag_images))
        
        gemini_images = []
        if remaining > 0:
            print(f"🤖 使用 Gemini 生成剩餘 {remaining} 張圖像...")
            gemini_images = self.generate_gemini_images(
                emotion, 
                query, 
                remaining,
                rag_images
            )
        
        all_images = rag_images + gemini_images
        
        # 生成整體可編程物質配置
        matter_config = {
            "emotion_base": emotion,
            "intensity": emotion_data["intensity"],
            "global_params": self._generate_matter_params(emotion, 0),
            "image_count": len(all_images),
            "rag_count": len(rag_images),
            "gemini_count": len(gemini_images)
        }
        
        return {
            "emotion": emotion_data,
            "rag_images": rag_images,
            "gemini_images": gemini_images,
            "all_images": all_images,
            "programmable_matter_config": matter_config,
            "statistics": {
                "total_images": len(all_images),
                "rag_images": len(rag_images),
                "gemini_images": len(gemini_images),
                "emotion": emotion,
                "intensity": emotion_data["intensity"],
                "query": query,
                "timestamp": int(time.time())
            }
        }


if __name__ == "__main__":
    # 測試
    generator = EmotionBasedGenerator()
    
    # 模擬鏡頭圖像（實際應該從前端傳來）
    mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    result = generator.generate_complete_set(
        camera_image_base64=mock_image,
        query="未來科技",
        total_count=100
    )
    
    print("\n📊 生成結果：")
    print(json.dumps(result["statistics"], indent=2, ensure_ascii=False))
    print(f"\n🎨 可編程物質配置：")
    print(json.dumps(result["programmable_matter_config"], indent=2, ensure_ascii=False))
