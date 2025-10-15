"""
Modern Reader Mobile API Client
支持 Flutter 和 React Native 的統一 API 介面
"""

class ModernReaderAPI:
    def __init__(self, base_url="https://localhost:8443", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.session_token = None
    
    # 認證方法
    async def login(self, identifier, password):
        """
        登入 (支持 email 或 username)
        """
        data = {"password": password}
        if "@" in identifier:
            data["email"] = identifier
        else:
            data["username"] = identifier
        
        response = await self._post("/auth/login", data)
        if response.get("success"):
            self.session_token = response.get("token")
        return response
    
    async def register(self, email, username, password, tier="free"):
        """
        註冊新用戶
        """
        data = {
            "email": email,
            "username": username,
            "password": password,
            "subscription_tier": tier
        }
        return await self._post("/auth/register", data)
    
    # AI 功能
    async def generate_text(self, prompt, model="現代閱讀", style="immersive"):
        """
        AI 文本生成
        """
        data = {
            "text": prompt,
            "style": style,
            "use_google": False,
            "model": model
        }
        return await self._post("/ai/enhance_text", data)
    
    async def analyze_emotion(self, text):
        """
        情感分析
        """
        data = {"text": text}
        return await self._post("/ai/analyze_emotion", data)
    
    async def text_to_speech(self, text, voice="zh-TW-Standard-A"):
        """
        文字轉語音
        """
        data = {"text": text, "voice": voice}
        response = await self._post("/tts", data)
        return response  # 返回音頻文件路徑或 base64
    
    async def generate_haptics(self, text=None, emotion=None, intensity=0.5):
        """
        生成觸覺反饋模式
        """
        data = {"intensity": intensity}
        if text:
            data["text"] = text
        if emotion:
            data["emotion"] = emotion
        return await self._post("/generate_haptics", data)
    
    # 系統方法
    async def health_check(self):
        """
        健康檢查
        """
        return await self._get("/health")
    
    async def get_user_info(self):
        """
        獲取當前用戶資訊
        """
        return await self._get("/auth/me")
    
    # 私有方法
    async def _get(self, endpoint):
        """GET 請求"""
        headers = self._get_headers()
        # 實際實現會使用 http 客戶端
        return {"method": "GET", "url": f"{self.base_url}{endpoint}", "headers": headers}
    
    async def _post(self, endpoint, data):
        """POST 請求"""
        headers = self._get_headers()
        # 實際實現會使用 http 客戶端
        return {"method": "POST", "url": f"{self.base_url}{endpoint}", "headers": headers, "data": data}
    
    def _get_headers(self):
        """獲取請求標頭"""
        headers = {"Content-Type": "application/json"}
        if self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers