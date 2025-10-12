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
   - **[CoreML 情緒分析](docs/EMOTION_ANALYSIS_INTEGRATION.md)**: 在 iOS 裝置上進行即時文字情緒偵測。

2. **生成式 AI**：
   - 基於語意單元創建動態的聽覺體驗（例如角色對話、環境音效）。
   - 使用文本到聲音 (Text-to-Sound) 與文本到氣味 (Text-to-Scent) 的生成技術，模擬多感官回饋。

3. **多模態感知系統**：
   - 整合聽覺、觸覺與嗅覺回饋，打造沉浸式的敘事體驗。
   - 開發 API 供硬體設備（如觸覺反饋裝置）使用。

## 預期成果 
- 一個沉浸式敘事框架，能夠將任何文本轉化為多感官體驗。
- 支援多語言，應用於教育、娛樂與療癒場景。 

## 功能特色

### 🎭 情緒分析 (CoreML)
- 在 iOS 裝置上進行即時文字情緒偵測
- 支援多種情緒類別（開心、悲傷、生氣、中性、驚訝、恐懼）
- 使用 CoreML 優化，充分利用裝置 Neural Engine
- [查看完整文件](docs/EMOTION_ANALYSIS_INTEGRATION.md)

### 🔧 開發工具
- Python 模型轉換工具（支援 PyTorch 和 TensorFlow/Keras）
- Swift 情緒分析服務（可直接整合到 iOS App）
- 完整的文件和使用範例

## 快速開始

### 情緒分析整合

```bash
# 1. 轉換模型
cd scripts
python convert_emotion_model.py --framework keras --input model.h5 --output EmotionLSTM.mlpackage

# 2. 在 iOS 中使用
# 將 EmotionLSTM.mlpackage 加入到 Xcode 專案
# 使用 EmotionAnalysisService 進行分析
```

詳細步驟請參考 [CoreML 情緒分析整合文件](docs/EMOTION_ANALYSIS_INTEGRATION.md)。

## 版權與貢獻 
歡迎對此專案感興趣的開發者提供意見並提交 PR.