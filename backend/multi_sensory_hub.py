"""
Multi-Sensory Hub - 多感官整合中樞
整合所有感官輸出設備的控制中心
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
import requests


class DeviceType(Enum):
    """設備類型枚舉"""
    APPLE_WATCH = "apple_watch"
    RAYBAN_META = "rayban_meta"
    TESLA_SUIT = "tesla_suit"
    BHAPTICS = "bhaptics"
    AROMAJOIN = "aromajoin"
    FOODINI = "foodini"


class EmotionMapping:
    """情緒到感官輸出的映射"""
    
    @staticmethod
    def get_haptic_pattern(emotion: str, intensity: float) -> Dict[str, Any]:
        """
        根據情緒生成觸覺反饋模式
        
        Returns:
            {
                "pattern": "heartbeat",
                "intensity": 0.8,
                "duration": 2000,
                "frequency": 120
            }
        """
        patterns = {
            "happy": {
                "pattern": "bounce",
                "intensity": intensity * 0.7,
                "duration": 1500,
                "frequency": 180,
                "zones": ["chest", "shoulders"]
            },
            "sad": {
                "pattern": "slow_pulse",
                "intensity": intensity * 0.5,
                "duration": 3000,
                "frequency": 60,
                "zones": ["chest", "back"]
            },
            "angry": {
                "pattern": "sharp_burst",
                "intensity": intensity * 0.9,
                "duration": 500,
                "frequency": 200,
                "zones": ["arms", "chest", "back"]
            },
            "fear": {
                "pattern": "tremor",
                "intensity": intensity * 0.8,
                "duration": 2000,
                "frequency": 150,
                "zones": ["spine", "shoulders"]
            },
            "surprise": {
                "pattern": "sudden_spike",
                "intensity": intensity,
                "duration": 800,
                "frequency": 220,
                "zones": ["chest", "arms"]
            },
            "disgust": {
                "pattern": "recoil_wave",
                "intensity": intensity * 0.6,
                "duration": 1200,
                "frequency": 90,
                "zones": ["stomach", "chest"]
            },
            "neutral": {
                "pattern": "gentle_wave",
                "intensity": intensity * 0.3,
                "duration": 2000,
                "frequency": 80,
                "zones": ["chest"]
            }
        }
        return patterns.get(emotion, patterns["neutral"])
    
    @staticmethod
    def get_aroma_profile(emotion: str, intensity: float) -> Dict[str, Any]:
        """
        根據情緒生成氣味配方
        
        Returns:
            {
                "scent": "lavender",
                "intensity": 0.6,
                "duration": 300,
                "notes": ["floral", "calming"]
            }
        """
        aromas = {
            "happy": {
                "scent": "citrus_blend",
                "notes": ["orange", "lemon", "bergamot"],
                "intensity": intensity * 0.8,
                "duration": 180
            },
            "sad": {
                "scent": "chamomile_vanilla",
                "notes": ["chamomile", "vanilla", "warm"],
                "intensity": intensity * 0.6,
                "duration": 300
            },
            "angry": {
                "scent": "peppermint_eucalyptus",
                "notes": ["peppermint", "eucalyptus", "cooling"],
                "intensity": intensity * 0.5,
                "duration": 120
            },
            "fear": {
                "scent": "lavender_sandalwood",
                "notes": ["lavender", "sandalwood", "grounding"],
                "intensity": intensity * 0.7,
                "duration": 240
            },
            "surprise": {
                "scent": "jasmine_ginger",
                "notes": ["jasmine", "ginger", "energizing"],
                "intensity": intensity * 0.9,
                "duration": 90
            },
            "disgust": {
                "scent": "mint_pine",
                "notes": ["mint", "pine", "fresh"],
                "intensity": intensity * 0.4,
                "duration": 150
            },
            "neutral": {
                "scent": "subtle_woody",
                "notes": ["cedar", "light"],
                "intensity": intensity * 0.3,
                "duration": 200
            }
        }
        return aromas.get(emotion, aromas["neutral"])
    
    @staticmethod
    def get_taste_profile(emotion: str, intensity: float) -> Dict[str, Any]:
        """
        根據情緒生成味覺配方（Foodini）
        
        Returns:
            {
                "flavor": "sweet_umami",
                "ingredients": ["honey", "miso"],
                "intensity": 0.7,
                "temperature": 37
            }
        """
        tastes = {
            "happy": {
                "flavor": "sweet_fruity",
                "ingredients": ["strawberry", "honey", "vanilla"],
                "intensity": intensity * 0.8,
                "temperature": 25,
                "texture": "smooth"
            },
            "sad": {
                "flavor": "comfort_sweet",
                "ingredients": ["chocolate", "caramel", "salt"],
                "intensity": intensity * 0.7,
                "temperature": 40,
                "texture": "creamy"
            },
            "angry": {
                "flavor": "spicy_bitter",
                "ingredients": ["chili", "dark_chocolate", "coffee"],
                "intensity": intensity * 0.9,
                "temperature": 50,
                "texture": "sharp"
            },
            "fear": {
                "flavor": "mild_earthy",
                "ingredients": ["chamomile", "honey", "oat"],
                "intensity": intensity * 0.5,
                "temperature": 37,
                "texture": "gentle"
            },
            "surprise": {
                "flavor": "tangy_pop",
                "ingredients": ["lemon", "ginger", "mint"],
                "intensity": intensity,
                "temperature": 15,
                "texture": "fizzy"
            },
            "disgust": {
                "flavor": "cleansing_fresh",
                "ingredients": ["cucumber", "mint", "lime"],
                "intensity": intensity * 0.4,
                "temperature": 10,
                "texture": "crisp"
            },
            "neutral": {
                "flavor": "subtle_umami",
                "ingredients": ["vegetable_broth", "herbs"],
                "intensity": intensity * 0.3,
                "temperature": 37,
                "texture": "light"
            }
        }
        return tastes.get(emotion, tastes["neutral"])
    
    @staticmethod
    def get_ar_overlay(emotion: str, intensity: float) -> Dict[str, Any]:
        """
        根據情緒生成 AR 覆蓋層（Ray-Ban Meta）
        
        Returns:
            {
                "overlay_type": "particle_effect",
                "color": [255, 220, 100],
                "opacity": 0.6,
                "animation": "float"
            }
        """
        overlays = {
            "happy": {
                "overlay_type": "sparkles",
                "color": [255, 220, 100],
                "opacity": intensity * 0.7,
                "animation": "float_up",
                "particle_count": 50
            },
            "sad": {
                "overlay_type": "rain",
                "color": [100, 150, 200],
                "opacity": intensity * 0.5,
                "animation": "fall_down",
                "particle_count": 30
            },
            "angry": {
                "overlay_type": "flames",
                "color": [255, 50, 50],
                "opacity": intensity * 0.8,
                "animation": "flicker",
                "particle_count": 60
            },
            "fear": {
                "overlay_type": "fog",
                "color": [150, 100, 200],
                "opacity": intensity * 0.6,
                "animation": "swirl",
                "particle_count": 40
            },
            "surprise": {
                "overlay_type": "burst",
                "color": [255, 200, 0],
                "opacity": intensity * 0.9,
                "animation": "explode",
                "particle_count": 80
            },
            "disgust": {
                "overlay_type": "ripple",
                "color": [150, 200, 100],
                "opacity": intensity * 0.4,
                "animation": "wave_out",
                "particle_count": 25
            },
            "neutral": {
                "overlay_type": "ambient",
                "color": [200, 200, 200],
                "opacity": intensity * 0.3,
                "animation": "subtle_glow",
                "particle_count": 20
            }
        }
        return overlays.get(emotion, overlays["neutral"])


class MultiSensoryHub:
    """多感官整合中樞"""
    
    def __init__(self):
        self.active_devices = set()
        self.current_emotion = None
        self.emotion_intensity = 0.5
        
    async def broadcast_to_all_devices(
        self, 
        emotion: str, 
        intensity: float,
        content: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        向所有已連接的設備廣播感官輸出
        
        Args:
            emotion: 當前情緒
            intensity: 情緒強度
            content: 額外的內容數據（文字、圖像等）
            
        Returns:
            各設備的執行狀態
        """
        self.current_emotion = emotion
        self.emotion_intensity = intensity
        
        results = {}
        
        # 並行發送到所有設備
        tasks = []
        
        if DeviceType.APPLE_WATCH.value in self.active_devices:
            tasks.append(self._send_to_apple_watch(emotion, intensity))
            
        if DeviceType.RAYBAN_META.value in self.active_devices:
            safe_content = content if content is not None else {}
            tasks.append(self._send_to_rayban_meta(emotion, intensity, safe_content))
            
        if DeviceType.TESLA_SUIT.value in self.active_devices:
            tasks.append(self._send_to_tesla_suit(emotion, intensity))
            
        if DeviceType.BHAPTICS.value in self.active_devices:
            tasks.append(self._send_to_bhaptics(emotion, intensity))
            
        if DeviceType.AROMAJOIN.value in self.active_devices:
            tasks.append(self._send_to_aromajoin(emotion, intensity))
            
        if DeviceType.FOODINI.value in self.active_devices:
            tasks.append(self._send_to_foodini(emotion, intensity))
        
        if tasks:
            device_results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, device_type in enumerate(self.active_devices):
                results[device_type] = device_results[i] if i < len(device_results) else None
        
        return {
            "emotion": emotion,
            "intensity": intensity,
            "devices": results,
            "timestamp": int(time.time())
        }
    
    async def _send_to_apple_watch(self, emotion: str, intensity: float) -> Dict:
        """發送觸覺反饋到 Apple Watch"""
        haptic = EmotionMapping.get_haptic_pattern(emotion, intensity)
        
        # 模擬 Apple Watch API 調用
        payload = {
            "type": "haptic",
            "pattern": haptic["pattern"],
            "intensity": haptic["intensity"],
            "duration": haptic["duration"]
        }
        
        print(f"📱 Apple Watch: {haptic['pattern']} (強度 {haptic['intensity']:.2f})")
        
        return {
            "device": "Apple Watch",
            "status": "success",
            "payload": payload
        }
    
    async def _send_to_rayban_meta(self, emotion: str, intensity: float, content: Dict) -> Dict:
        """發送 AR 覆蓋到 Ray-Ban Meta 眼鏡"""
        overlay = EmotionMapping.get_ar_overlay(emotion, intensity)
        
        payload = {
            "type": "ar_overlay",
            "overlay": overlay,
            "content": content.get("text") if content else "",
            "images": content.get("images", [])[:3] if content else []  # 最多 3 張
        }
        
        print(f"🕶️ Ray-Ban Meta: {overlay['overlay_type']} AR 效果")
        
        return {
            "device": "Ray-Ban Meta",
            "status": "success",
            "payload": payload
        }
    
    async def _send_to_tesla_suit(self, emotion: str, intensity: float) -> Dict:
        """發送全身觸覺到 Tesla Suit"""
        haptic = EmotionMapping.get_haptic_pattern(emotion, intensity)
        
        payload = {
            "type": "full_body_haptic",
            "zones": haptic["zones"],
            "pattern": haptic["pattern"],
            "intensity": haptic["intensity"],
            "frequency": haptic["frequency"],
            "duration": haptic["duration"]
        }
        
        print(f"🦾 Tesla Suit: {', '.join(haptic['zones'])} 區域觸覺")
        
        return {
            "device": "Tesla Suit",
            "status": "success",
            "payload": payload
        }
    
    async def _send_to_bhaptics(self, emotion: str, intensity: float) -> Dict:
        """發送觸覺反饋到 bHaptics 背心"""
        haptic = EmotionMapping.get_haptic_pattern(emotion, intensity)
        
        payload = {
            "type": "vest_haptic",
            "pattern": haptic["pattern"],
            "zones": haptic["zones"],
            "intensity": haptic["intensity"],
            "duration": haptic["duration"]
        }
        
        print(f"🎽 bHaptics: {haptic['pattern']} 觸覺模式")
        
        return {
            "device": "bHaptics",
            "status": "success",
            "payload": payload
        }
    
    async def _send_to_aromajoin(self, emotion: str, intensity: float) -> Dict:
        """發送氣味到 Aromajoin"""
        aroma = EmotionMapping.get_aroma_profile(emotion, intensity)
        
        payload = {
            "type": "aroma",
            "scent": aroma["scent"],
            "notes": aroma["notes"],
            "intensity": aroma["intensity"],
            "duration": aroma["duration"]
        }
        
        print(f"👃 Aromajoin: {aroma['scent']} ({', '.join(aroma['notes'])})")
        
        return {
            "device": "Aromajoin",
            "status": "success",
            "payload": payload
        }
    
    async def _send_to_foodini(self, emotion: str, intensity: float) -> Dict:
        """發送味覺到 Foodini"""
        taste = EmotionMapping.get_taste_profile(emotion, intensity)
        
        payload = {
            "type": "taste",
            "flavor": taste["flavor"],
            "ingredients": taste["ingredients"],
            "intensity": taste["intensity"],
            "temperature": taste["temperature"],
            "texture": taste["texture"]
        }
        
        print(f"🍽️ Foodini: {taste['flavor']} ({', '.join(taste['ingredients'])})")
        
        return {
            "device": "Foodini",
            "status": "success",
            "payload": payload
        }
    
    def connect_device(self, device_type: str) -> bool:
        """連接設備"""
        if device_type in [d.value for d in DeviceType]:
            self.active_devices.add(device_type)
            print(f"✅ 已連接: {device_type}")
            return True
        return False
    
    def disconnect_device(self, device_type: str) -> bool:
        """斷開設備"""
        if device_type in self.active_devices:
            self.active_devices.remove(device_type)
            print(f"❌ 已斷開: {device_type}")
            return True
        return False
    
    def get_connected_devices(self) -> List[str]:
        """獲取已連接的設備列表"""
        return list(self.active_devices)


# 全局實例
sensory_hub = MultiSensoryHub()


if __name__ == "__main__":
    # 測試
    async def test():
        hub = MultiSensoryHub()
        
        # 連接所有設備
        hub.connect_device(DeviceType.APPLE_WATCH.value)
        hub.connect_device(DeviceType.RAYBAN_META.value)
        hub.connect_device(DeviceType.TESLA_SUIT.value)
        hub.connect_device(DeviceType.BHAPTICS.value)
        hub.connect_device(DeviceType.AROMAJOIN.value)
        hub.connect_device(DeviceType.FOODINI.value)
        
        # 測試廣播
        result = await hub.broadcast_to_all_devices(
            emotion="happy",
            intensity=0.8,
            content={
                "text": "這是一個快樂的時刻！",
                "images": ["img1.jpg", "img2.jpg"]
            }
        )
        
        print("\n📊 廣播結果：")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
