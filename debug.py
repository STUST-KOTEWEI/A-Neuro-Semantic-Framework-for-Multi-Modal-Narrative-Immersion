#!/usr/bin/env python3
"""
Debug script to test all components including new AI features
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all imports work correctly"""
    print("Testing imports...")
    
    try:
        from holo.ingestion.text_segmenter import TextSegmenter
        print("✓ TextSegmenter imported successfully")
    except ImportError as e:
        print(f"✗ TextSegmenter import failed: {e}")
    
    try:
        from holo.auditory.elevenlabs_tts import get_tts_engine, ElevenLabsTTS, ElevenLabsTTSFallback
        print("✓ ElevenLabs TTS imported successfully")
    except ImportError as e:
        print(f"✗ ElevenLabs TTS import failed: {e}")
    
    try:
        from holo.sensory.haptics_emulator import HapticsEmulator
        print("✓ HapticsEmulator imported successfully")
    except ImportError as e:
        print(f"✗ HapticsEmulator import failed: {e}")
    
    # Test new AI imports
    try:
        from backend.ai_image_selector import AIImageSelector
        print("✓ AIImageSelector imported successfully")
    except ImportError as e:
        print(f"✗ AIImageSelector import failed: {e}")
    
    try:
        from backend.ai_text_generator import AITextGenerator
        print("✓ AITextGenerator imported successfully")
    except ImportError as e:
        print(f"✗ AITextGenerator import failed: {e}")
    
    try:
        from backend.ai_image_captioner import AIImageCaptioner
        print("✓ AIImageCaptioner imported successfully")
    except ImportError as e:
        print(f"✗ AIImageCaptioner import failed: {e}")

def test_components():
    """Test basic functionality of each component"""
    print("\nTesting component functionality...")
    
    # Test Text Segmenter
    try:
        from holo.ingestion.text_segmenter import TextSegmenter
        segmenter = TextSegmenter()
        result = segmenter.segment_by_sentences("Hello world. This is a test.")
        print(f"✓ TextSegmenter works: {len(result)} segments")
    except Exception as e:
        print(f"✗ TextSegmenter test failed: {e}")
    
    # Test TTS Engine
    try:
        from holo.auditory.elevenlabs_tts import get_tts_engine
        tts = get_tts_engine()
        print(f"✓ TTS Engine initialized: {type(tts).__name__}")
    except Exception as e:
        print(f"✗ TTS Engine test failed: {e}")
    
    # Test Haptics
    try:
        from holo.sensory.haptics_emulator import HapticsEmulator
        haptics = HapticsEmulator()
        pattern = haptics.generate_from_text("test text")
        print(f"✓ HapticsEmulator works: {len(pattern.get('events', []))} events")
    except Exception as e:
        print(f"✗ HapticsEmulator test failed: {e}")
    
    # Test AI Image Selector
    try:
        from backend.ai_image_selector import AIImageSelector
        selector = AIImageSelector()
        stats = selector.get_emotion_statistics()
        print(f"✓ AIImageSelector works: {stats['total_images']} images available")
        
        # Test emotion analysis
        emotion_result = selector.analyze_text_emotion("The dark forest was scary and mysterious.")
        print(f"✓ Emotion analysis: {emotion_result['emotion']} (intensity: {emotion_result['intensity']:.2f})")
        
        # Test image selection
        images = selector.select_images_for_text("I feel happy and joyful today!")
        print(f"✓ Image selection: {len(images['selected_images'])} images selected")
        
    except Exception as e:
        print(f"✗ AIImageSelector test failed: {e}")
    
    # Test AI Text Generator
    try:
        from backend.ai_text_generator import AITextGenerator
        generator = AITextGenerator()
        
        # Check Ollama status
        ollama_status = generator.check_ollama_status()
        print(f"✓ AITextGenerator initialized. Ollama: {ollama_status['status']}")
        
        # Test Google API if available
        if generator.gemini_model:
            print("✓ Google Gemini API available")
        else:
            print("⚠ Google Gemini API not configured")
            
    except Exception as e:
        print(f"✗ AITextGenerator test failed: {e}")

def test_web_backend():
    """Test web backend imports"""
    print("\nTesting web backend...")
    
    try:
        from web.backend.main import app
        print("✓ FastAPI app imported successfully")
        
        # Test that we can access the app
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        
    except Exception as e:
        print(f"✗ Web backend test failed: {e}")

def test_ai_integration():
    """Test AI integration with sample data"""
    print("\nTesting AI integration...")
    
    try:
        from backend.ai_image_selector import AIImageSelector
        from backend.ai_text_generator import AITextGenerator
        
        selector = AIImageSelector()
        generator = AITextGenerator()
        
        test_text = "The old house creaked in the wind, its windows rattling like bones."
        
        # Test complete workflow
        print(f"Testing with: '{test_text}'")
        
        # 1. Emotion analysis
        emotion_analysis = selector.analyze_text_emotion(test_text)
        print(f"✓ Detected emotion: {emotion_analysis['emotion']} (intensity: {emotion_analysis['intensity']:.2f})")
        
        # 2. Image selection
        image_selection = selector.select_images_for_text(test_text, count=2)
        print(f"✓ Selected {len(image_selection['selected_images'])} images")
        
        # 3. Text enhancement (if Google API available)
        if generator.gemini_model:
            enhancement = generator.enhance_narrative_text(test_text, style="immersive")
            if enhancement.get("success"):
                print("✓ Text enhancement successful")
                print(f"  Enhanced length: {enhancement.get('response_length', 0)} chars")
            else:
                print(f"⚠ Text enhancement failed: {enhancement.get('error', 'Unknown error')}")
        else:
            print("⚠ Text enhancement skipped (Google API not configured)")
        
        print("✓ AI integration test completed successfully")
        
    except Exception as e:
        print(f"✗ AI integration test failed: {e}")

if __name__ == "__main__":
    print("=== AI-Reader Debug Script (Enhanced) ===")
    test_imports()
    test_components()
    test_web_backend()
    test_ai_integration()
    print("\n=== Debug Complete ===")