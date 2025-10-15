# 播客功能說明 / Podcast Feature Documentation

## 概述 / Overview

AI多感官智能閱讀器現在支援播客生成功能！使用者可以將文字轉換為高品質的語音播客，支援多種語音風格和語言。

## 功能特點 / Features

### 🔒 解鎖機制 / Unlock Mechanism

播客功能需要解鎖才能使用，提供兩種解鎖方式：

1. **電子郵件註冊**
   - 輸入有效的電子郵件地址
   - 系統驗證格式（必須包含 @ 和 .）
   - 註冊成功後立即解鎖

2. **廠商代碼**
   - 輸入廠商提供的代碼
   - 測試用代碼：`DEMO2025`, `TEST2025`, `VENDOR2025`
   - 驗證成功後立即解鎖

### 🎙️ 播客編輯器 / Podcast Editor

解鎖後可使用完整的播客編輯器：

- **內容編輯器** - 大型文本輸入區域
- **語音選擇** - 6種預設語音：
  - 預設語音
  - Kore (女性，專業)
  - Aoede (女性，溫柔)
  - Charon (男性，沉穩)
  - Fenrir (男性，活潑)
  - Puck (童音，可愛)
- **語言選擇** - 5種語言：
  - 中文 (繁體)
  - 中文 (简体)
  - English
  - 日本語
  - 한국어

### 🎉 首次使用體驗 / First-time Experience

- 解鎖成功後顯示歡迎模態框
- 介紹播客功能的主要特點
- 解鎖狀態保存在 localStorage，下次訪問無需重新解鎖

### 🎧 播客控制 / Podcast Controls

- **生成** - 一鍵生成播客音頻
- **播放** - 內建音頻播放器
- **下載** - 下載為 MP3 文件
- **重新生成** - 清除當前內容重新開始

## 使用指南 / Usage Guide

### 1. 啟動系統 / Start System

#### 啟動後端 / Start Backend
```bash
cd web/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

後端將在 `http://127.0.0.1:8000` 運行

#### 打開前端 / Open Frontend
```bash
# 使用瀏覽器打開
open reader.html
# 或使用 HTTP 服務器
python3 -m http.server 8080
# 然後訪問 http://localhost:8080/reader.html
```

### 2. 解鎖播客功能 / Unlock Podcast Feature

1. 導航到播客部分（點擊導航欄的 "🎙️ 播客"）
2. 選擇解鎖方式：
   - **方式一**：輸入電子郵件，點擊「註冊並解鎖」
   - **方式二**：輸入廠商代碼（如 `DEMO2025`），點擊「使用代碼解鎖」
3. 成功後會顯示歡迎訊息

### 3. 生成播客 / Generate Podcast

1. 在編輯器中輸入播客內容
2. 選擇語音風格（預設為「預設語音」）
3. 選擇語言（預設為「中文 (繁體)」）
4. 點擊「🎙️ 生成播客音頻」
5. 等待生成完成
6. 使用播放器收聽，或下載音頻文件

## API 文檔 / API Documentation

### POST /podcast/register

註冊或使用廠商代碼解鎖播客功能。

**請求體 / Request Body:**
```json
{
  "email": "user@example.com"  // 電子郵件註冊
}
```
或
```json
{
  "vendor_code": "DEMO2025"  // 廠商代碼
}
```

**響應 / Response:**
```json
{
  "success": true,
  "message": "註冊成功！播客功能已解鎖。",
  "access_token": "user@example.com"
}
```

### POST /podcast/tts

生成播客音頻。

**請求體 / Request Body:**
```json
{
  "text": "這是播客內容",
  "voice": "Kore",
  "lang": "zh-tw"
}
```

**響應 / Response:**
- Content-Type: `audio/mpeg`
- Body: 音頻文件數據

### GET /podcast/voices

獲取可用語音列表。

**響應 / Response:**
```json
{
  "voices": [
    {
      "voice_id": "gtts",
      "name": "Google TTS",
      "description": "Fallback TTS using Google Text-to-Speech"
    }
  ],
  "default": "default"
}
```

## 測試 / Testing

### 運行 API 測試 / Run API Tests

```bash
cd /home/runner/work/AI-Reader/AI-Reader
python3 -m pip install httpx
python3 << 'EOF'
import sys
sys.path.append('.')
from web.backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# 測試電子郵件註冊
response = client.post("/podcast/register", json={"email": "test@example.com"})
assert response.json()["success"] == True
print("✓ 電子郵件註冊測試通過")

# 測試廠商代碼
response = client.post("/podcast/register", json={"vendor_code": "DEMO2025"})
assert response.json()["success"] == True
print("✓ 廠商代碼測試通過")

# 測試無效代碼
response = client.post("/podcast/register", json={"vendor_code": "INVALID"})
assert response.json()["success"] == False
print("✓ 無效代碼拒絕測試通過")

print("\n所有測試通過！")
EOF
```

## 故障排除 / Troubleshooting

### 問題：無法解鎖播客功能

**解決方案：**
1. 確認後端正在運行（訪問 http://127.0.0.1:8000）
2. 檢查瀏覽器控制台是否有錯誤
3. 嘗試不同的廠商代碼（DEMO2025, TEST2025, VENDOR2025）
4. 清除瀏覽器 localStorage：`localStorage.clear()`

### 問題：音頻生成失敗

**解決方案：**
1. 確認後端正在運行
2. 檢查 gTTS 是否已安裝：`pip install gTTS`
3. 確認網絡連接正常（gTTS 需要網絡）
4. 查看後端日誌錯誤訊息

### 問題：無法下載音頻

**解決方案：**
1. 確認已成功生成音頻（播放器中有音頻）
2. 檢查瀏覽器下載權限
3. 嘗試右鍵點擊播放器選擇「另存為」

## 技術架構 / Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (HTML/JS)                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Podcast Lock Screen                                 │ │
│  │  - Email Registration Form                           │ │
│  │  - Vendor Code Input                                 │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Podcast Generator (After Unlock)                    │ │
│  │  - Content Editor                                    │ │
│  │  - Voice Selection (6 options)                       │ │
│  │  - Language Selection (5 options)                    │ │
│  │  - Audio Player & Controls                           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI/Python)                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  POST /podcast/register                              │ │
│  │  - Email validation                                  │ │
│  │  - Vendor code verification                          │ │
│  │  - Access token generation                           │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  POST /podcast/tts                                   │ │
│  │  - Text-to-Speech generation (gTTS)                  │ │
│  │  - Voice & language processing                       │ │
│  │  - Audio streaming                                   │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  GET /podcast/voices                                 │ │
│  │  - Available voices listing                          │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 安全性 / Security

- 電子郵件格式驗證
- 廠商代碼白名單驗證
- 前端使用 localStorage 持久化（僅存儲 access_token）
- 後端使用內存存儲（生產環境應使用資料庫）

## 未來增強 / Future Enhancements

- [ ] 整合 ElevenLabs API 提供更高品質語音
- [ ] 添加音頻編輯功能（剪輯、合併、特效）
- [ ] 支援批量生成播客
- [ ] 添加播客模板和預設
- [ ] 實現播客歷史記錄
- [ ] 支援多人協作編輯
- [ ] 添加音頻分析和品質評估
- [ ] 支援導出為不同格式（WAV, FLAC, OGG）

## 授權 / License

本功能是 AI多感官智能閱讀器專案的一部分。
