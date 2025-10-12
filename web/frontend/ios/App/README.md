# iOS App - 情緒分析整合指南

此目錄包含 AI-Reader 的 iOS 應用程式，整合了 CoreML 情緒分析功能。

## 檔案結構

```
App/
├── App/
│   ├── AppDelegate.swift              # 應用程式委託
│   ├── EmotionAnalysisService.swift   # 情緒分析服務
│   ├── Assets.xcassets/               # 資源檔案
│   ├── Base.lproj/                    # 本地化資源
│   └── Info.plist                     # 應用程式配置
├── App.xcodeproj/                     # Xcode 專案
└── README.md                          # 本文件
```

## 情緒分析整合

### 1. 準備模型檔案

首先，你需要準備一個 CoreML 格式的情緒分析模型：

```bash
# 在專案根目錄的 scripts 目錄中
cd scripts

# 從 Keras 模型轉換（範例）
python convert_emotion_model.py \
    --framework keras \
    --input /path/to/your/emotion_model.h5 \
    --output EmotionLSTM.mlpackage \
    --labels happy sad angry neutral surprise fear

# 或從 PyTorch 模型轉換
python convert_emotion_model.py \
    --framework pytorch \
    --input /path/to/your/emotion_model.pth \
    --output EmotionLSTM.mlpackage \
    --input-shape 1 128 \
    --labels happy sad angry neutral surprise fear
```

### 2. 加入模型到 Xcode 專案

1. 在 Xcode 中開啟 `App.xcodeproj`
2. 將生成的 `EmotionLSTM.mlpackage` 檔案拖放到專案導航器中
3. 在彈出的對話框中：
   - ✅ 勾選 "Copy items if needed"
   - ✅ 確認 Target 選擇了 "App"
   - 點擊 "Finish"
4. 選中加入的 `.mlpackage` 檔案
5. 在右側面板的 "Target Membership" 中確認 "App" 被勾選

### 3. 使用 EmotionAnalysisService

`EmotionAnalysisService` 已經在 `EmotionAnalysisService.swift` 中實作完成。

#### 基本使用方法

```swift
import UIKit

class YourViewController: UIViewController {
    
    let emotionService = EmotionAnalysisService()
    
    func analyzeText() {
        let text = "I am feeling great today!"
        
        if let emotion = emotionService.analyze(text: text) {
            print("偵測到的情緒: \(emotion)")
            // 根據情緒做相應處理
            updateUI(with: emotion)
        } else {
            print("情緒分析失敗")
        }
    }
    
    func updateUI(with emotion: String) {
        // 根據情緒更新使用者介面
        switch emotion {
        case "happy":
            // 顯示開心的視覺效果
            break
        case "sad":
            // 顯示悲傷的視覺效果
            break
        case "angry":
            // 顯示生氣的視覺效果
            break
        default:
            break
        }
    }
}
```

## 架構說明

### EmotionAnalysisService

情緒分析服務的核心類別，提供以下功能：

#### 主要方法

- `analyze(text: String) -> String?`
  - 分析輸入文字的情緒
  - 返回情緒標籤字串（如 "happy", "sad" 等）
  - 失敗時返回 `nil`

#### 內部處理流程

1. **預處理 (preprocess)**
   - 將文字轉換為 token IDs
   - 填充/截斷到固定長度
   - 轉換為 `MLMultiArray` 格式

2. **預測 (predict)**
   - 使用 CoreML 模型進行推理
   - 返回原始預測結果

3. **後處理 (postprocess)**
   - 找出機率最高的類別
   - 轉換為可讀的情緒標籤

## 模型要求

### 輸入格式
- 類型: `MLMultiArray`
- 形狀: `[1, 128]` (批次大小 x 序列長度)
- 資料類型: `Int32`

### 輸出格式
- 類型: `MLMultiArray`
- 形狀: `[1, num_classes]`
- 資料類型: `Double` 或 `Float`

### 支援的情緒標籤
預設支援以下情緒類別：
- `happy` (開心)
- `sad` (悲傷)
- `angry` (生氣)
- `neutral` (中性)
- `surprise` (驚訝)
- `fear` (恐懼)

## 自訂配置

### 修改情緒標籤

在 `EmotionAnalysisService.swift` 中修改 `emotionLabels` 屬性：

```swift
private let emotionLabels: [String] = ["custom1", "custom2", "custom3"]
```

### 調整序列長度

根據你的模型訓練配置修改：

```swift
private let maxSequenceLength: Int = 256  // 預設是 128
```

### 更換分詞器

目前使用的是簡化的分詞邏輯。在生產環境中，建議：

1. 使用與模型訓練時相同的分詞器
2. 儲存詞彙表到專案中
3. 在 `tokenize(text:)` 方法中實作對應的分詞邏輯

## 效能最佳化

### 運算單元選擇

在 `loadModel()` 中可以調整運算單元：

```swift
// 僅使用 CPU
config.computeUnits = .cpuOnly

// 僅使用 GPU
config.computeUnits = .cpuAndGPU

// 使用所有可用單元（推薦）
config.computeUnits = .all
```

### 批次處理

如需處理多個文字，可以修改服務以支援批次輸入：

```swift
func analyzeBatch(texts: [String]) -> [String?] {
    return texts.map { analyze(text: $0) }
}
```

## 疑難排解

### 模型找不到

確認：
1. `.mlpackage` 檔案已正確加入專案
2. Target Membership 已勾選
3. 檔案名稱為 `EmotionLSTM`

### 預測結果不準確

檢查：
1. 模型訓練品質
2. 分詞器是否與訓練時一致
3. 輸入預處理是否正確

### 效能問題

嘗試：
1. 使用較小的模型
2. 調整 `computeUnits` 設定
3. 減少序列長度

## 測試

建議在 Xcode 中建立單元測試：

```swift
import XCTest

class EmotionAnalysisServiceTests: XCTestCase {
    
    let service = EmotionAnalysisService()
    
    func testHappyEmotion() {
        let result = service.analyze(text: "I am so happy!")
        XCTAssertEqual(result, "happy")
    }
    
    func testSadEmotion() {
        let result = service.analyze(text: "I feel terrible")
        XCTAssertEqual(result, "sad")
    }
}
```

## 更多資源

- [CoreML 官方文件](https://developer.apple.com/documentation/coreml)
- [MLModel 配置選項](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [coremltools 文件](https://coremltools.readme.io/)
