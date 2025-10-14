"""
CoreML 情緒分析模型轉換腳本

此腳本用於將 PyTorch 或 TensorFlow/Keras 格式的情緒分析模型轉換為 CoreML 的 .mlpackage 格式。
支援 LSTM、GRU 等常見的序列模型架構。

使用範例:
    # 從 TensorFlow/Keras 轉換
    python convert_emotion_model.py --framework keras --input model.h5 --output EmotionLSTM.mlpackage
    
    # 從 PyTorch 轉換
    python convert_emotion_model.py --framework pytorch --input model.pth --output EmotionLSTM.mlpackage
"""

import argparse
import sys
import os

try:
    import coremltools as ct
except ImportError:
    print("錯誤: 無法匯入 coremltools")
    print("請執行: pip install coremltools")
    sys.exit(1)


def load_keras_model(model_path):
    """
    從 .h5 檔案載入 TensorFlow/Keras 模型
    
    Args:
        model_path: .h5 模型檔案的路徑
        
    Returns:
        載入的 Keras 模型
    """
    try:
        import tensorflow as tf
    except ImportError:
        print("錯誤: 無法匯入 tensorflow")
        print("請執行: pip install tensorflow")
        sys.exit(1)
    
    print(f"正在載入 Keras 模型: {model_path}")
    model = tf.keras.models.load_model(model_path)
    print(f"模型架構: {model.summary()}")
    return model


def load_pytorch_model(model_path, model_class=None, input_shape=(1, 128)):
    """
    從 .pth 檔案載入 PyTorch 模型並進行追蹤
    
    Args:
        model_path: .pth 模型檔案的路徑
        model_class: PyTorch 模型類別（如果需要）
        input_shape: 輸入張量的形狀，用於追蹤
        
    Returns:
        追蹤後的 PyTorch 模型
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("錯誤: 無法匯入 torch")
        print("請執行: pip install torch")
        sys.exit(1)
    
    print(f"正在載入 PyTorch 模型: {model_path}")
    
    # 如果提供了模型類別，實例化它
    if model_class is not None:
        model = model_class()
        model.load_state_dict(torch.load(model_path))
    else:
        # 嘗試直接載入完整模型
        model = torch.load(model_path)
    
    model.eval()
    
    # 追蹤模型
    example_input = torch.randn(input_shape)
    traced_model = torch.jit.trace(model, example_input)
    
    print("PyTorch 模型已追蹤完成")
    return traced_model


def convert_keras_to_coreml(keras_model, output_path, class_labels=None):
    """
    將 Keras 模型轉換為 CoreML 格式
    
    Args:
        keras_model: Keras 模型
        output_path: 輸出的 .mlpackage 路徑
        class_labels: 類別標籤列表（可選）
    """
    print("正在將 Keras 模型轉換為 CoreML...")
    
    # 定義輸入
    input_shape = keras_model.input_shape[1:]  # 移除 batch 維度
    
    # 執行轉換
    mlmodel = ct.convert(
        keras_model,
        inputs=[ct.TensorType(name="text_input", shape=(1,) + input_shape)],
        classifier_config=ct.ClassifierConfig(class_labels) if class_labels else None,
        convert_to="mlprogram"
    )
    
    # 設定模型元資料
    mlmodel.author = "AI-Reader Team"
    mlmodel.license = "MIT"
    mlmodel.short_description = "情緒分析 LSTM 模型 - 從 Keras 轉換"
    mlmodel.version = "1.0"
    
    # 儲存模型
    mlmodel.save(output_path)
    print(f"✓ 模型已成功儲存至: {output_path}")


def convert_pytorch_to_coreml(traced_model, output_path, input_shape=(1, 128), class_labels=None):
    """
    將 PyTorch 模型轉換為 CoreML 格式
    
    Args:
        traced_model: 已追蹤的 PyTorch 模型
        output_path: 輸出的 .mlpackage 路徑
        input_shape: 輸入張量的形狀
        class_labels: 類別標籤列表（可選）
    """
    print("正在將 PyTorch 模型轉換為 CoreML...")
    
    try:
        import torch
    except ImportError:
        print("錯誤: 無法匯入 torch")
        sys.exit(1)
    
    # 執行轉換
    mlmodel = ct.convert(
        traced_model,
        inputs=[ct.TensorType(name="text_input", shape=input_shape)],
        classifier_config=ct.ClassifierConfig(class_labels) if class_labels else None,
        convert_to="mlprogram"
    )
    
    # 設定模型元資料
    mlmodel.author = "AI-Reader Team"
    mlmodel.license = "MIT"
    mlmodel.short_description = "情緒分析 LSTM 模型 - 從 PyTorch 轉換"
    mlmodel.version = "1.0"
    
    # 儲存模型
    mlmodel.save(output_path)
    print(f"✓ 模型已成功儲存至: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="將情緒分析模型轉換為 CoreML 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # 從 Keras 轉換
  python convert_emotion_model.py --framework keras --input emotion_model.h5 --output EmotionLSTM.mlpackage
  
  # 從 PyTorch 轉換
  python convert_emotion_model.py --framework pytorch --input emotion_model.pth --output EmotionLSTM.mlpackage
  
  # 指定類別標籤
  python convert_emotion_model.py --framework keras --input model.h5 --output EmotionLSTM.mlpackage \\
      --labels happy sad angry neutral
        """
    )
    
    parser.add_argument(
        "--framework",
        type=str,
        required=True,
        choices=["keras", "pytorch"],
        help="源模型框架 (keras 或 pytorch)"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="輸入模型檔案路徑 (.h5 for Keras, .pth for PyTorch)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="EmotionLSTM.mlpackage",
        help="輸出 CoreML 模型路徑 (預設: EmotionLSTM.mlpackage)"
    )
    
    parser.add_argument(
        "--labels",
        type=str,
        nargs="+",
        help="情緒類別標籤 (例如: happy sad angry neutral)"
    )
    
    parser.add_argument(
        "--input-shape",
        type=int,
        nargs="+",
        default=[1, 128],
        help="PyTorch 模型的輸入形狀 (預設: 1 128)"
    )
    
    args = parser.parse_args()
    
    # 檢查輸入檔案是否存在
    if not os.path.exists(args.input):
        print(f"錯誤: 輸入檔案不存在: {args.input}")
        sys.exit(1)
    
    print("=" * 60)
    print("CoreML 情緒分析模型轉換工具")
    print("=" * 60)
    print(f"框架: {args.framework}")
    print(f"輸入: {args.input}")
    print(f"輸出: {args.output}")
    if args.labels:
        print(f"標籤: {args.labels}")
    print("=" * 60)
    
    try:
        if args.framework == "keras":
            # Keras 轉換流程
            model = load_keras_model(args.input)
            convert_keras_to_coreml(model, args.output, args.labels)
            
        elif args.framework == "pytorch":
            # PyTorch 轉換流程
            input_shape = tuple(args.input_shape)
            traced_model = load_pytorch_model(args.input, input_shape=input_shape)
            convert_pytorch_to_coreml(traced_model, args.output, input_shape, args.labels)
        
        print("\n" + "=" * 60)
        print("✓ 轉換完成!")
        print("=" * 60)
        print(f"\n下一步:")
        print(f"1. 將 {args.output} 加入到 Xcode 專案中")
        print(f"2. 確認模型在 Target Membership 中被勾選")
        print(f"3. 在 Swift 程式碼中使用 EmotionAnalysisService 載入模型")
        
    except Exception as e:
        print(f"\n錯誤: 轉換失敗")
        print(f"詳細資訊: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
