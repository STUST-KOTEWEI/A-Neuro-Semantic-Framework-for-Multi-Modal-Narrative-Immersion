# AI多感官智能閱讀器 - 完整版

一個集成了人工智慧技術的多感官閱讀體驗平台，現已升級包含用戶認證、訂閱管理和廣播生成功能。

## 🆕 新功能 (2024)

### 1. 用戶認證系統
- **多層級訂閱方案**: Free、EDU、Plus、Pro
- **安全認證**: JWT Token 基礎認證
- **使用量管理**: 基於訂閱等級的 API 限制

### 2. 訂閱方案詳情
| 方案 | API 呼叫/日 | TTS 分鐘/日 | 圖像生成/日 | 特殊功能 |
|------|-------------|-------------|-------------|----------|
| **Free** | 10 | 5 | 3 | 基礎功能 |
| **EDU** | 100 | 30 | 20 | 教育內容 |
| **Plus** | 500 | 120 | 50 | 廣播生成 |
| **Pro** | 無限制 | 無限制 | 無限制 | 所有功能 + API 存取 |

### 3. 10分鐘廣播生成
- **智能腳本生成**: 基於輸入主題自動創建節目腳本
- **時間軸管理**: 自動分割為10個1分鐘段落
- **語音合成**: 完整節目音頻生成
- **同步影像**: 情感化配圖支持

### 4. 增強 AI 功能
- **文本分析**: Google Gemini + Ollama 雙引擎
- **情感配圖**: 基於情感的智能圖像選擇
- **觸覺反饋**: 高精度觸覺模式生成
- **多語言 TTS**: ElevenLabs + gTTS 備援

## 🚀 快速開始

### 環境設置
```bash
# 安裝依賴
pip install -r requirements.txt

# 設置環境變數
cp .env.example .env
# 編輯 .env 加入 API Keys
```

### 啟動服務
```bash
# 啟動 FastAPI 服務器
python web/backend/main.py

# 服務運行在 http://localhost:8000
```

### 默認登入帳戶
- **管理員**: `admin@aireader.com` / `admin123` (Pro 會員)
- **示範用戶**: `demo@example.com` / `demo123` (Plus 會員)

## 📡 API 端點

### 認證相關
- `POST /auth/register` - 用戶註冊
- `POST /auth/login` - 用戶登入
- `GET /auth/profile` - 用戶資料
- `GET /auth/check` - 驗證 Token

### AI 功能
- `POST /generate_text_protected` - 受保護的文本生成
- `POST /generate_tts` - 語音合成
- `POST /generate_haptics` - 觸覺反饋
- `POST /select_images` - 情感配圖
- `POST /analyze_image` - 圖像分析

### 數據管理
- `GET /status` - 系統狀態
- `GET /haptic_patterns` - 觸覺模式列表

## 🔧 技術架構

### 後端框架
- **FastAPI**: 現代 Python Web 框架
- **Pydantic**: 數據驗證和序列化
- **JWT**: 安全認證機制
- **bcrypt**: 密碼加密

### AI 整合
- **Google Generative AI**: 文本生成和分析
- **Ollama**: 本地 LLM 處理
- **ElevenLabs**: 高品質語音合成
- **gTTS**: 備援語音合成

### 前端技術
- **TailwindCSS**: 響應式 UI 框架
- **Vanilla JavaScript**: 原生 JS 互動
- **Chart.js**: 數據視覺化

## 📊 使用量監控

系統提供即時使用量監控：
- **API 呼叫次數**: 每日追蹤和限制
- **TTS 分鐘數**: 語音合成時間統計
- **圖像生成數**: 配圖生成次數管理
- **視覺化進度條**: 直觀顯示剩餘額度

## 🎯 未來發展

### UI/App/Unity 開發計劃
1. **移動應用**: React Native / Flutter 版本
2. **Unity 整合**: 3D 沉浸式體驗
3. **桌面應用**: Electron 跨平台版本
4. **VR/AR 支援**: 虛擬實境擴展

### AI 模型改進
1. **自定義 Ollama 模型**: 針對性微調
2. **更小模型**: 優化效能和速度
3. **多模態融合**: 視覺+語音+觸覺整合
4. **實時處理**: 降低延遲和提升響應

## 🔒 安全性

- **JWT Token 認證**: 安全的無狀態認證
- **密碼加密**: bcrypt 哈希保護
- **API 限制**: 防止濫用和攻擊
- **CORS 設定**: 跨域請求控制

## 📝 開發日誌

### v2.0.0 (2024-12-27)
- ✅ 完整用戶認證系統
- ✅ 多層級訂閱方案
- ✅ 10分鐘廣播生成功能
- ✅ 使用量監控和限制
- ✅ 新版 reader.html 界面
- ✅ JWT 安全認證
- ✅ 密碼加密存儲

### v1.0.0 (之前版本)
- ✅ 基礎 AI 文本分析
- ✅ 語音合成 (TTS)
- ✅ 觸覺反饋模擬
- ✅ 情感配圖系統
- ✅ Google API 整合
- ✅ Ollama 本地 LLM

## 🤝 貢獻

歡迎提交 Issues 和 Pull Requests！

## 📄 授權

此專案採用 MIT 授權條款。

---

**AI多感官智能閱讀器** - 讓閱讀體驗更加沉浸和智能 🚀