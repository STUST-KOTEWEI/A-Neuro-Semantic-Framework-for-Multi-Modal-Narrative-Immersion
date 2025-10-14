"""
CoreML Model Conversion Script for Emotion Analysis

This script converts a pre-trained emotion analysis model from PyTorch or TensorFlow/Keras
to CoreML .mlpackage format for integration into iOS applications.

Usage:
    python convert_emotion_model.py --input model.h5 --format keras
    python convert_emotion_model.py --input model.pt --format pytorch
"""

import argparse
import sys

try:
    import coremltools as ct
except ImportError:
    print("Error: coremltools is not installed. Please run: pip install coremltools")
    sys.exit(1)


def load_keras_model(model_path):
    """
    Load a Keras/TensorFlow model from .h5 file.
    
    Args:
        model_path: Path to the .h5 model file
        
    Returns:
        Loaded Keras model
    """
    try:
        import tensorflow as tf
        from tensorflow import keras
    except ImportError:
        print("Error: TensorFlow is not installed. Please run: pip install tensorflow")
        sys.exit(1)
    
    print(f"Loading Keras model from {model_path}...")
    model = keras.models.load_model(model_path)
    print(f"Model loaded successfully. Input shape: {model.input_shape}")
    return model


def load_pytorch_model(model_path, input_shape=(1, 128)):
    """
    Load a PyTorch model and trace it for CoreML conversion.
    
    Args:
        model_path: Path to the .pt model file
        input_shape: Expected input shape for tracing
        
    Returns:
        Traced PyTorch model
    """
    try:
        import torch
        import torch.nn as nn
    except ImportError:
        print("Error: PyTorch is not installed. Please run: pip install torch")
        sys.exit(1)
    
    print(f"Loading PyTorch model from {model_path}...")
    model = torch.load(model_path, map_location='cpu')
    model.eval()
    
    # Trace the model for CoreML conversion
    print(f"Tracing model with input shape: {input_shape}")
    example_input = torch.randn(input_shape)
    traced_model = torch.jit.trace(model, example_input)
    print("Model traced successfully.")
    return traced_model, example_input


def convert_keras_to_coreml(model, output_path="EmotionLSTM.mlpackage"):
    """
    Convert a Keras model to CoreML format.
    
    Args:
        model: Keras model to convert
        output_path: Path to save the .mlpackage
    """
    print("\nConverting Keras model to CoreML...")
    
    # Define input
    input_shape = model.input_shape[1:]  # Remove batch dimension
    
    # Convert to CoreML
    coreml_model = ct.convert(
        model,
        inputs=[ct.TensorType(name="text_input", shape=(1,) + input_shape)],
        outputs=[ct.TensorType(name="emotion_output")],
        minimum_deployment_target=ct.target.iOS15,
        convert_to="mlprogram"
    )
    
    # Add metadata
    coreml_model.author = "AI-Reader Team"
    coreml_model.short_description = "Emotion analysis model for text sentiment detection"
    coreml_model.version = "1.0"
    
    # Set input/output descriptions
    coreml_model.input_description["text_input"] = "Preprocessed text input as token IDs"
    coreml_model.output_description["emotion_output"] = "Emotion probabilities (e.g., joy, sadness, anger, fear, neutral)"
    
    # Save the model
    print(f"Saving CoreML model to {output_path}...")
    coreml_model.save(output_path)
    print(f"Model saved successfully!")


def convert_pytorch_to_coreml(traced_model, example_input, output_path="EmotionLSTM.mlpackage"):
    """
    Convert a traced PyTorch model to CoreML format.
    
    Args:
        traced_model: Traced PyTorch model
        example_input: Example input tensor used for tracing
        output_path: Path to save the .mlpackage
    """
    print("\nConverting PyTorch model to CoreML...")
    
    # Convert to CoreML
    coreml_model = ct.convert(
        traced_model,
        inputs=[ct.TensorType(name="text_input", shape=example_input.shape)],
        outputs=[ct.TensorType(name="emotion_output")],
        minimum_deployment_target=ct.target.iOS15,
        convert_to="mlprogram"
    )
    
    # Add metadata
    coreml_model.author = "AI-Reader Team"
    coreml_model.short_description = "Emotion analysis model for text sentiment detection"
    coreml_model.version = "1.0"
    
    # Set input/output descriptions
    coreml_model.input_description["text_input"] = "Preprocessed text input as token IDs"
    coreml_model.output_description["emotion_output"] = "Emotion probabilities (e.g., joy, sadness, anger, fear, neutral)"
    
    # Save the model
    print(f"Saving CoreML model to {output_path}...")
    coreml_model.save(output_path)
    print(f"Model saved successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Convert emotion analysis models to CoreML format"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input model file (.h5 for Keras or .pt for PyTorch)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["keras", "pytorch"],
        required=True,
        help="Model format: 'keras' for TensorFlow/Keras or 'pytorch' for PyTorch"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="EmotionLSTM.mlpackage",
        help="Output path for CoreML model (default: EmotionLSTM.mlpackage)"
    )
    parser.add_argument(
        "--input-shape",
        type=str,
        default="1,128",
        help="Input shape for PyTorch models (comma-separated, default: 1,128)"
    )
    
    args = parser.parse_args()
    
    if args.format == "keras":
        # Load and convert Keras model
        model = load_keras_model(args.input)
        convert_keras_to_coreml(model, args.output)
    
    elif args.format == "pytorch":
        # Parse input shape
        input_shape = tuple(map(int, args.input_shape.split(",")))
        
        # Load and convert PyTorch model
        traced_model, example_input = load_pytorch_model(args.input, input_shape)
        convert_pytorch_to_coreml(traced_model, example_input, args.output)
    
    print("\n✅ Conversion completed successfully!")
    print(f"📦 CoreML model saved to: {args.output}")
    print("\nNext steps:")
    print("1. Add the .mlpackage file to your Xcode project")
    print("2. Ensure the model is added to the target's Copy Bundle Resources")
    print("3. Use EmotionAnalysisService in Swift to load and use the model")


if __name__ == "__main__":
    main()
