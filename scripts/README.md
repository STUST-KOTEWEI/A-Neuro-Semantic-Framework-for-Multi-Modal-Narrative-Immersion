# 模型轉換腳本

此目錄包含將機器學習模型轉換為 CoreML 格式的工具。

## convert_emotion_model.py

將情緒分析模型（PyTorch 或 TensorFlow/Keras 格式）轉換為 CoreML 的 `.mlpackage` 格式。

### 安裝依賴

```bash
pip install -r requirements-model-conversion.txt
```

如果需要轉換 TensorFlow/Keras 模型，請另外安裝:
```bash
pip install tensorflow
```

如果需要轉換 PyTorch 模型，請另外安裝:
```bash
pip install torch
```

### 使用方法

#### 從 Keras 模型轉換

```bash
python convert_emotion_model.py \
    --framework keras \
    --input path/to/emotion_model.h5 \
    --output EmotionLSTM.mlpackage \
    --labels happy sad angry neutral
```

#### 從 PyTorch 模型轉換

```bash
python convert_emotion_model.py \
    --framework pytorch \
    --input path/to/emotion_model.pth \
    --output EmotionLSTM.mlpackage \
    --input-shape 1 128 \
    --labels happy sad angry neutral
```

### 參數說明

- `--framework`: 源模型框架，可選 `keras` 或 `pytorch`
- `--input`: 輸入模型檔案路徑 (`.h5` for Keras, `.pth` for PyTorch)
- `--output`: 輸出 CoreML 模型路徑（預設: `EmotionLSTM.mlpackage`）
- `--labels`: 情緒類別標籤（可選）
- `--input-shape`: PyTorch 模型的輸入形狀（預設: `1 128`）

### 轉換後的步驟

1. 將生成的 `.mlpackage` 檔案拖放到 Xcode 專案中
2. 確認模型在 Target Membership 中被勾選
3. 在 Swift 程式碼中使用 `EmotionAnalysisService` 載入並使用模型

## 注意事項

- 轉換前請確保已安裝對應的機器學習框架（TensorFlow 或 PyTorch）
- 模型的輸入輸出格式需要與 iOS 端的預處理/後處理邏輯相匹配
- 建議在轉換前先在 Python 環境中測試模型的正確性
