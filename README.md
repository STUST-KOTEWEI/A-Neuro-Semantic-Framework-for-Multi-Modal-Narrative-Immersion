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

2. **影像識別與情緒分析**：
   - 整合 Google Vision API，實現影像情緒檢測。
   - 使用 PaddleOCR 提取文字，支持多語言和模糊影像。
   - 提供完整的圖片標籤識別和文字提取功能。

3. **生成式 AI**：
   - 使用 OpenAI GPT-4 API 生成表情文字與播客腳本。
   - 支持多種內容類型：摘要、分析、續寫等。
   - 基於語意單元創建動態的聽覺體驗（例如角色對話、環境音效）。
   - 使用文本到聲音 (Text-to-Sound) 與文本到氣味 (Text-to-Scent) 的生成技術，模擬多感官回饋。

4. **多感官輸出**：
   - 使用 Google TTS 生成語音，支持多語言。
   - 整合聽覺、觸覺與嗅覺回饋，打造沉浸式的敘事體驗。
   - 開發 API 供硬體設備（如觸覺反饋裝置）使用。

5. **多模態感知系統**：
   - 整合影像、文字、語音等多種輸入方式。
   - 提供跨平台的使用介面，支持掃描、播放與互動。

## 預期成果 
- 一個沉浸式敘事框架，能夠將任何文本轉化為多感官體驗。
- 完整的影像識別系統，支持情緒檢測和文字提取。
- 強大的生成式 AI 功能，可生成播客腳本、摘要、分析等內容。
- 支援多語言，應用於教育、娛樂與療癒場景。
- 直觀的跨平台使用介面，提供無障礙設計。

## API 端點
### 影像識別
- `POST /analyze_image` - 上傳圖片進行情緒檢測、標籤識別和文字提取

### 生成式 AI
- `POST /generate_content` - 生成表情文字、播客腳本、摘要等內容
- `POST /tts` - 文字轉語音

### 多模態體驗
- `POST /generate_immersion` - 生成沉浸式體驗（聽覺、感官、知識圖譜）

## 安裝與使用
### 後端
```bash
cd web/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 前端
```bash
cd web/frontend
npm install
npm run dev
```

## 環境變數配置
創建 `.env` 文件並設置以下變數：
```
OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json
```

## 版權與貢獻 
歡迎對此專案感興趣的開發者提供意見並提交 PR.