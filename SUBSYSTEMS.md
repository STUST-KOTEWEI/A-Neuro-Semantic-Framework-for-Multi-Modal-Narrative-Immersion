# AI-Reader 子系統整合文檔

## 概述

AI-Reader 專案整合了四個主要子系統，共同實現多模態敘事沉浸體驗：

1. **Image Recognition Subsystem** (圖像識別子系統)
2. **AI Content Generation Subsystem** (內容生成子系統)
3. **Multi-sensory Output Subsystem** (多感官輸出子系統)
4. **UI & Control Subsystem** (使用者介面控制子系統)

---

## 1. Image Recognition Subsystem (圖像識別子系統)

### 目標
辨識書籍封面圖像與文字，支援模糊影像、低光源、多語言OCR，適用於雲端與離線環境。

### 技術選型
- Google Vision API 與 MobileNet 模型整合
- 支援模糊影像、低光源處理
- 多語言 OCR（中文繁體/簡體、英文、日文、韓文）
- 雲端與離線雙模式運作

### 模組組成

#### OCRProcessor (`holo/image_recognition/ocr_processor.py`)
```python
from holo.image_recognition import OCRProcessor

# 初始化
ocr = OCRProcessor(use_cloud=False)

# 提取文字
result = ocr.extract_text(image_data, language='zh-TW')
# 返回: {'text': '...', 'confidence': 0.95, 'language': 'zh-TW', ...}
```

**主要功能：**
- `extract_text()`: 從圖像提取文字
- `preprocess_image()`: 預處理圖像（降噪、增強對比度）
- `batch_extract()`: 批次處理多張圖像

#### ImageClassifier (`holo/image_recognition/image_classifier.py`)
```python
from holo.image_recognition import ImageClassifier

# 初始化
classifier = ImageClassifier(model_type='mobilenet')

# 分類書籍
result = classifier.classify_image(image_data)
# 返回: {'primary_category': 'fiction', 'confidence': 0.89, ...}
```

**主要功能：**
- `classify_image()`: 分類書籍類型
- `detect_book_cover()`: 檢測是否為書籍封面
- `extract_features()`: 提取圖像特徵向量

### 引用技術文獻
1. 用於影像識別的深度殘餘學習（ResNet）
2. 深度卷積神經網路的 ImageNet 分類（AlexNet）
3. 深度學習影像資料增強的調查
4. 視覺變換器（ViT）技術

---

## 2. AI Content Generation Subsystem (內容生成子系統)

### 目標
生成播客腳本與書籍摘要，支援多語言與風格控制。

### 技術選型
- 使用 GPT-4、BLOOM 等大型語言模型
- 結合 Open Library API 擴充書籍資料
- 透過 Prompt Engineering 控制風格與結構
- 支援多語言與在地化生成

### 模組組成

#### ScriptGenerator (`holo/content_generation/script_generator.py`)
```python
from holo.content_generation import ScriptGenerator

# 初始化
generator = ScriptGenerator(model='gpt-4')

# 生成播客腳本
script = generator.generate_podcast_script(
    content="書籍內容...",
    style='conversational',
    language='zh-TW',
    duration_minutes=10
)
```

**主要功能：**
- `generate_podcast_script()`: 生成播客腳本
- `generate_dialogue()`: 生成多人對話
- `apply_prompt_engineering()`: 應用提示詞工程技術

**支援風格：**
- conversational（對話式）
- narrative（敘事式）
- educational（教育式）
- dramatic（戲劇化）
- casual（輕鬆式）
- formal（正式）

#### SummaryGenerator (`holo/content_generation/summary_generator.py`)
```python
from holo.content_generation import SummaryGenerator

# 初始化
summarizer = SummaryGenerator()

# 生成摘要
summary = summarizer.generate_summary(
    content="書籍內容...",
    summary_type='brief',
    language='zh-TW',
    max_length=500
)
```

**主要功能：**
- `generate_summary()`: 生成書籍摘要
- `extract_key_points()`: 提取關鍵要點
- `generate_chapter_summaries()`: 生成章節摘要

**摘要類型：**
- brief（簡要）
- detailed（詳細）
- chapter-by-chapter（逐章）
- key-points（要點式）

#### BookDataEnricher (`holo/content_generation/book_data_enricher.py`)
```python
from holo.content_generation import BookDataEnricher

# 初始化
enricher = BookDataEnricher()

# 擴充書籍資料
book_info = enricher.enrich_book_data(
    book_title="書名",
    author="作者",
    isbn="ISBN編號"
)
```

**主要功能：**
- `enrich_book_data()`: 整合 Open Library 資料
- `search_by_isbn()`: 透過 ISBN 搜尋
- `get_author_info()`: 獲取作者資訊
- `get_recommendations()`: 獲取推薦書籍

### 引用技術文獻
1. Transformer 架構（Attention is All You Need）
2. GPT-3 與 Few-Shot Learning 技術
3. 提示詞工程（Prompt Engineering Techniques for LLMs）
4. 檢索增強生成（Retrieval-Augmented Generation, RAG）

---

## 3. Multi-sensory Output Subsystem (多感官輸出子系統)

### 目標
將生成內容轉化為語音、字幕、配圖、配樂與觸覺回饋，支援未來量子與 Vision-based 裝置。

### 技術選型
- 語音合成（TTS）
- 字幕生成（SRT/VTT/ASS格式）
- AI圖像生成（DALL-E, Stable Diffusion）
- 背景音樂與音效生成
- 觸覺回饋支援

### 模組組成

#### SubtitleGenerator (`holo/sensory/subtitle_generator.py`)
```python
from holo.sensory.subtitle_generator import SubtitleGenerator

# 初始化
sub_gen = SubtitleGenerator(format='srt')

# 生成字幕
subtitles = sub_gen.generate_subtitles(
    text="文本內容...",
    audio_duration=120,
    language='zh-TW'
)

# 格式化為 SRT
srt_content = sub_gen.format_as_srt(subtitles)
```

**支援格式：**
- SRT（SubRip）
- VTT（WebVTT）
- ASS（Advanced SubStation Alpha）

#### ImageGenerator (`holo/sensory/image_generator.py`)
```python
from holo.sensory.image_generator import ImageGenerator

# 初始化
img_gen = ImageGenerator(model='stable-diffusion')

# 生成圖像
images = img_gen.generate_image(
    prompt="一片森林在夜晚的場景",
    style='realistic',
    size='512x512',
    num_images=1
)

# 生成場景插圖
scene = img_gen.generate_scene_illustration(
    scene_description="森林場景",
    characters=['主角', '配角'],
    setting='夜晚'
)
```

**支援風格：**
- realistic（寫實）
- anime（動漫）
- oil-painting（油畫）
- watercolor（水彩）
- sketch（素描）
- digital-art（數位藝術）
- 3d-render（3D渲染）

#### MusicGenerator (`holo/sensory/music_generator.py`)
```python
from holo.sensory.music_generator import MusicGenerator

# 初始化
music_gen = MusicGenerator()

# 生成背景音樂
music = music_gen.generate_background_music(
    mood='calm',
    duration_seconds=60,
    instruments=['piano', 'strings']
)

# 分析情緒
emotions = music_gen.analyze_emotion_from_text(text)

# 生成音效
sfx = music_gen.generate_sound_effect(
    effect_type='rain',
    duration_seconds=5.0
)
```

**支援情緒：**
- happy（愉快）
- sad（悲傷）
- energetic（活力）
- calm（平靜）
- suspenseful（懸疑）
- romantic（浪漫）
- mysterious（神秘）
- epic（史詩）
- peaceful（安詳）

### 引用技術文獻
1. ICMS 模擬真實觸覺技術
2. SES 提升虛擬觸覺辨識
3. 穿戴式多感官裝置
4. 電子皮膚技術

---

## 4. UI & Control Subsystem (使用者介面控制子系統)

### 目標
設計簡潔直覺的使用介面，支援掃描、播放與互動，並強調無障礙設計與個人化設定。

### 技術選型
- 跨平台部署（手機、平板、電腦、IoT）
- 無障礙設計（WAI-ARIA 1.2標準）
- 個人化設定
- 鍵盤導航與語音控制

### 模組組成

#### AccessibilityManager (`holo/ui_control/accessibility.py`)
```python
from holo.ui_control import AccessibilityManager

# 初始化
accessibility = AccessibilityManager()

# 啟用功能
accessibility.enable_feature('screen_reader')
accessibility.enable_feature('high_contrast')

# 獲取 ARIA 屬性
aria = accessibility.get_aria_attributes('button')

# 獲取鍵盤快捷鍵
shortcuts = accessibility.get_keyboard_shortcuts()

# 應用色彩方案
colors = accessibility.apply_color_scheme('high-contrast')
```

**無障礙功能：**
- screen_reader（螢幕閱讀器）
- high_contrast（高對比度）
- large_text（大字體）
- voice_control（語音控制）
- keyboard_navigation（鍵盤導航）
- closed_captions（隱藏字幕）

**鍵盤快捷鍵：**
- Ctrl+P: 播放/暫停
- Ctrl+S: 掃描書籍
- Ctrl+H: 顯示說明
- Ctrl++: 增大字體
- Ctrl+-: 減小字體
- Space: 播放/暫停
- Esc: 關閉對話框

#### PersonalizationManager (`holo/ui_control/personalization.py`)
```python
from holo.ui_control import PersonalizationManager

# 初始化
personalization = PersonalizationManager()

# 獲取使用者配置
profile = personalization.get_user_profile('user_123')

# 更新設定
personalization.update_setting('language', 'zh-TW')
personalization.update_setting('voice_speed', 1.2)

# 匯出/匯入設定
settings = personalization.export_settings()
personalization.import_settings(settings)

# 獲取推薦設定
recommendations = personalization.get_recommended_settings({
    'visual_impairment': True
})
```

**個人化設定項目：**
- language（語言）
- voice_speed（語音速度）
- voice_gender（語音性別）
- theme（主題）
- font_size（字體大小）
- reading_mode（閱讀模式）
- auto_play（自動播放）
- notification_enabled（通知啟用）

### 引用技術文獻
1. 無障礙介面設計綜述
2. WAI-ARIA 1.2 標準
3. 生成式 AI 與包容性設計
4. 跨平台 UI 框架技術（Flutter、React Native）

---

## 整合層 (Integration Layer)

### AIReaderIntegration (`holo/integration.py`)

整合所有四個子系統的核心類別：

```python
from holo.integration import AIReaderIntegration

# 初始化整合系統
integration = AIReaderIntegration()

# 處理書籍掃描
scan_result = integration.process_book_scan(image_data, user_profile)

# 生成沉浸式體驗
experience = integration.generate_immersive_experience(content, user_profile)

# 應用無障礙功能
accessible_content = integration.apply_accessibility_features(
    content,
    accessibility_needs={'screen_reader': True, 'high_contrast': True}
)

# 獲取子系統狀態
status = integration.get_subsystem_status()
```

### 工作流程

#### 1. 書籍掃描流程
```
圖像輸入 → OCR識別 → 圖像分類 → 書籍封面檢測 → Open Library擴充 → 結果輸出
```

#### 2. 沉浸式體驗生成流程
```
文本輸入 → 內容生成（腳本+摘要） → 多感官輸出（字幕+配圖+音樂） → 個人化調整 → 體驗輸出
```

---

## API 端點

### 後端 API (`web/backend/main.py`)

#### 基礎端點
- `GET /` - API 根目錄
- `GET /subsystems/status` - 獲取所有子系統狀態

#### 圖像識別
- `POST /scan_book` - 掃描書籍封面（Base64）
- `POST /upload_book_image` - 上傳書籍圖像文件

#### 內容生成
- `POST /generate/script` - 生成播客腳本
- `POST /generate/summary` - 生成書籍摘要
- `POST /generate_immersion` - 生成完整沉浸式體驗

#### 多感官輸出
- `POST /tts` - 文字轉語音

#### 使用者控制
- `GET /personalization/{user_id}` - 獲取個人化設定
- `POST /personalization/update` - 更新個人化設定

---

## 前端介面

### 功能選項卡

1. **沉浸式體驗**
   - 文本輸入
   - 生成沉浸式體驗
   - 播放語音
   - 顯示結果（聽覺、感官、內容生成）

2. **書籍掃描**
   - 圖像上傳
   - OCR識別結果
   - 圖像分類
   - 書籍資訊顯示

3. **系統狀態**
   - 查看四個子系統運作狀態
   - 支援語言清單
   - 模組狀態監控

---

## 安裝與使用

### 後端設置

```bash
# 安裝依賴
cd web/backend
pip install -r requirements.txt

# 啟動後端服務
uvicorn main:app --reload
```

### 前端設置

```bash
# 安裝依賴
cd web/frontend
npm install

# 啟動開發服務器
npm run dev
```

---

## 未來擴展

### 計劃中的功能

1. **圖像識別**
   - 整合實際的 Google Vision API
   - 支援更多語言
   - 實時OCR處理

2. **內容生成**
   - 整合真實的 GPT-4 API
   - 實現 RAG 檢索增強
   - 更多風格選項

3. **多感官輸出**
   - 實際的圖像生成模型整合
   - 真實的音樂生成
   - 觸覺設備連接

4. **UI控制**
   - 移動應用開發（Flutter/React Native）
   - IoT 設備支援
   - 更多無障礙功能

---

## 授權與貢獻

歡迎對此專案感興趣的開發者提供意見並提交 PR。

## 聯繫方式

如有問題或建議，請開啟 GitHub Issue。
