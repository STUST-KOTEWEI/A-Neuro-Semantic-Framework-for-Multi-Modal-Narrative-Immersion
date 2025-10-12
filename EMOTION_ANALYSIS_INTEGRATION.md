# CoreML 情緒分析整合指南

本文檔說明如何將情緒分析模型整合到 AI-Reader 應用程式中。

## 概述

這個整合包含兩個主要部分：
1. **Python 模型轉換**：將 PyTorch 或 TensorFlow/Keras 模型轉換為 CoreML 格式
2. **Swift 服務實作**：在 iOS 應用程式中使用 CoreML 模型進行情緒分析

## 第一步：模型轉換 (Python)

### 安裝依賴

首先安裝必要的 Python 套件：

```bash
# 安裝 coremltools
pip install coremltools

# 根據您的模型格式安裝對應的深度學習框架
# 對於 TensorFlow/Keras 模型：
pip install tensorflow

# 對於 PyTorch 模型：
pip install torch
```

### 使用轉換腳本

本專案提供了 `convert_emotion_model.py` 腳本來執行模型轉換。

#### 從 TensorFlow/Keras (.h5) 轉換

```bash
python convert_emotion_model.py \
    --input path/to/your/model.h5 \
    --format keras \
    --output EmotionLSTM.mlpackage
```

#### 從 PyTorch (.pt) 轉換

```bash
python convert_emotion_model.py \
    --input path/to/your/model.pt \
    --format pytorch \
    --input-shape 1,128 \
    --output EmotionLSTM.mlpackage
```

**參數說明：**
- `--input`: 輸入模型檔案的路徑
- `--format`: 模型格式 (`keras` 或 `pytorch`)
- `--output`: 輸出 CoreML 模型的路徑（預設：EmotionLSTM.mlpackage）
- `--input-shape`: PyTorch 模型的輸入形狀（預設：1,128）

### 轉換腳本功能

`convert_emotion_model.py` 提供以下功能：

1. **自動載入模型**：支援 Keras (.h5) 和 PyTorch (.pt) 格式
2. **模型追蹤**：對 PyTorch 模型進行 JIT 追蹤以支援 CoreML 轉換
3. **設定元數據**：自動為 CoreML 模型添加描述、版本等資訊
4. **輸入輸出描述**：清楚標註模型的輸入輸出格式

## 第二步：整合到 iOS 專案 (Swift)

### 添加模型到 Xcode

1. 將生成的 `EmotionLSTM.mlpackage` 檔案拖放到 Xcode 專案中
2. 確保在彈出的對話框中勾選：
   - ✅ "Copy items if needed"
   - ✅ 選擇正確的 Target（通常是 "App"）
3. 驗證模型已添加到 "Copy Bundle Resources" 中：
   - 選擇專案 > Target > Build Phases > Copy Bundle Resources
   - 確認 `EmotionLSTM.mlpackage` 在列表中

### 使用 EmotionAnalysisService

`EmotionAnalysisService.swift` 已經實作完成，包含以下功能：

#### 基本使用

```swift
// 創建服務實例
let emotionService = EmotionAnalysisService()

// 分析文字情緒
let text = "I am so happy today! This is wonderful!"
let emotion = emotionService.analyze(text: text)
print("Detected emotion: \(emotion)") // 輸出: "joy"
```

#### 獲取詳細的置信度分數

```swift
let emotionService = EmotionAnalysisService()

let text = "This is terrible and I feel awful."
let confidences = emotionService.analyzeWithConfidence(text: text)

for (emotion, confidence) in confidences {
    print("\(emotion): \(String(format: "%.2f%%", confidence * 100))")
}
// 輸出範例:
// joy: 5.23%
// sadness: 78.45%
// anger: 12.34%
// fear: 2.98%
// neutral: 1.00%
```

### EmotionAnalysisService 架構

服務包含以下主要組件：

1. **模型載入 (`loadModel`)**
   - 自動從 Bundle 中載入 CoreML 模型
   - 配置使用 Neural Engine 以提升效能

2. **預處理 (`preprocess`)**
   - 將輸入文字分詞 (tokenization)
   - 轉換為詞彙索引
   - 填充或截斷至固定長度 (128)
   - 轉換為 `MLMultiArray` 格式

3. **預測 (`predict`)**
   - 呼叫 CoreML 模型進行推理
   - 返回模型輸出

4. **後處理 (`postprocess`)**
   - 從模型輸出中提取最高機率的情緒
   - 返回人類可讀的情緒標籤

5. **公開 API**
   - `analyze(text:)`: 返回檢測到的情緒字串
   - `analyzeWithConfidence(text:)`: 返回所有情緒的置信度分數

## 情緒標籤

模型支援以下五種情緒：

- `joy` (喜悅)
- `sadness` (悲傷)
- `anger` (憤怒)
- `fear` (恐懼)
- `neutral` (中性)

## 注意事項

### 詞彙表 (Vocabulary)

目前 `EmotionAnalysisService` 使用簡化的詞彙表。在生產環境中，應該：

1. 使用與訓練時相同的詞彙表
2. 將詞彙表儲存為 JSON 或 plist 檔案
3. 在應用程式啟動時載入

範例詞彙表格式 (vocabulary.json)：

```json
{
  "the": 1,
  "a": 2,
  "happy": 3,
  "sad": 4,
  ...
}
```

在 Swift 中載入：

```swift
if let path = Bundle.main.path(forResource: "vocabulary", ofType: "json"),
   let data = try? Data(contentsOf: URL(fileURLWithPath: path)),
   let vocab = try? JSONDecoder().decode([String: Int].self, from: data) {
    self.vocabulary = vocab
}
```

### 效能優化

1. **模型量化**：使用 `coremltools` 將模型量化為 Float16 或 Int8 以減少大小
2. **批次處理**：對多個文字進行批次推理
3. **快取**：對常見輸入進行結果快取

### 測試建議

建議建立單元測試來驗證：

1. 模型載入成功
2. 預處理正確處理各種輸入
3. 情緒檢測結果符合預期

範例測試：

```swift
func testEmotionAnalysis() {
    let service = EmotionAnalysisService()
    
    let happyText = "I am so happy and excited!"
    let result = service.analyze(text: happyText)
    XCTAssertEqual(result, "joy")
    
    let sadText = "I feel terrible and depressed."
    let result2 = service.analyze(text: sadText)
    XCTAssertEqual(result2, "sadness")
}
```

## 整合到 App Workflow

在您的 iOS 應用程式中整合情緒分析：

```swift
import UIKit

class TextAnalysisViewController: UIViewController {
    
    private let emotionService = EmotionAnalysisService()
    
    @IBOutlet weak var textView: UITextView!
    @IBOutlet weak var emotionLabel: UILabel!
    
    @IBAction func analyzeButtonTapped(_ sender: UIButton) {
        guard let text = textView.text, !text.isEmpty else {
            return
        }
        
        // 執行情緒分析
        let emotion = emotionService.analyze(text: text)
        
        // 更新 UI
        emotionLabel.text = "檢測到的情緒: \(emotion)"
        
        // 取得詳細置信度
        let confidences = emotionService.analyzeWithConfidence(text: text)
        print("Emotion confidences: \(confidences)")
    }
}
```

## 疑難排解

### 模型未找到

**錯誤**：`⚠️ EmotionLSTM model not found in bundle`

**解決方案**：
1. 確認 .mlpackage 檔案已添加到專案
2. 檢查 Build Phases > Copy Bundle Resources
3. 清理專案 (Product > Clean Build Folder)
4. 重新編譯

### 預測失敗

**錯誤**：`❌ Prediction failed`

**可能原因**：
1. 輸入格式不正確
2. 模型與程式碼不匹配
3. 記憶體不足

**解決方案**：
1. 檢查輸入維度與模型期望是否一致
2. 查看詳細錯誤訊息
3. 在實體裝置上測試

### 轉換錯誤

**錯誤**：轉換腳本執行失敗

**解決方案**：
1. 確認已安裝對應的深度學習框架
2. 檢查模型檔案路徑
3. 確認模型格式正確
4. 更新 `coremltools` 到最新版本：`pip install --upgrade coremltools`

## 參考資源

- [Core ML 官方文檔](https://developer.apple.com/documentation/coreml)
- [coremltools 文檔](https://coremltools.readme.io/)
- [Apple Machine Learning](https://developer.apple.com/machine-learning/)

## 授權

本整合遵循 AI-Reader 專案的授權條款。
