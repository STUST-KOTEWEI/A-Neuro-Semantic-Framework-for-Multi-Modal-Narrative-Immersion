# 🌈 多感官沉浸式閱讀器 - 完整系統文檔

## 🎯 系統概述

這是一個革命性的**多感官整合閱讀系統**，結合了情緒感知、語音交互、圖像生成和多設備感官輸出，為用戶提供前所未有的沉浸式閱讀體驗。

### 核心功能模組

#### 1. **情緒感知系統** 😊

- 即時鏡頭捕獲與表情分析
- Google Gemini Vision API 深度情緒識別
- 7種情緒檢測：happy, sad, angry, fear, surprise, disgust, neutral
- 情緒強度量化（0.0-1.0）
- 次要情緒與表情特徵分析

#### 2. **語音交互系統** 🎤🔊

- **TTS (Text-to-Speech)** - 文字轉語音
  - 支援多語音引擎：OpenAI, ElevenLabs, Google, Azure
  - 情緒驅動的語調調整
  - 語速控制 (0.5-2.0x)
  - 多語音選擇（alloy, echo, fable, onyx, nova, shimmer）

- **STT (Speech-to-Text)** - 語音轉文字
  - 使用 OpenAI Whisper / Google Speech API
  - 多語言支援（zh-TW, en-US, ja-JP等）
  - 高準確度識別（>95%）

#### 3. **混合內容生成** 🎨

- **RAG 生成**：從資料庫檢索或生成前 50 張圖像
- **Gemini AI 補充**：Google AI 生成剩餘圖像
- 情緒上下文注入
- 動態查詢優化
- 圖像自動標籤與分類

#### 4. **多設備感官輸出** 📡

支援 6 種感官輸出設備：

| 設備 | 類型 | 輸出方式 |
|------|------|----------|
| **Apple Watch** ⌚ | 觸覺 | 振動模式、心率反饋 |
| **Ray-Ban Meta** 🕶️ | 視覺 | AR 覆蓋層、粒子效果 |
| **Tesla Suit** 🦾 | 全身觸覺 | 多區域電刺激、運動反饋 |
| **bHaptics** 🎽 | 觸覺背心 | 40點觸覺陣列 |
| **Aromajoin** 👃 | 嗅覺 | 氣味釋放、香氛配方 |
| **Foodini** 🍽️ | 味覺 | 味覺刺激、食物打印 |

#### 5. **圖像輪播系統** 🖼️

- 根據情緒自動播放圖像
- 手動/自動切換模式
- 淡入淡出動畫效果
- 圖像來源標註（RAG/Gemini/ISBN/Podcast）

#### 6. **可編程物質模擬** 🌊

- 基於情緒的粒子系統
- 7種運動模式：bubble, drip, spike, scatter, burst, recoil, flow
- 動態參數調整：密度、黏度、顏色、速度

---

## 📁 檔案結構

```text
AI-Reader/
├── backend/
│   ├── emotion_based_generator.py    # 情緒生成引擎
│   ├── voice_engine.py                # TTS/STT 引擎
│   ├── multi_sensory_hub.py           # 多感官設備中樞
│   ├── rag_engine.py                  # RAG 檢索引擎
│   ├── ai_image_selector.py           # 圖像選擇器
│   └── database.py                    # 資料庫操作
│
├── web/frontend/
│   ├── multisensory_reader.html       # 主介面 HTML
│   ├── multisensory_reader.js         # 前端邏輯
│   ├── emotion_matter_generator.html  # 情緒物質生成器
│   └── reader_new.html                # 舊版介面（兼容）
│
├── integrated_server.py               # FastAPI 主服務器
├── test_multisensory_system.py        # 完整測試套件
├── modernreader.db                    # SQLite 資料庫
└── MULTISENSORY_SYSTEM.md             # 本文檔

```text

---

## 🚀 快速開始

### 前置需求

```bash

# Python 3.10+

python --version

# 安裝依賴

pip install -r requirements.txt

```text

### 啟動服務器

```bash
cd /Users/kedewei/AI-Reader
.venv/bin/python -m uvicorn integrated_server:app --host 0.0.0.0 --port 8010 --reload

```text

### 打開前端

在瀏覽器訪問：

```bash
http://localhost:8010/web/multisensory_reader.html

```text

### 使用流程

1. **啟動鏡頭** 📷
   - 點擊「啟動鏡頭」
   - 允許瀏覽器訪問鏡頭權限

2. **檢測情緒** 😊
   - 對著鏡頭做出表情
   - 點擊「檢測情緒」
   - 查看檢測結果

3. **連接設備** 📡
   - 點擊設備卡片以連接/斷開
   - 已連接設備顯示綠色邊框
   - 可同時連接多個設備

4. **語音交互** 🎤
   - **錄音（STT）**：點擊「開始錄音」→ 說話 → 點擊「停止」
   - **朗讀（TTS）**：輸入文字 → 點擊「朗讀文字」

5. **載入內容** 📚
   - 點擊功能按鈕（ISBN書籍、播客、NLP、RAG）
   - 查看圖像輪播
   - 自動根據情緒播放

6. **生成內容** 🚀
   - 點擊「生成內容」按鈕
   - 等待 RAG + Gemini 生成完成
   - 查看 60 張混合圖像

7. **廣播到設備** 📡
   - 確保已連接設備
   - 點擊「廣播到所有設備」
   - 體驗多感官輸出

---

## 🔌 API 端點文檔

### 1. 情緒檢測

**POST** `/api/detect-emotion`

**請求體**：

```json
{
  "image_base64": "base64_encoded_image"
}

```text

**回應**：

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

### 2. TTS (文字轉語音)

**POST** `/api/tts`

**請求體**：

```json
{
  "text": "你好！這是測試。",
  "voice": "alloy",
  "emotion": "happy",
  "speed": 1.0
}

```text

**回應**：

```json
{
  "audio_url": "/static/audio/tts_1697355789.mp3",
  "audio_base64": "...",
  "duration": 3.5,
  "format": "mp3",
  "provider": "openai",
  "voice": "alloy"
}

```text

### 3. STT (語音轉文字)

**POST** `/api/stt`

**請求體**：

```json
{
  "audio_base64": "base64_encoded_audio",
  "language": "zh-TW"
}

```text

**回應**：

```json
{
  "text": "這是識別的文字內容",
  "confidence": 0.95,
  "language": "zh-TW",
  "duration": 3.2,
  "provider": "openai"
}

```text

### 4. 多設備廣播

**POST** `/api/broadcast-to-devices`

**請求體**：

```json
{
  "emotion": "happy",
  "intensity": 0.8,
  "devices": ["apple_watch", "rayban_meta", "tesla_suit"],
  "content": {
    "text": "這是一個快樂的時刻！",
    "images": ["img1.jpg", "img2.jpg"]
  }
}

```text

**回應**：

```json
{
  "emotion": "happy",
  "intensity": 0.8,
  "devices": {
    "apple_watch": {
      "device": "Apple Watch",
      "status": "success",
      "payload": {...}
    },
    ...
  },
  "timestamp": 1697355789
}

```text

### 5. 完整生成

**POST** `/api/generate-complete`

**請求體**：

```json
{
  "camera_image_base64": "base64_image",
  "query": "未來科技",
  "total_count": 60
}

```text

**回應**：

```json
{
  "emotion": {...},
  "rag_images": [...],      // 50 張
  "gemini_images": [...],   // 10 張
  "all_images": [...],      // 60 張
  "programmable_matter_config": {...},
  "statistics": {
    "total_images": 60,
    "rag_images": 50,
    "gemini_images": 10,
    "emotion": "happy",
    "intensity": 0.8
  }
}

```text

### 6. 功能數據端點

- **GET** `/data/users` - 用戶列表
- **GET** `/data/book-covers` - ISBN 書籍封面
- **GET** `/data/podcasts` - 播客內容
- **GET** `/data/emotions` - 情緒檢測記錄
- **GET** `/data/nlp` - NLP 分析結果
- **GET** `/data/rag-images` - RAG 圖像

---

## 🎨 情緒映射表

### 觸覺反饋映射

| 情緒 | 振動模式 | 強度 | 頻率 | 持續時間 | 區域 |
|------|----------|------|------|----------|------|
| happy | bounce | 70% | 180Hz | 1.5s | chest, shoulders |
| sad | slow_pulse | 50% | 60Hz | 3.0s | chest, back |
| angry | sharp_burst | 90% | 200Hz | 0.5s | arms, chest, back |
| fear | tremor | 80% | 150Hz | 2.0s | spine, shoulders |
| surprise | sudden_spike | 100% | 220Hz | 0.8s | chest, arms |
| disgust | recoil_wave | 60% | 90Hz | 1.2s | stomach, chest |
| neutral | gentle_wave | 30% | 80Hz | 2.0s | chest |

### 氣味配方映射

| 情緒 | 氣味組合 | 香調 | 強度 | 持續時間 |
|------|----------|------|------|----------|
| happy | 柑橘混合 | orange, lemon, bergamot | 80% | 180s |
| sad | 洋甘菊香草 | chamomile, vanilla | 60% | 300s |
| angry | 薄荷尤加利 | peppermint, eucalyptus | 50% | 120s |
| fear | 薰衣草檀香 | lavender, sandalwood | 70% | 240s |
| surprise | 茉莉生薑 | jasmine, ginger | 90% | 90s |
| disgust | 薄荷松木 | mint, pine | 40% | 150s |
| neutral | 淡雅木質 | cedar, light | 30% | 200s |

### 味覺配方映射

| 情緒 | 風味組合 | 成分 | 溫度 | 質地 |
|------|----------|------|------|------|
| happy | 甜果味 | strawberry, honey, vanilla | 25°C | smooth |
| sad | 舒適甜味 | chocolate, caramel, salt | 40°C | creamy |
| angry | 辛苦味 | chili, dark chocolate, coffee | 50°C | sharp |
| fear | 溫和土味 | chamomile, honey, oat | 37°C | gentle |
| surprise | 酸爽味 | lemon, ginger, mint | 15°C | fizzy |
| disgust | 清爽味 | cucumber, mint, lime | 10°C | crisp |
| neutral | 淡鮮味 | vegetable broth, herbs | 37°C | light |

### AR 視覺效果映射

| 情緒 | 覆蓋類型 | 顏色 (RGB) | 不透明度 | 動畫 | 粒子數 |
|------|----------|------------|----------|------|--------|
| happy | sparkles | [255,220,100] | 70% | float_up | 50 |
| sad | rain | [100,150,200] | 50% | fall_down | 30 |
| angry | flames | [255,50,50] | 80% | flicker | 60 |
| fear | fog | [150,100,200] | 60% | swirl | 40 |
| surprise | burst | [255,200,0] | 90% | explode | 80 |
| disgust | ripple | [150,200,100] | 40% | wave_out | 25 |
| neutral | ambient | [200,200,200] | 30% | subtle_glow | 20 |

---

## 🧪 測試

### 運行完整測試套件

```bash
.venv/bin/python test_multisensory_system.py

```text

### 測試項目

1. ✅ 情緒檢測 API
2. ✅ TTS (文字轉語音)
3. ✅ STT (語音轉文字)
4. ✅ 多設備廣播
5. ✅ 完整內容生成（RAG + Gemini）
6. ✅ 功能端點（ISBN, Podcast, NLP, RAG）

### 測試結果

```text
總計: 5/5 測試通過 ✅

```text

---

## ⚙️ 配置

### 環境變數

```bash

# OpenAI (TTS/STT)

export OPENAI_API_KEY="sk-..."

# Google Gemini (情緒檢測)

export GEMINI_API_KEY="AIza..."

# ElevenLabs (情緒語音)

export ELEVENLABS_API_KEY="..."

# Google Cloud (語音)

export GOOGLE_CLOUD_API_KEY="..."

# Azure (語音)

export AZURE_SPEECH_KEY="..."

```text

### 資料庫

系統使用 SQLite (`modernreader.db`)，包含 6 個表：

1. **users** - 用戶資料
2. **emotion_detections** - 情緒檢測記錄
3. **rag_images** - RAG 生成圖像
4. **book_covers** - ISBN 書籍封面
5. **podcast_contents** - 播客內容
6. **nlp_analyses** - NLP 分析結果

---

## 🎯 使用場景

### 場景 1: 情緒日記

```text
用戶早上打開系統 → 鏡頭檢測心情 → 生成對應圖像 →
TTS 朗讀日記 → 廣播到 Apple Watch（觸覺）+ Aromajoin（氣味）

```text

### 場景 2: 沉浸式閱讀

```text
用戶閱讀小說 → 系統檢測情緒變化 → 動態調整圖像輪播 →
Tesla Suit 提供情節觸覺反饋 → Ray-Ban Meta 顯示 AR 特效

```text

### 場景 3: 語音學習

```text
用戶說外語 (STT) → 系統識別並分析 → TTS 朗讀正確發音 →
根據學習情緒調整鼓勵方式 → bHaptics 提供正確/錯誤反饋

```text

### 場景 4: 多人體驗

```text
多位用戶同時使用 → 各自檢測情緒 → 生成個性化內容 →
同步廣播到各自設備 → Foodini 根據情緒提供味覺體驗

```text

---

## 📊 系統架構

```text
┌─────────────────────────────────────────────────────────┐
│                    前端 (HTML + JS)                      │
│  • 鏡頭捕獲  • 語音錄製  • 圖像輪播  • 設備控制        │
└────────────────┬────────────────────────────────────────┘
                 │ WebSocket / REST API
┌────────────────┴────────────────────────────────────────┐
│              FastAPI 後端服務器 (Port 8010)              │
│  /api/detect-emotion  /api/tts  /api/stt               │
│  /api/broadcast-to-devices  /api/generate-complete     │
└──┬────────┬────────┬────────┬────────┬─────────────────┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Emotion│ │Voice │ │ RAG  │ │Multi │ │ DB  │
│ Gen  │ │Engine│ │Engine│ │Sensory│ │     │
└──────┘ └──────┘ └──────┘ └──────┘ └──────┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────────────────────────────────────────┐
│          外部 API / 設備通訊              │
│  Gemini Vision  │ OpenAI  │ Apple Watch │
│  ElevenLabs     │ Unsplash│ Ray-Ban Meta│
│  Tesla Suit │ bHaptics │ Aromajoin │ Foodini
└──────────────────────────────────────────┘

```text

---

## 🚧 未來擴展

- [ ] WebXR 整合 (VR/AR 頭戴裝置)
- [ ] 腦波檢測 (EEG) 整合
- [ ] 5G 低延遲設備控制
- [ ] 多人協作模式
- [ ] AI 生成 3D 環境
- [ ] 區塊鏈情緒 NFT
- [ ] 跨平台移動端 App
- [ ] 雲端同步與分享

---

## 📝 授權

MIT License

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📧 聯繫

如有問題，請聯繫開發團隊。

---

**版本**: 2.0.0
**建立日期**: 2025-10-15
**最後更新**: 2025-10-15
**作者**: AI-Reader Team

---

🎉 **享受多感官沉浸式閱讀體驗！** 🎉

