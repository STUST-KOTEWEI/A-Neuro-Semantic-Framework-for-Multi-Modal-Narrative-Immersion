# 🚀 CoreML 情緒分析 - 快速開始指南

> **完成時間：** 約 15 分鐘  
> **難度：** ⭐⭐☆☆☆ (簡單)

## 📋 前置需求

- [ ] Python 3.7+ 已安裝
- [ ] Xcode 13.0+ 已安裝
- [ ] iOS 15.0+ 裝置或模擬器
- [ ] 已訓練好的情緒分析模型 (PyTorch 或 TensorFlow)

## ⚡ 三步驟快速整合

### 步驟 1: 安裝 Python 依賴 (2 分鐘)

```bash
# 進入專案目錄
cd AI-Reader

# 安裝依賴
pip install coremltools

# 根據您的模型類型選擇安裝
pip install torch        # PyTorch 模型
# 或
pip install tensorflow   # TensorFlow 模型
```

### 步驟 2: 轉換模型 (3 分鐘)

```bash
# PyTorch 模型轉換
python convert_emotion_model.py \
    --input your_model.pt \
    --format pytorch \
    --output EmotionLSTM.mlpackage

# TensorFlow/Keras 模型轉換
python convert_emotion_model.py \
    --input your_model.h5 \
    --format keras \
    --output EmotionLSTM.mlpackage
```

**預期輸出：**
```
Loading model from your_model.pt...
Model loaded successfully...
Converting to CoreML...
Saving CoreML model to EmotionLSTM.mlpackage...
✅ Conversion completed successfully!
```

### 步驟 3: 整合到 iOS (10 分鐘)

#### 3.1 添加檔案到 Xcode (2 分鐘)

1. 打開 Xcode 專案
2. 將 `EmotionLSTM.mlpackage` 拖入專案
3. 將 `EmotionAnalysisService.swift` 拖入專案
4. 確保勾選目標 Target

#### 3.2 使用服務 (8 分鐘)

在任何 ViewController 中：

```swift
import UIKit

class MyViewController: UIViewController {
    // 創建服務實例
    private let emotionService = EmotionAnalysisService()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 測試情緒分析
        testEmotionAnalysis()
    }
    
    func testEmotionAnalysis() {
        // 分析文字
        let text = "I am so happy today! This is wonderful!"
        let emotion = emotionService.analyze(text: text)
        
        print("檢測到的情緒: \(emotion)")
        // 輸出: 檢測到的情緒: joy
        
        // 獲取詳細置信度
        let confidences = emotionService.analyzeWithConfidence(text: text)
        for (emotion, confidence) in confidences {
            print("\(emotion): \(String(format: "%.2f%%", confidence * 100))")
        }
    }
}
```

## ✅ 驗證安裝

執行測試以驗證一切正常：

```bash
# 測試 Python 轉換工具
python test_emotion_conversion.py
```

**預期輸出：**
```
============================================================
Emotion Model Conversion Test
============================================================
✅ PyTorch is installed
✅ coremltools is installed

📦 Creating dummy PyTorch emotion model...
✅ Dummy model saved to dummy_emotion_model.pt

🔄 Testing model conversion...
✅ Conversion successful!
✅ TestEmotionLSTM.mlpackage file created

============================================================
✅ All tests passed!
============================================================
```

## 📚 完整文檔

如需更詳細的資訊，請參考：

1. **[README_EMOTION_MODEL.md](README_EMOTION_MODEL.md)** - 完整功能說明
2. **[EMOTION_ANALYSIS_INTEGRATION.md](EMOTION_ANALYSIS_INTEGRATION.md)** - 詳細整合步驟
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系統架構圖
4. **[examples/emotion_analysis_example.swift](examples/emotion_analysis_example.swift)** - UIKit & SwiftUI 範例

## 🎯 支援的情緒

| 情緒 | 英文 | Emoji |
|------|------|-------|
| 喜悅 | joy | 😊 |
| 悲傷 | sadness | 😢 |
| 憤怒 | anger | 😠 |
| 恐懼 | fear | 😨 |
| 中性 | neutral | 😐 |

## 💡 使用範例

### 簡單使用

```swift
let service = EmotionAnalysisService()
let emotion = service.analyze(text: "I love this!")
print(emotion)  // "joy"
```

### 獲取置信度

```swift
let service = EmotionAnalysisService()
let confidences = service.analyzeWithConfidence(text: "I love this!")

// 輸出所有情緒的置信度
for (emotion, score) in confidences.sorted(by: { $0.value > $1.value }) {
    print("\(emotion): \(String(format: "%.1f%%", score * 100))")
}
```

### 在 SwiftUI 中使用

```swift
import SwiftUI

struct ContentView: View {
    @State private var text = ""
    @State private var emotion = ""
    private let service = EmotionAnalysisService()
    
    var body: some View {
        VStack {
            TextField("輸入文字", text: $text)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding()
            
            Button("分析情緒") {
                emotion = service.analyze(text: text)
            }
            
            Text("檢測到的情緒: \(emotion)")
                .font(.headline)
        }
    }
}
```

## 🔧 常見問題

### Q: 模型檔案找不到

**A:** 確認以下步驟：
1. 檔案已拖入 Xcode 專案
2. 在 Target > Build Phases > Copy Bundle Resources 中可以看到該檔案
3. Clean Build Folder (Cmd+Shift+K) 並重新編譯

### Q: 轉換失敗

**A:** 檢查：
1. `coremltools` 是否已安裝: `pip list | grep coremltools`
2. 模型檔案路徑是否正確
3. 模型格式是否與 `--format` 參數匹配

### Q: 預測結果不準確

**A:** 可能原因：
1. 詞彙表不匹配：請使用訓練時的詞彙表
2. 輸入序列長度不匹配：調整 `maxSequenceLength`
3. 模型本身的準確度問題：檢查訓練效果

## 🚀 下一步

完成基本整合後，您可以：

1. **自訂詞彙表**：使用與訓練相同的詞彙表以提高準確度
2. **添加單元測試**：確保服務穩定運行
3. **優化效能**：使用模型量化減少檔案大小
4. **整合到 UI**：創建美觀的情緒顯示介面
5. **批次處理**：同時分析多段文字

## 📞 獲取幫助

如遇到問題：

1. 查看 [EMOTION_ANALYSIS_INTEGRATION.md](EMOTION_ANALYSIS_INTEGRATION.md) 中的疑難排解章節
2. 檢查 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) 了解完整實作細節
3. 參考 [examples/](examples/) 目錄中的範例程式碼

## 🎉 完成！

恭喜！您已成功整合 CoreML 情緒分析功能。現在您的應用程式可以：

- ✅ 即時分析文字情緒
- ✅ 獲取詳細的置信度分數
- ✅ 在裝置上離線運行
- ✅ 利用 Neural Engine 加速

開始使用並享受情緒分析的強大功能吧！🚀

---

**版本：** 1.0.0  
**最後更新：** 2025-10-12  
**專案：** AI-Reader CoreML Integration
