# 快速開始：情緒分析整合

這是一個快速指南，幫助你在 5 分鐘內開始使用 AI-Reader 的情緒分析功能。

## 📋 前置需求

- Python 3.8+ (用於模型轉換)
- Xcode 14+ (用於 iOS 開發)
- 一個訓練好的情緒分析模型 (PyTorch 或 TensorFlow/Keras)

## 🚀 三步驟快速開始

### 步驟 1: 轉換模型 (Python)

```bash
# 1. 安裝依賴
cd scripts
pip install -r requirements-model-conversion.txt
pip install tensorflow  # 或 torch，依你的模型而定

# 2. 轉換模型
python convert_emotion_model.py \
    --framework keras \
    --input /path/to/your/model.h5 \
    --output EmotionLSTM.mlpackage \
    --labels happy sad angry neutral surprise fear
```

### 步驟 2: 加入模型到 Xcode (iOS)

1. 開啟 `web/frontend/ios/App/App.xcodeproj`
2. 拖放 `EmotionLSTM.mlpackage` 到專案中
3. 確認「Target Membership」勾選了「App」

### 步驟 3: 使用服務 (Swift)

```swift
import UIKit

class MyViewController: UIViewController {
    
    let emotionService = EmotionAnalysisService()
    
    func analyzeUserInput() {
        let text = textField.text ?? ""
        
        if let emotion = emotionService.analyze(text: text) {
            print("偵測到情緒: \(emotion)")
            // 根據情緒更新 UI
            updateUI(for: emotion)
        }
    }
    
    func updateUI(for emotion: String) {
        switch emotion {
        case "happy":
            view.backgroundColor = .systemYellow
            statusLabel.text = "😊"
        case "sad":
            view.backgroundColor = .systemBlue
            statusLabel.text = "😢"
        default:
            view.backgroundColor = .white
            statusLabel.text = "😐"
        }
    }
}
```

## ✅ 完成！

現在你的 App 已經具備即時情緒分析功能了！

## 📚 下一步

- **詳細文件**: [完整整合指南](docs/EMOTION_ANALYSIS_INTEGRATION.md)
- **進階範例**: [使用範例集合](scripts/example_usage.md)
- **iOS 指南**: [iOS 整合說明](web/frontend/ios/App/README.md)
- **實作總結**: [實作細節](IMPLEMENTATION_SUMMARY.md)

## 🔧 疑難排解

### 問題: 找不到模型
**解決方案**: 確認模型檔案已加入專案，且檔名為 `EmotionLSTM`

### 問題: 轉換失敗
**解決方案**: 檢查模型格式是否正確，參考[詳細文件](docs/EMOTION_ANALYSIS_INTEGRATION.md#疑難排解)

### 問題: 預測不準確
**解決方案**: 確保使用與訓練時相同的分詞器和詞彙表

## 💡 提示

- 在實際裝置上測試效能
- 使用 `.all` 運算單元以獲得最佳效能
- 考慮對模型進行量化以減小大小
- 實作快取機制以提升速度

## 🤝 需要幫助？

- 查看 [完整文件](docs/EMOTION_ANALYSIS_INTEGRATION.md)
- 提交 [GitHub Issue](https://github.com/STUST-KOTEWEI/AI-Reader/issues)
- 查閱 [實作總結](IMPLEMENTATION_SUMMARY.md)

---

**快速開始版本**: v1.0  
**更新日期**: 2025-10-12
