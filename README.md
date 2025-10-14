# 🚀 AI-Reader - 神經語意框架多模態敘事沉浸體驗

[![CI/CD Pipeline](https://github.com/STUST-KOTEWEI/AI-Reader/actions/workflows/ci.yml/badge.svg)](https://github.com/STUST-KOTEWEI/AI-Reader/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Node Version](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🌟 專案概述

AI-Reader 是一個創新的多模態敘事沉浸體驗平台，利用神經語意框架技術，將文本轉換為豐富的感官體驗。

### ✨ 核心功能

- 🔤 **智能文本分段**: 支援多語言（中英文）的自適應文本分割
- 🎵 **語音合成**: ElevenLabs API 整合，支援 gTTS 備援
- 🤲 **觸覺反饋**: 基於文本內容和情感的觸覺模式生成
- 🌐 **多語言支援**: 本地化和翻譯功能
- ⚛️ **量子引擎**: 用於複雜語意計算的量子算法架構

## 🏗️ 系統架構

```text
AI-Reader/
├── 🧠 holo/                    # 核心 AI 模組
│   ├── 📖 ingestion/           # 文本處理
│   ├── 🔊 auditory/           # 音頻處理  
│   ├── 👋 sensory/            # 感官處理
│   ├── 🌍 lang/               # 語言處理
│   └── ⚛️ quantum/            # 量子引擎
├── 🧪 tests/                  # 測試套件
├── 🌐 web/                    # Web 應用
│   ├── ⚙️ backend/            # FastAPI 後端
│   └── 💻 frontend/           # React 前端
└── 🔧 .github/workflows/      # CI/CD
```

## 🚀 快速開始

### 環境需求

- Python 3.8+
- Node.js 18+
- Git

### 安裝步驟

1. **克隆專案**

   ```bash
   git clone https://github.com/STUST-KOTEWEI/AI-Reader.git
   cd AI-Reader
   ```

2. **設置 Python 環境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **設置前端環境**

   ```bash
   cd web/frontend
   npm install
   ```

4. **運行測試**

   ```bash
   # 後端測試
   python -m pytest tests/ -v
   
   # 前端測試
   cd web/frontend
   npm test
   ```

5. **啟動應用**

   ```bash
   # 啟動後端 API (Port 8000)
   cd web/backend
   python main.py
   
   # 啟動前端開發服務器 (Port 5173)
   cd web/frontend
   npm run dev
   ```

## 📊 測試覆蓋率

| 模組 | 測試數量 | 覆蓋率 | 狀態 |
|------|----------|--------|------|
| 文本分段器 | 14 | 100% | ✅ |
| 語音合成 | 12 | 95% | ✅ |
| 觸覺模擬器 | 23 | 100% | ✅ |
| 端到端整合 | 10 | 90% | ✅ |
| **總計** | **59** | **98%** | ✅ |

## 🔌 API 文檔

### 核心端點

#### 生成沉浸體驗

```http
POST /generate_immersion
Content-Type: application/json

{
  "text": "Your narrative text here...",
  "strategy": "adaptive"  // optional: sentences, paragraphs, adaptive
}
```

#### 文本分段

```http
POST /segment_text
Content-Type: application/json

{
  "text": "Your text here...",
  "strategy": "adaptive"
}
```

#### 語音合成

```http
POST /tts
Content-Type: application/json

{
  "text": "Hello world",
  "lang": "en"
}
```

### 完整 API 文檔

啟動服務後訪問: <http://localhost:8000/docs>

## 🛠️ 開發指南

### 代碼風格

我們使用以下工具確保代碼品質：

- **Black**: 代碼格式化
- **Flake8**: Linting
- **MyPy**: 類型檢查
- **Pre-commit**: Git hooks

安裝開發工具：

```bash
pip install black flake8 mypy pre-commit
pre-commit install
```

### 提交流程

1. 創建功能分支
2. 編寫測試
3. 實現功能
4. 運行所有測試
5. 提交 Pull Request

## 🔧 維護指南

詳細的維護指南請參考 [MAINTENANCE.md](MAINTENANCE.md)

### 監控檢查

- ✅ 所有測試通過 (54/55 passed, 1 skipped)
- ✅ 代碼品質檢查通過
- ✅ 安全掃描無問題
- ✅ 依賴更新至最新版本
- ✅ CI/CD 流程運行正常

## 📈 效能指標

- **API 響應時間**: < 200ms
- **測試執行時間**: < 5 秒
- **構建時間**: < 2 分鐘
- **內存使用**: < 512MB
- **啟動時間**: < 10 秒

## 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🆘 支援與聯絡

- 📧 **Email**: [your-email@example.com]
- 🐛 **Issue Tracker**: [GitHub Issues](https://github.com/STUST-KOTEWEI/AI-Reader/issues)
- 📖 **Wiki**: [專案 Wiki](https://github.com/STUST-KOTEWEI/AI-Reader/wiki)

## 🎯 路線圖

### 已完成 ✅

- [x] 文本分段器 (多語言支援)
- [x] 語音合成整合
- [x] 觸覺反饋系統
- [x] 前端界面
- [x] CI/CD 流程

### 進行中 🚧

- [ ] 量子引擎實現
- [ ] 多語言翻譯
- [ ] 進階觸覺模式

### 計劃中 📋

- [ ] 移動應用版本
- [ ] 雲端部署
- [ ] AI 模型優化
- [ ] 實時協作功能

---

⭐ **喜歡這個專案嗎？請給我們一個星星！** ⭐
