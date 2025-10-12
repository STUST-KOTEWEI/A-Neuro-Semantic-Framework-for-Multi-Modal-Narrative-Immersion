# CoreML 模型轉換使用範例

本文件展示如何使用 `convert_emotion_model.py` 進行模型轉換。

## 前置準備

### 1. 安裝依賴套件

```bash
# 安裝基本轉換工具
pip install -r requirements-model-conversion.txt

# 如果要轉換 TensorFlow/Keras 模型
pip install tensorflow

# 如果要轉換 PyTorch 模型  
pip install torch
```

## 轉換流程

### 範例 1: 從 Keras/TensorFlow 模型轉換

假設你有一個訓練好的 Keras 情緒分析模型 `emotion_model.h5`：

```python
# train_keras_model.py (訓練模型的範例程式碼)
import tensorflow as tf
from tensorflow import keras

# 建立簡單的 LSTM 模型
model = keras.Sequential([
    keras.layers.Embedding(input_dim=10000, output_dim=128, input_length=128),
    keras.layers.LSTM(64),
    keras.layers.Dense(6, activation='softmax')  # 6 種情緒類別
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 訓練模型 (假設你已經有訓練資料)
# model.fit(X_train, y_train, epochs=10, batch_size=32)

# 儲存模型
model.save('emotion_model.h5')
```

轉換為 CoreML：

```bash
python convert_emotion_model.py \
    --framework keras \
    --input emotion_model.h5 \
    --output EmotionLSTM.mlpackage \
    --labels happy sad angry neutral surprise fear
```

### 範例 2: 從 PyTorch 模型轉換

假設你有一個訓練好的 PyTorch 情緒分析模型：

```python
# train_pytorch_model.py (訓練模型的範例程式碼)
import torch
import torch.nn as nn

class EmotionLSTM(nn.Module):
    def __init__(self, vocab_size=10000, embedding_dim=128, hidden_dim=64, num_classes=6):
        super(EmotionLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x):
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        output = self.fc(lstm_out[:, -1, :])
        return output

# 建立並訓練模型
model = EmotionLSTM()
# optimizer = torch.optim.Adam(model.parameters())
# ... 訓練過程 ...

# 儲存模型
torch.save(model, 'emotion_model.pth')
# 或只儲存參數: torch.save(model.state_dict(), 'emotion_model.pth')
```

轉換為 CoreML：

```bash
python convert_emotion_model.py \
    --framework pytorch \
    --input emotion_model.pth \
    --output EmotionLSTM.mlpackage \
    --input-shape 1 128 \
    --labels happy sad angry neutral surprise fear
```

## 轉換後的步驟

### 1. 將模型加入 Xcode 專案

1. 在 Finder 中找到生成的 `EmotionLSTM.mlpackage`
2. 開啟 Xcode 專案: `web/frontend/ios/App/App.xcodeproj`
3. 將 `EmotionLSTM.mlpackage` 拖放到專案導航器中的 `App` 群組
4. 在彈出的對話框中:
   - ✅ 勾選 "Copy items if needed"
   - ✅ 勾選 "App" target
   - 點擊 "Finish"

### 2. 在 Swift 中使用

```swift
// 在你的 ViewController 或其他需要的地方
import UIKit

class TextAnalysisViewController: UIViewController {
    
    // 建立情緒分析服務實例
    let emotionService = EmotionAnalysisService()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 測試情緒分析
        testEmotionAnalysis()
    }
    
    func testEmotionAnalysis() {
        let testTexts = [
            "I am so happy today!",
            "I feel terrible and sad",
            "This makes me so angry!",
            "Just a normal day",
            "Wow, what a surprise!",
            "I'm scared and worried"
        ]
        
        for text in testTexts {
            if let emotion = emotionService.analyze(text: text) {
                print("文字: \(text)")
                print("情緒: \(emotion)")
                print("---")
            }
        }
    }
    
    // 在實際應用中使用
    @IBAction func analyzeButtonTapped(_ sender: UIButton) {
        guard let inputText = textView.text, !inputText.isEmpty else {
            return
        }
        
        if let emotion = emotionService.analyze(text: inputText) {
            // 根據偵測到的情緒更新 UI
            updateUIForEmotion(emotion)
        }
    }
    
    func updateUIForEmotion(_ emotion: String) {
        switch emotion {
        case "happy":
            view.backgroundColor = .systemYellow
            emotionLabel.text = "😊"
        case "sad":
            view.backgroundColor = .systemBlue
            emotionLabel.text = "😢"
        case "angry":
            view.backgroundColor = .systemRed
            emotionLabel.text = "😠"
        case "neutral":
            view.backgroundColor = .systemGray
            emotionLabel.text = "😐"
        case "surprise":
            view.backgroundColor = .systemOrange
            emotionLabel.text = "😮"
        case "fear":
            view.backgroundColor = .systemPurple
            emotionLabel.text = "😨"
        default:
            view.backgroundColor = .white
            emotionLabel.text = "❓"
        }
    }
}
```

## 注意事項

### 模型訓練建議

1. **資料集**: 使用高品質的情緒標註資料集
2. **序列長度**: 確保訓練時的序列長度與 iOS 端設定一致（預設 128）
3. **詞彙表**: 保存訓練時使用的詞彙表，以便在 iOS 端實作相同的分詞邏輯
4. **標籤順序**: 記錄類別標籤的順序，確保與 iOS 端的 `emotionLabels` 陣列一致

### 分詞器同步

目前 `EmotionAnalysisService.swift` 中使用的是簡化的分詞邏輯。在生產環境中，你需要：

1. 在訓練時保存詞彙表（vocabulary）
2. 將詞彙表匯出為 JSON 或其他格式
3. 在 iOS 專案中載入相同的詞彙表
4. 實作與訓練時相同的分詞和編碼邏輯

範例詞彙表格式：

```json
{
    "word_to_id": {
        "happy": 1,
        "sad": 2,
        "angry": 3,
        "the": 4,
        "is": 5,
        ...
    },
    "max_length": 128,
    "padding_value": 0
}
```

### 效能考量

- **模型大小**: 建議模型檔案小於 10MB，以避免影響 App 下載大小
- **推理速度**: 在實際裝置上測試，確保推理時間小於 100ms
- **記憶體使用**: 監控記憶體使用，特別是在處理長文字時

## 疑難排解

### 問題 1: 轉換時出現形狀不匹配錯誤

```
ValueError: Input shape mismatch
```

**解決方案**: 檢查 `--input-shape` 參數是否與模型訓練時的輸入形狀一致。

### 問題 2: 模型在 iOS 中無法載入

```
Unable to load model
```

**解決方案**: 
1. 確認模型檔案已正確加入專案
2. 檢查 Target Membership
3. 清理並重新建置專案 (Product -> Clean Build Folder)

### 問題 3: 預測結果與 Python 不一致

**可能原因**:
1. 分詞方式不同
2. 輸入預處理邏輯不同
3. 標籤順序不一致

**解決方案**: 確保 iOS 端的預處理邏輯與訓練時完全一致。

## 進階功能

### 量化模型以減小大小

在轉換時可以使用量化來減小模型大小：

```python
# 修改 convert_emotion_model.py 中的轉換函式
mlmodel = ct.convert(
    model,
    inputs=[ct.TensorType(name="text_input", shape=input_shape)],
    convert_to="mlprogram",
    compute_precision=ct.precision.FLOAT16  # 使用 16 位浮點數
)
```

### 支援多語言

如果你的模型支援多語言，可以在 `EmotionAnalysisService` 中加入語言偵測：

```swift
func analyze(text: String, language: String = "en") -> String? {
    // 根據語言使用不同的分詞策略
    let tokens = tokenize(text: text, language: language)
    // ...
}
```

## 相關資源

- [TensorFlow 模型轉換指南](https://coremltools.readme.io/docs/tensorflow-2)
- [PyTorch 模型轉換指南](https://coremltools.readme.io/docs/pytorch-conversion)
- [CoreML 最佳實踐](https://developer.apple.com/documentation/coreml/core_ml_api/integrating_a_core_ml_model_into_your_app)
- [情緒分析資料集](https://huggingface.co/datasets?task_categories=text-classification&task_ids=sentiment-analysis)
