# AI-Reader System Architecture

## Overview

AI-Reader 整合了四個核心子系統，實現書籍的多模態沉浸式閱讀體驗。

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI-Reader System                          │
│                     (Project-HOLO v0.2.0)                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Frontend Interface                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  沉浸式體驗   │  │  書籍掃描     │  │  系統狀態     │         │
│  │  Immersion   │  │  Book Scan   │  │  Status      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                           │
│  FastAPI + Uvicorn (http://127.0.0.1:8000)                     │
│                                                                  │
│  Endpoints:                                                      │
│  • GET  /                        - API 根目錄                    │
│  • GET  /subsystems/status       - 子系統狀態                   │
│  • POST /scan_book               - 書籍掃描                     │
│  • POST /upload_book_image       - 上傳圖像                     │
│  • POST /generate/script         - 生成播客腳本                 │
│  • POST /generate/summary        - 生成摘要                     │
│  • POST /generate_immersion      - 生成沉浸式體驗               │
│  • POST /tts                     - 文字轉語音                   │
│  • GET  /personalization/{id}    - 個人化設定                  │
│  • POST /personalization/update  - 更新設定                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Python Imports
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Integration Layer                             │
│              holo/integration.py                                 │
│                                                                  │
│  AIReaderIntegration 類別：                                      │
│  • process_book_scan()           - 處理書籍掃描流程             │
│  • generate_immersive_experience() - 生成完整體驗               │
│  • apply_accessibility_features()  - 應用無障礙功能             │
│  • get_subsystem_status()         - 獲取系統狀態                │
└─────────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Subsystem 1   │  │   Subsystem 2   │  │   Subsystem 3   │
│      Image      │  │    AI Content   │  │ Multi-sensory   │
│  Recognition    │  │   Generation    │  │     Output      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
                                                   
                              │
                              ▼
                   ┌─────────────────┐
                   │   Subsystem 4   │
                   │   UI & Control  │
                   └─────────────────┘
```

---

## Subsystem 1: Image Recognition (圖像識別)

```
holo/image_recognition/
├── __init__.py
├── ocr_processor.py          # OCR文字識別
└── image_classifier.py       # 圖像分類

功能模組：
┌─────────────────────────────────────────┐
│          OCRProcessor                    │
│  • extract_text()      - 提取文字        │
│  • preprocess_image()  - 預處理圖像      │
│  • batch_extract()     - 批次處理        │
│                                          │
│  支援語言：                               │
│  zh-TW, zh-CN, en, ja, ko               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        ImageClassifier                   │
│  • classify_image()     - 分類書籍       │
│  • detect_book_cover()  - 檢測封面       │
│  • extract_features()   - 提取特徵       │
│                                          │
│  支援類別：                               │
│  fiction, non-fiction, textbook,        │
│  magazine, comic, children, reference   │
└─────────────────────────────────────────┘

技術基礎：
• Google Vision API
• MobileNet
• ResNet
• Vision Transformer (ViT)
```

---

## Subsystem 2: AI Content Generation (內容生成)

```
holo/content_generation/
├── __init__.py
├── script_generator.py       # 腳本生成器
├── summary_generator.py      # 摘要生成器
└── book_data_enricher.py     # 資料擴充器

功能模組：
┌─────────────────────────────────────────┐
│       ScriptGenerator                    │
│  • generate_podcast_script()            │
│  • generate_dialogue()                  │
│  • apply_prompt_engineering()           │
│                                          │
│  支援風格：                               │
│  conversational, narrative, educational,│
│  dramatic, casual, formal               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      SummaryGenerator                    │
│  • generate_summary()                   │
│  • extract_key_points()                 │
│  • generate_chapter_summaries()         │
│                                          │
│  摘要類型：                               │
│  brief, detailed, chapter-by-chapter,   │
│  key-points                             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│     BookDataEnricher                     │
│  • enrich_book_data()                   │
│  • search_by_isbn()                     │
│  • get_author_info()                    │
│  • get_recommendations()                │
│                                          │
│  整合：Open Library API                  │
└─────────────────────────────────────────┘

技術基礎：
• GPT-4 / GPT-3.5-turbo
• BLOOM
• Prompt Engineering
• RAG (Retrieval-Augmented Generation)
```

---

## Subsystem 3: Multi-sensory Output (多感官輸出)

```
holo/sensory/
├── subtitle_generator.py     # 字幕生成
├── image_generator.py        # 圖像生成
├── music_generator.py        # 音樂生成
├── haptic_controller.py      # 觸覺控制
└── neuro_stimulator.py       # 神經刺激

功能模組：
┌─────────────────────────────────────────┐
│     SubtitleGenerator                    │
│  • generate_subtitles()                 │
│  • format_as_srt()                      │
│                                          │
│  支援格式：SRT, VTT, ASS                 │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       ImageGenerator                     │
│  • generate_image()                     │
│  • generate_scene_illustration()        │
│  • enhance_image_quality()              │
│                                          │
│  支援風格：                               │
│  realistic, anime, oil-painting,        │
│  watercolor, sketch, digital-art,       │
│  3d-render                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       MusicGenerator                     │
│  • generate_background_music()          │
│  • generate_sound_effect()              │
│  • analyze_emotion_from_text()          │
│  • create_adaptive_soundtrack()         │
│                                          │
│  支援情緒：                               │
│  happy, sad, energetic, calm,           │
│  suspenseful, romantic, mysterious,     │
│  epic, peaceful                         │
└─────────────────────────────────────────┘

技術基礎：
• gTTS (Text-to-Speech)
• DALL-E / Stable Diffusion
• 音樂生成算法
• ICMS 觸覺技術
• 電子皮膚技術
```

---

## Subsystem 4: UI & Control (使用者介面控制)

```
holo/ui_control/
├── __init__.py
├── accessibility.py          # 無障礙管理
└── personalization.py        # 個人化管理

功能模組：
┌─────────────────────────────────────────┐
│    AccessibilityManager                  │
│  • enable_feature()                     │
│  • get_aria_attributes()                │
│  • get_keyboard_shortcuts()             │
│  • apply_color_scheme()                 │
│                                          │
│  無障礙功能：                             │
│  • screen_reader      - 螢幕閱讀器       │
│  • high_contrast      - 高對比度         │
│  • large_text         - 大字體          │
│  • voice_control      - 語音控制         │
│  • keyboard_navigation - 鍵盤導航        │
│  • closed_captions    - 隱藏字幕         │
│                                          │
│  標準：WAI-ARIA 1.2                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   PersonalizationManager                 │
│  • get_user_profile()                   │
│  • update_setting()                     │
│  • export_settings()                    │
│  • import_settings()                    │
│  • get_recommended_settings()           │
│                                          │
│  個人化設定：                             │
│  • language          - 語言              │
│  • voice_speed       - 語音速度          │
│  • voice_gender      - 語音性別          │
│  • theme             - 主題              │
│  • font_size         - 字體大小          │
│  • reading_mode      - 閱讀模式          │
│  • auto_play         - 自動播放          │
│  • notification_enabled - 通知          │
└─────────────────────────────────────────┘

技術基礎：
• WAI-ARIA 1.2 標準
• React (Frontend)
• Flutter / React Native (Mobile)
• 跨平台 UI 框架
```

---

## Data Flow Diagram (資料流程圖)

### 書籍掃描流程

```
使用者上傳書籍封面
      │
      ▼
┌─────────────┐
│ 圖像預處理   │ ← Subsystem 1
└─────────────┘
      │
      ▼
┌─────────────┐
│ OCR文字識別 │ ← Subsystem 1
└─────────────┘
      │
      ▼
┌─────────────┐
│ 圖像分類    │ ← Subsystem 1
└─────────────┘
      │
      ▼
┌─────────────┐
│ 封面檢測    │ ← Subsystem 1
└─────────────┘
      │
      ▼
┌─────────────┐
│ 資料擴充    │ ← Subsystem 2 (Open Library)
└─────────────┘
      │
      ▼
返回完整書籍資訊
```

### 沉浸式體驗生成流程

```
使用者輸入文本
      │
      ▼
┌─────────────┐
│ 內容分析    │ ← Subsystem 2
└─────────────┘
      │
      ├─────────────────────────────────┐
      │                                 │
      ▼                                 ▼
┌─────────────┐                 ┌─────────────┐
│ 腳本生成    │ ← Subsystem 2   │ 摘要生成    │ ← Subsystem 2
└─────────────┘                 └─────────────┘
      │                                 │
      └─────────────┬───────────────────┘
                    ▼
            ┌──────────────┐
            │ 情緒分析      │ ← Subsystem 3
            └──────────────┘
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ 字幕生成  │  │ 配圖生成  │  │ 配樂生成  │ ← Subsystem 3
└──────────┘  └──────────┘  └──────────┘
      │             │             │
      └─────────────┼─────────────┘
                    ▼
            ┌──────────────┐
            │ 個人化調整     │ ← Subsystem 4
            └──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │ 無障礙處理     │ ← Subsystem 4
            └──────────────┘
                    │
                    ▼
            完整沉浸式體驗
```

---

## Technology Stack (技術堆疊)

### Backend
```
Language:     Python 3.x
Framework:    FastAPI
Server:       Uvicorn (ASGI)
Dependencies: 
  - pydantic   (Data validation)
  - gTTS       (Text-to-Speech)
  - typing     (Type hints)
```

### Frontend
```
Language:     JavaScript (ES6+)
Framework:    React 19.x
Build Tool:   Vite
UI Library:   Custom CSS
Testing:      Vitest
```

### AI/ML Models (Planned Integration)
```
OCR:          Google Vision API, Tesseract
Image:        MobileNet, ResNet, ViT
Generation:   GPT-4, BLOOM
Image Gen:    DALL-E, Stable Diffusion
TTS:          gTTS, Azure TTS
```

---

## File Structure

```
AI-Reader/
├── holo/                           # 核心子系統
│   ├── image_recognition/          # 子系統 1
│   │   ├── __init__.py
│   │   ├── ocr_processor.py
│   │   └── image_classifier.py
│   ├── content_generation/         # 子系統 2
│   │   ├── __init__.py
│   │   ├── script_generator.py
│   │   ├── summary_generator.py
│   │   └── book_data_enricher.py
│   ├── sensory/                    # 子系統 3
│   │   ├── subtitle_generator.py
│   │   ├── image_generator.py
│   │   ├── music_generator.py
│   │   ├── haptic_controller.py
│   │   └── neuro_stimulator.py
│   ├── ui_control/                 # 子系統 4
│   │   ├── __init__.py
│   │   ├── accessibility.py
│   │   └── personalization.py
│   └── integration.py              # 整合層
│
├── web/
│   ├── backend/                    # FastAPI 後端
│   │   ├── main.py                 # API 端點
│   │   └── requirements.txt
│   └── frontend/                   # React 前端
│       ├── src/
│       │   ├── App.jsx             # 主應用
│       │   └── App.css             # 樣式
│       └── package.json
│
├── README.md                       # 專案說明
├── SUBSYSTEMS.md                   # 子系統詳細文檔
└── ARCHITECTURE.md                 # 本文件
```

---

## Deployment Architecture (部署架構)

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │  Load Balancer │
              └────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌─────────────┐        ┌─────────────┐
    │  Frontend   │        │  Frontend   │
    │   Server    │        │   Server    │
    │  (Static)   │        │  (Static)   │
    └─────────────┘        └─────────────┘
           │                       │
           └───────────┬───────────┘
                       │
                       ▼
              ┌────────────────┐
              │   API Gateway  │
              └────────────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌─────────────┐        ┌─────────────┐
    │  Backend    │        │  Backend    │
    │   Server    │        │   Server    │
    │  (FastAPI)  │        │  (FastAPI)  │
    └─────────────┘        └─────────────┘
           │                       │
           └───────────┬───────────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌─────────────┐        ┌─────────────┐
    │  Database   │        │  AI Models  │
    │  (User Data)│        │   Cache     │
    └─────────────┘        └─────────────┘
```

---

## Performance Considerations (效能考量)

### 響應時間目標
- OCR 處理: < 3 秒
- 內容生成: < 5 秒
- 圖像生成: < 10 秒
- TTS 合成: < 2 秒
- API 回應: < 500ms

### 優化策略
1. **快取機制**: Redis 快取常用書籍資料
2. **異步處理**: 大型任務使用 Celery 後台處理
3. **CDN**: 靜態資源使用 CDN 加速
4. **負載均衡**: 多實例部署分散負載
5. **資料庫優化**: 索引優化，查詢優化

---

## Security Considerations (安全考量)

1. **API 認證**: JWT Token 認證
2. **CORS 設定**: 限制允許的來源
3. **輸入驗證**: Pydantic 模型驗證
4. **檔案上傳**: 檔案類型和大小限制
5. **速率限制**: API 請求頻率限制
6. **HTTPS**: 所有通訊使用 TLS/SSL

---

## Future Roadmap (未來規劃)

### Phase 1 (Q1 2025)
- [ ] 整合真實的 Google Vision API
- [ ] 實現 GPT-4 API 連接
- [ ] 完整的使用者認證系統

### Phase 2 (Q2 2025)
- [ ] 移動應用開發 (Flutter)
- [ ] 實時協作功能
- [ ] 離線模式支援

### Phase 3 (Q3 2025)
- [ ] IoT 設備整合
- [ ] 觸覺回饋硬體支援
- [ ] 量子運算實驗

### Phase 4 (Q4 2025)
- [ ] 多語言 UI 完整支援
- [ ] AI 模型微調和優化
- [ ] 企業級部署方案

---

## Contributing (貢獻指南)

歡迎貢獻！請參考以下步驟：

1. Fork 本專案
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## License (授權)

本專案遵循 MIT 授權條款。

---

**Last Updated**: 2025-10-12  
**Version**: 0.2.0  
**Maintainer**: STUST-KOTEWEI
