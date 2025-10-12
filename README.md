# A Neuro-Semantic Framework for Multi-Modal Narrative Immersion 

## 專案願景 
故事的核心在於體驗，而非僅是文字。數百年來，我們透過視覺解碼符號來理解故事，但文字本身僅是通往故事世界的媒介。

Project H.O.L.O. 的使命，就是打破這個媒介的限制，提出一個大膽的問題：如果我們不僅能"閱讀"故事，而是能真正地"感受"它呢？ 

## 專案目標 
- 重新定義"閱讀"的體驗，讓讀者不僅僅是解讀文字，而是全方位感受故事中的情感與情境，成為故事的一部分。 

## 核心技術 
1. **深度語意分析**：
   - 使用自然語言處理 (NLP) 技術，將文本解構為語意單元。
   - 分析情感、語調、角色關係與故事背景。

2. **生成式 AI**：
   - 基於語意單元創建動態的聽覺體驗（例如角色對話、環境音效）。
   - 使用文本到聲音 (Text-to-Sound) 與文本到氣味 (Text-to-Scent) 的生成技術，模擬多感官回饋。

3. **多模態感知系統**：
   - 整合聽覺、觸覺與嗅覺回饋，打造沉浸式的敘事體驗。
   - 開發 API 供硬體設備（如觸覺反饋裝置）使用。

## 預期成果 
- 一個沉浸式敘事框架，能夠將任何文本轉化為多感官體驗。
- 支援多語言，應用於教育、娛樂與療癒場景。 

## MultisensoryReader-Orchestrator

我們已經實作了 MultisensoryReader-Orchestrator，這是一個協調文本處理、情感檢測、語音合成和觸覺/嗅覺設備控制的系統。

### 主要功能

- **ReaderAgent**: 文本攝取、分段處理和重點提取
- **EmotionAgent**: 從文本或語音樣本預測情感，並映射到 TTS 語音預設
- **DeviceAgent**: 將重點和情感事件映射到觸覺和嗅覺模式
- **MemoryAgent**: 用戶偏好和 RAG 搜索
- **Orchestrator**: 協調所有代理並實現主要工作流程

### API 端點

- `POST /orchestrator/play` - 開始播放文本並生成多感官體驗
- `POST /orchestrator/pause` - 暫停當前播放
- `POST /orchestrator/seek` - 跳轉到特定段落
- `GET /orchestrator/summary` - 獲取當前會話摘要

### 快速開始

1. 安裝依賴：
```bash
cd web/backend
pip install -r requirements.txt
```

2. 啟動後端服務：
```bash
uvicorn main:app --reload
```

3. 訪問 API 文檔：
http://localhost:8000/docs

4. 運行示例：
```bash
python examples/orchestrator_demo.py
```

詳細文檔請參考 [holo/orchestrator/README.md](holo/orchestrator/README.md)

## 版權與貢獻 
歡迎對此專案感興趣的開發者提供意見並提交 PR.