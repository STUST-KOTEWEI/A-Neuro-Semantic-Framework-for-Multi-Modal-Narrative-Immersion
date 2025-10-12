# CoreML 情緒分析整合文件

本文件說明如何在 AI-Reader 專案中整合 CoreML 情緒分析功能。

## 概述

此整合包含兩個主要部分：

1. **Python 模型轉換工具**: 將 PyTorch 或 TensorFlow/Keras 模型轉換為 CoreML 格式
2. **Swift 情緒分析服務**: 在 iOS 應用中載入並使用 CoreML 模型進行即時情緒分析

## 架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                    訓練環境 (Python)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PyTorch/TensorFlow Model                                   │
│         ↓                                                   │
│  convert_emotion_model.py (轉換工具)                         │
│         ↓                                                   │
│  EmotionLSTM.mlpackage (CoreML 模型)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓ (拖放到 Xcode)
┌─────────────────────────────────────────────────────────────┐
│                     iOS 應用 (Swift)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  EmotionAnalysisService                                     │
│         ↓                                                   │
│  1. 載入 CoreML 模型                                          │
│  2. 預處理文字 (tokenization)                                 │
│  3. 模型推理                                                  │
│  4. 後處理輸出 (emotion labels)                               │
│         ↓                                                   │
│  返回情緒字串 (e.g., "happy", "sad")                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 檔案結構

```
AI-Reader/
├── scripts/                                    # Python 轉換工具
│   ├── README.md                              # 轉換工具說明
│   ├── convert_emotion_model.py               # 主要轉換腳本
│   ├── example_usage.md                       # 詳細使用範例
│   └── requirements-model-conversion.txt      # Python 依賴
│
├── web/frontend/ios/App/                      # iOS 應用
│   ├── App/
│   │   ├── EmotionAnalysisService.swift       # 情緒分析服務
│   │   ├── AppDelegate.swift
│   │   └── [EmotionLSTM.mlpackage]            # 模型檔案 (使用者需自行加入)
│   └── README.md                              # iOS 整合說明
│
└── docs/
    └── EMOTION_ANALYSIS_INTEGRATION.md        # 本文件
```

## 快速開始

### 步驟 1: 準備環境

```bash
# 安裝 Python 依賴
cd scripts
pip install -r requirements-model-conversion.txt

# 如果需要轉換 TensorFlow/Keras 模型
pip install tensorflow

# 如果需要轉換 PyTorch 模型
pip install torch
```

### 步驟 2: 轉換模型

```bash
# 從 Keras 模型轉換
python convert_emotion_model.py \
    --framework keras \
    --input path/to/emotion_model.h5 \
    --output EmotionLSTM.mlpackage \
    --labels happy sad angry neutral surprise fear

# 從 PyTorch 模型轉換
python convert_emotion_model.py \
    --framework pytorch \
    --input path/to/emotion_model.pth \
    --output EmotionLSTM.mlpackage \
    --input-shape 1 128 \
    --labels happy sad angry neutral surprise fear
```

### 步驟 3: 整合到 iOS

1. 在 Xcode 中開啟 `web/frontend/ios/App/App.xcodeproj`
2. 將生成的 `EmotionLSTM.mlpackage` 拖放到專案中
3. 確認 Target Membership 包含 "App"
4. 使用 `EmotionAnalysisService` 進行情緒分析

```swift
let emotionService = EmotionAnalysisService()
if let emotion = emotionService.analyze(text: "I'm so happy!") {
    print("偵測到情緒: \(emotion)")
}
```

## 詳細說明

### Python 模型轉換

#### 支援的框架
- TensorFlow/Keras (`.h5` 格式)
- PyTorch (`.pth` 或 `.pt` 格式)

#### 轉換參數

| 參數 | 說明 | 必填 | 預設值 |
|------|------|------|--------|
| `--framework` | 模型框架 (keras/pytorch) | ✅ | - |
| `--input` | 輸入模型檔案路徑 | ✅ | - |
| `--output` | 輸出 CoreML 檔案路徑 | ❌ | EmotionLSTM.mlpackage |
| `--labels` | 情緒類別標籤 | ❌ | - |
| `--input-shape` | PyTorch 模型輸入形狀 | ❌ | 1 128 |

#### 模型要求

**輸入規格**:
- 形狀: `[batch_size, sequence_length]`
- 資料類型: Integer (token IDs)
- 推薦序列長度: 128

**輸出規格**:
- 形狀: `[batch_size, num_classes]`
- 資料類型: Float (class probabilities)
- 輸出層: Softmax 或 logits

### Swift 情緒分析服務

#### EmotionAnalysisService API

**主要方法**:

```swift
func analyze(text: String) -> String?
```

- **輸入**: 要分析的文字字串
- **輸出**: 情緒標籤字串，失敗時返回 `nil`
- **支援的情緒**: `happy`, `sad`, `angry`, `neutral`, `surprise`, `fear`

#### 內部處理流程

1. **預處理 (Preprocessing)**
   ```swift
   private func preprocess(text: String) -> MLMultiArray?
   ```
   - 將文字轉換為 token IDs
   - 填充或截斷到固定長度
   - 轉換為 `MLMultiArray` 格式

2. **分詞 (Tokenization)**
   ```swift
   private func tokenize(text: String) -> [Int]
   ```
   - 目前使用簡化的 hash-based 分詞
   - **重要**: 實際應用需使用與訓練時相同的分詞器

3. **預測 (Prediction)**
   ```swift
   private func predict(inputArray: MLMultiArray) -> MLMultiArray?
   ```
   - 使用 CoreML 模型進行推理
   - 返回原始預測結果

4. **後處理 (Postprocessing)**
   ```swift
   private func postprocess(prediction: MLMultiArray) -> String
   ```
   - 找出機率最高的類別
   - 轉換為可讀的情緒標籤
   - 輸出信心度資訊

## 自訂配置

### 修改支援的情緒類別

在 `EmotionAnalysisService.swift` 中:

```swift
private let emotionLabels: [String] = ["custom1", "custom2", ...]
```

**注意**: 標籤順序必須與模型訓練時一致。

### 調整序列長度

```swift
private let maxSequenceLength: Int = 256  // 修改為你的需求
```

### 更換分詞器

目前的分詞器是簡化版本。在生產環境中建議：

1. 在訓練時保存詞彙表 (vocabulary)
2. 將詞彙表匯出為 JSON
3. 在 iOS 專案中載入詞彙表
4. 實作相同的分詞邏輯

範例詞彙表結構：

```json
{
    "word_to_id": {
        "happy": 1,
        "sad": 2,
        "the": 3,
        ...
    },
    "id_to_word": {
        "1": "happy",
        "2": "sad",
        ...
    },
    "max_length": 128,
    "padding_token": 0,
    "unknown_token": 1
}
```

## 效能最佳化

### 1. 運算單元選擇

```swift
let config = MLModelConfiguration()

// 選項 1: 僅使用 CPU
config.computeUnits = .cpuOnly

// 選項 2: CPU + GPU
config.computeUnits = .cpuAndGPU

// 選項 3: 所有單元 (推薦)
config.computeUnits = .all  // CPU + GPU + Neural Engine
```

### 2. 模型量化

在轉換時使用較低精度以減小模型大小：

```python
mlmodel = ct.convert(
    model,
    inputs=[...],
    convert_to="mlprogram",
    compute_precision=ct.precision.FLOAT16  # 或 FLOAT32
)
```

### 3. 批次處理

如需處理多個文字，可擴展服務：

```swift
func analyzeBatch(texts: [String]) -> [String?] {
    return texts.map { analyze(text: $0) }
}
```

## 測試建議

### 單元測試範例

```swift
import XCTest

class EmotionAnalysisServiceTests: XCTestCase {
    
    var service: EmotionAnalysisService!
    
    override func setUp() {
        super.setUp()
        service = EmotionAnalysisService()
    }
    
    func testHappyEmotion() {
        let result = service.analyze(text: "I am so happy today!")
        XCTAssertEqual(result, "happy")
    }
    
    func testSadEmotion() {
        let result = service.analyze(text: "I feel terrible and sad")
        XCTAssertEqual(result, "sad")
    }
    
    func testAngryEmotion() {
        let result = service.analyze(text: "This makes me so angry!")
        XCTAssertEqual(result, "angry")
    }
    
    func testEmptyString() {
        let result = service.analyze(text: "")
        XCTAssertNotNil(result)
    }
}
```

### 效能測試

```swift
func testPerformance() {
    measure {
        _ = service.analyze(text: "This is a test sentence.")
    }
}
```

## 疑難排解

### 問題 1: 模型無法載入

**症狀**:
```
⚠️ 警告: 無法找到 EmotionLSTM 模型檔案
```

**解決方案**:
1. 確認 `.mlpackage` 已加入專案
2. 檢查 Target Membership
3. 清理並重建專案 (Cmd+Shift+K)
4. 檢查 Build Phases -> Copy Bundle Resources

### 問題 2: 轉換失敗

**症狀**:
```
錯誤: 轉換失敗
```

**可能原因**:
- 模型架構不支援
- 輸入形狀不正確
- 缺少必要的依賴套件

**解決方案**:
1. 檢查模型架構是否被 CoreML 支援
2. 驗證輸入輸出形狀
3. 查看詳細錯誤訊息
4. 參考 coremltools 文件

### 問題 3: 預測結果不準確

**可能原因**:
- 分詞方式不同
- 預處理邏輯不一致
- 標籤順序錯誤

**解決方案**:
1. 確保使用相同的分詞器
2. 驗證預處理步驟
3. 檢查標籤順序是否一致
4. 在 Python 和 Swift 中測試相同的輸入

### 問題 4: 效能問題

**症狀**: 推理時間過長

**解決方案**:
1. 使用 `.all` 計算單元
2. 考慮模型量化
3. 減少序列長度
4. 使用較小的模型架構

## 進階主題

### 1. 支援多語言

```swift
class MultilingualEmotionService {
    private var models: [String: EmotionAnalysisService] = [:]
    
    func analyze(text: String, language: String) -> String? {
        guard let service = models[language] else {
            return nil
        }
        return service.analyze(text: text)
    }
}
```

### 2. 即時串流分析

```swift
class StreamingEmotionAnalyzer {
    func analyzeStream(_ textStream: AsyncStream<String>) async {
        for await text in textStream {
            if let emotion = service.analyze(text: text) {
                await handleEmotion(emotion)
            }
        }
    }
}
```

### 3. 與後端整合

```swift
class HybridEmotionService {
    func analyze(text: String, useLocalModel: Bool = true) async -> String? {
        if useLocalModel {
            return localService.analyze(text: text)
        } else {
            return await remoteAPI.analyzeEmotion(text: text)
        }
    }
}
```

## 最佳實踐

1. **模型版本管理**
   - 在模型檔案名稱中包含版本號
   - 記錄模型訓練日期和參數
   - 使用 Git LFS 管理大型模型檔案

2. **錯誤處理**
   - 總是檢查返回值
   - 提供適當的錯誤訊息
   - 實作降級機制

3. **使用者體驗**
   - 顯示處理進度
   - 提供視覺化情緒回饋
   - 快取常用結果

4. **安全性**
   - 不要在模型中儲存敏感資料
   - 驗證使用者輸入
   - 限制輸入長度

## 相關資源

### 官方文件
- [CoreML 文件](https://developer.apple.com/documentation/coreml)
- [coremltools 指南](https://coremltools.readme.io/)
- [MLModel 規格](https://apple.github.io/coremltools/mlmodel/index.html)

### 教學資源
- [CoreML 最佳實踐](https://developer.apple.com/videos/play/wwdc2023/10049/)
- [優化 CoreML 模型](https://developer.apple.com/videos/play/wwdc2022/10027/)

### 情緒分析資源
- [Hugging Face 情緒分析模型](https://huggingface.co/models?pipeline_tag=text-classification&sort=downloads&search=emotion)
- [情緒分析資料集](https://paperswithcode.com/task/emotion-recognition-in-conversation)

## 授權

本整合遵循 AI-Reader 專案的授權條款。

## 貢獻

歡迎提交問題和 Pull Request 來改進此整合。

## 更新日誌

### v1.0.0 (2025-10-12)
- ✅ 初始實作
- ✅ 支援 Keras 和 PyTorch 模型轉換
- ✅ Swift 情緒分析服務
- ✅ 完整的文件和範例
