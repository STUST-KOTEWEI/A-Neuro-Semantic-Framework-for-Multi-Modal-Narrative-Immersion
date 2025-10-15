# 情緒驅動可編程物質生成系統

## 🎯 系統概述

這是一個整合鏡頭表情感測、RAG 圖像生成、Google Gemini AI 補充生成、以及可編程物質模擬的完整系統。

### 核心特性

1. **鏡頭表情檢測** 📷
   - 實時捕獲用戶表情
   - 使用 Google Gemini Vision API 分析情緒
   - 檢測主要情緒、強度、次要情緒、表情特徵
   - 支援的情緒：happy, sad, angry, fear, surprise, disgust, neutral

2. **混合圖像生成** 🎨
   - **RAG 生成**：最多 50 張圖像（從資料庫或基於查詢生成）
   - **Gemini 補充**：剩餘數量由 Google AI 生成
   - 每張圖像包含情緒上下文、標籤、生成 prompt

3. **可編程物質模擬** 🌊
   - 根據檢測到的情緒動態調整參數
   - 參數包括：密度、黏度、顏色、運動模式、轉換速度
   - 即時視覺化粒子系統
   - 6 種運動模式：bubble, drip, spike, scatter, burst, flow

## 📁 檔案結構

```text
/Users/kedewei/AI-Reader/
├── backend/
│   └── emotion_based_generator.py      # 核心生成引擎
├── web/frontend/
│   └── emotion_matter_generator.html   # 前端介面
├── integrated_server.py                 # FastAPI 後端服務器
├── test_emotion_system.py              # 整合測試腳本
└── modernreader.db                     # SQLite 資料庫

```text

## 🚀 快速開始

### 1. 啟動後端服務器

```bash
cd /Users/kedewei/AI-Reader
.venv/bin/python -m uvicorn integrated_server:app --host 0.0.0.0 --port 8010 --reload

```text

### 2. 打開前端介面

在瀏覽器訪問：

```bash
http://localhost:8010/web/emotion_matter_generator.html

```text

### 3. 使用流程

1. **啟動鏡頭**
   - 點擊「啟動鏡頭」按鈕
   - 允許瀏覽器使用鏡頭權限

2. **捕獲表情**
   - 對著鏡頭做出表情
   - 點擊「捕獲表情」按鈕
   - 系統會分析您的情緒

3. **設定參數**
   - 輸入查詢主題（例如：未來科技、自然風景）
   - 設定總圖像數量（50-200）
   - RAG 圖像數量固定為 50

4. **開始生成**
   - 點擊「開始生成」按鈕
   - 等待進度條完成
   - 查看生成結果

## 🔌 API 端點

### 1. 表情檢測

**端點**: `POST /api/detect-emotion`

**請求體**:

```json
{
  "image_base64": "base64_encoded_image_data"
}

```text

**回應**:

```json
{
  "primary_emotion": "happy",
  "intensity": 0.85,
  "secondary_emotions": ["excited", "calm"],
  "facial_features": "笑容明顯，眼睛彎曲",
  "timestamp": 1697355789,
  "status": "detected"
}

```text

### 2. 完整生成

**端點**: `POST /api/generate-complete`

**請求體**:

```json
{
  "camera_image_base64": "base64_encoded_image_data",
  "query": "未來科技",
  "total_count": 100
}

```text

**回應**:

```json
{
  "emotion": {
    "primary_emotion": "happy",
    "intensity": 0.85,
    "secondary_emotions": ["excited"],
    "status": "detected"
  },
  "rag_images": [
    {
      "id": "rag_1",
      "url": "https://...",
      "caption": "RAG 生成圖像 #1",
      "tags": ["happy", "tech"],
      "source": "RAG",
      "emotion_context": "happy"
    }
  ],
  "gemini_images": [
    {
      "id": "gemini_51",
      "url": "https://...",
      "caption": "Gemini 生成圖像 #51",
      "tags": ["happy", "tech", "AI"],
      "source": "Gemini",
      "prompt": "creative prompt...",
      "programmable_matter": {
        "density": 0.4,
        "viscosity": 0.3,
        "color": [255, 220, 100],
        "motion_pattern": "bubble",
        "transformation_speed": 0.7
      }
    }
  ],
  "all_images": [...],
  "programmable_matter_config": {
    "emotion_base": "happy",
    "intensity": 0.85,
    "global_params": {...},
    "image_count": 100,
    "rag_count": 50,
    "gemini_count": 50
  },
  "statistics": {
    "total_images": 100,
    "rag_images": 50,
    "gemini_images": 50,
    "emotion": "happy",
    "intensity": 0.85,
    "query": "未來科技",
    "timestamp": 1697355789
  }
}

```text

## 🎨 可編程物質參數

### 情緒映射

| 情緒 | 密度 | 黏度 | 顏色 (RGB) | 運動模式 |
|------|------|------|------------|----------|
| happy | 0.3 | 0.2 | [255, 220, 100] | bubble (上浮) |
| sad | 0.8 | 0.9 | [100, 150, 200] | drip (下滴) |
| angry | 0.9 | 0.3 | [255, 50, 50] | spike (尖刺) |
| fear | 0.4 | 0.7 | [150, 100, 200] | scatter (散射) |
| surprise | 0.5 | 0.1 | [255, 200, 0] | burst (爆發) |
| disgust | 0.7 | 0.8 | [150, 200, 100] | recoil (後退) |
| neutral | 0.5 | 0.5 | [200, 200, 200] | flow (流動) |

### 動畫效果

- **bubble**: 粒子向上浮動，輕盈感
- **drip**: 粒子向下滴落，沉重感
- **spike**: 粒子從中心向外擴散，激烈感
- **scatter**: 粒子隨機散射，不安感
- **burst**: 粒子爆發式擴散，驚訝感
- **recoil**: 粒子向後收縮，厭惡感
- **flow**: 粒子平穩流動，平靜感

## 🧪 測試

執行完整測試套件：

```bash
.venv/bin/python test_emotion_system.py

```text

測試包括：

1. ✅ 表情檢測 API
2. ✅ 完整生成流程（RAG 50 + Gemini 30）
3. ✅ 資料庫數據檢查

## 🔧 設定 Gemini API Key

如果要啟用真實的 Google Gemini 情緒檢測和圖像生成，需要設定 API Key：

```bash
export GEMINI_API_KEY="your_api_key_here"

```text

或在 `backend/emotion_based_generator.py` 中設定。

## 📊 資料庫結構

系統使用 SQLite 資料庫 (`modernreader.db`)，包含以下表：

1. **users** - 用戶資料
2. **emotion_detections** - 表情檢測記錄
3. **rag_images** - RAG 生成的圖像
4. **book_covers** - ISBN 書籍封面
5. **podcast_contents** - 播客內容
6. **nlp_analyses** - NLP 分析結果

## 🎯 使用情境

### 情境 1: 根據心情推薦閱讀內容

```text
用戶笑容 (happy) → 生成輕鬆、有趣的內容圖像
用戶皺眉 (sad) → 生成溫暖、療癒的內容圖像

```text

### 情境 2: 情緒日記視覺化

```text
捕獲每日表情 → 記錄情緒變化 → 生成個性化視覺日記

```text

### 情境 3: 沉浸式閱讀體驗

```text
檢測閱讀時的情緒 → 動態調整可編程物質效果 → 增強閱讀氛圍

```text

## 🚀 未來擴展

- [ ] 支援多人同時檢測
- [ ] 加入音樂推薦（根據情緒）
- [ ] 3D 可編程物質視覺化（Three.js）
- [ ] 情緒歷史追蹤與分析
- [ ] VR/AR 整合
- [ ] 實時情緒流動預測
- [ ] 社交情緒分享功能

## 📝 測試結果

```text
✅ 所有測試通過！

📊 統計資訊:

  - 總圖像數: 80
  - RAG 生成: 50
  - Gemini 補充: 30
  - 主要情緒: neutral
  - 情緒強度: 0.5

🌊 可編程物質配置:

  - 情緒基礎: neutral
  - 密度: 0.4
  - 黏度: 0.4
  - 顏色: [200, 200, 200]
  - 運動模式: flow

```text

## 💡 技術亮點

1. **WebRTC** - 即時鏡頭捕獲
2. **Canvas API** - 圖像處理與粒子動畫
3. **Google Gemini Vision** - 表情分析
4. **FastAPI** - 高性能後端
5. **SQLite** - 輕量級數據存儲
6. **Responsive Design** - 適配各種螢幕尺寸

## 📞 支援

如有問題，請檢查：

1. 服務器是否正常運行（端口 8010）
2. 瀏覽器是否允許鏡頭權限
3. API Key 是否正確設定（如使用真實 Gemini API）

---

**版本**: 1.0.0
**建立日期**: 2025-10-15
**作者**: AI-Reader Team

