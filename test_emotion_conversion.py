"""
Test script for emotion model conversion

This script demonstrates how to create a simple emotion analysis model
and convert it to CoreML format using the convert_emotion_model.py script.

Note: This creates a dummy model for testing purposes only.
"""

import sys
import os

# Test if required packages are available
def check_dependencies():
    """Check if required packages are installed"""
    missing_packages = []
    
    try:
        import torch
        print("✅ PyTorch is installed")
    except ImportError:
        missing_packages.append("torch")
    
    try:
        import coremltools
        print("✅ coremltools is installed")
    except ImportError:
        missing_packages.append("coremltools")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages:")
        print("  pip install " + " ".join(missing_packages))
        return False
    
    return True


def create_dummy_pytorch_model():
    """Create a simple dummy PyTorch model for testing"""
    try:
        import torch
        import torch.nn as nn
        
        print("\n📦 Creating dummy PyTorch emotion model...")
        
        class SimpleLSTM(nn.Module):
            def __init__(self, vocab_size=1000, embedding_dim=64, hidden_dim=128, output_dim=5):
                super(SimpleLSTM, self).__init__()
                self.embedding = nn.Embedding(vocab_size, embedding_dim)
                self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
                self.fc = nn.Linear(hidden_dim, output_dim)
                self.softmax = nn.Softmax(dim=1)
            
            def forward(self, x):
                embedded = self.embedding(x)
                lstm_out, (hidden, _) = self.lstm(embedded)
                output = self.fc(hidden[-1])
                return self.softmax(output)
        
        # Create model
        model = SimpleLSTM()
        model.eval()
        
        # Save model
        torch.save(model, "dummy_emotion_model.pt")
        print("✅ Dummy model saved to dummy_emotion_model.pt")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create dummy model: {e}")
        return False


def test_conversion():
    """Test the conversion process"""
    print("\n🔄 Testing model conversion...")
    
    # Run the conversion script
    import subprocess
    
    try:
        result = subprocess.run([
            "python3", "convert_emotion_model.py",
            "--input", "dummy_emotion_model.pt",
            "--format", "pytorch",
            "--output", "TestEmotionLSTM.mlpackage"
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        print("✅ Conversion successful!")
        
        # Check if the output file was created
        if os.path.exists("TestEmotionLSTM.mlpackage"):
            print("✅ TestEmotionLSTM.mlpackage file created")
            
            # Get file size
            import shutil
            size = os.path.getsize("TestEmotionLSTM.mlpackage") if os.path.isfile("TestEmotionLSTM.mlpackage") else sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk("TestEmotionLSTM.mlpackage")
                for filename in filenames
            )
            print(f"📦 Model package size: {size / 1024:.2f} KB")
            return True
        else:
            print("⚠️  Output file not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Conversion failed: {e}")
        print(f"Output: {e.output}")
        return False
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False


def cleanup():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    files_to_remove = [
        "dummy_emotion_model.pt",
        "TestEmotionLSTM.mlpackage"
    ]
    
    for file in files_to_remove:
        try:
            if os.path.isdir(file):
                import shutil
                shutil.rmtree(file)
                print(f"  Removed directory: {file}")
            elif os.path.isfile(file):
                os.remove(file)
                print(f"  Removed file: {file}")
        except Exception as e:
            print(f"  Could not remove {file}: {e}")


def main():
    """Main test function"""
    print("=" * 60)
    print("Emotion Model Conversion Test")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install required dependencies first")
        return 1
    
    # Create dummy model
    if not create_dummy_pytorch_model():
        print("\n❌ Failed to create test model")
        return 1
    
    # Test conversion
    success = test_conversion()
    
    # Cleanup
    cleanup()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nYou can now use convert_emotion_model.py with your actual")
        print("trained emotion analysis model.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
