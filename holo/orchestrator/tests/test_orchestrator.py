"""Tests for the Orchestrator class"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from holo.orchestrator import Orchestrator


@pytest.fixture
def orchestrator():
    """Create an orchestrator instance for testing"""
    config = {
        'connectors': {
            'textPreprocessor': {'type': 'http', 'url': 'https://example.com/api/preprocess'},
            'vectorDB': {'type': 'pinecone', 'index': 'test_index'},
            'emotionModelAPI': {'type': 'http', 'url': 'https://example.com/api/emotion'},
            'TTS': {'type': 'http', 'url': 'https://api.tts.example.com'},
            'bhapticsSDK': {'type': 'http', 'url': 'https://example.com/api/haptics'},
            'aromajoinAPI': {'type': 'http', 'url': 'https://example.com/api/scent'},
            'postgres': {'type': 'sql', 'connection': 'postgres://test'}
        }
    }
    return Orchestrator(config)


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return """
    The forest was alive with the sounds of night. Crickets chirped in harmony.
    A gentle breeze rustled through the leaves, creating a peaceful atmosphere.
    """


@pytest.mark.asyncio
async def test_play(orchestrator, sample_text):
    """Test the play functionality"""
    result = await orchestrator.play(sample_text, "test_user")
    
    assert 'playback_url' in result
    assert 'metadata' in result
    assert result['metadata']['total_segments'] > 0
    assert 'emotion' in result['metadata']
    assert 'tts_settings' in result['metadata']
    assert 'haptic_events' in result['metadata']
    assert 'scent_events' in result['metadata']


@pytest.mark.asyncio
async def test_pause(orchestrator, sample_text):
    """Test the pause functionality"""
    # First play
    await orchestrator.play(sample_text, "test_user")
    
    # Then pause
    result = await orchestrator.pause()
    
    assert result['status'] == 'paused'
    assert result['is_playing'] is False
    assert 'current_segment' in result


@pytest.mark.asyncio
async def test_seek(orchestrator, sample_text):
    """Test the seek functionality"""
    # First play
    await orchestrator.play(sample_text, "test_user")
    
    # Then seek to segment 0
    result = await orchestrator.seek(0)
    
    assert result['status'] == 'seeked'
    assert result['current_segment'] == 0
    assert 'playback_url' in result
    assert 'segment_text' in result
    assert 'segment_duration' in result


@pytest.mark.asyncio
async def test_seek_invalid_segment(orchestrator, sample_text):
    """Test seeking to an invalid segment"""
    # First play
    await orchestrator.play(sample_text, "test_user")
    
    # Try to seek to invalid segment
    result = await orchestrator.seek(999)
    
    assert result['status'] == 'error'
    assert 'error' in result


@pytest.mark.asyncio
async def test_summary(orchestrator, sample_text):
    """Test the summary functionality"""
    # First play
    await orchestrator.play(sample_text, "test_user")
    
    # Get summary
    result = await orchestrator.summary()
    
    assert 'summary' in result
    assert 'total_segments' in result
    assert 'total_highlights' in result
    assert 'emotion' in result
    assert 'current_position' in result
    assert 'is_playing' in result


@pytest.mark.asyncio
async def test_emotion_detection_happy(orchestrator):
    """Test emotion detection for happy text"""
    happy_text = "I am so happy and delighted! This is wonderful and joyful!"
    result = await orchestrator.play(happy_text, "test_user")
    
    assert result['metadata']['emotion'] == 'happy'


@pytest.mark.asyncio
async def test_emotion_detection_sad(orchestrator):
    """Test emotion detection for sad text"""
    sad_text = "I feel so sad and depressed. This is a sorrowful and melancholy day."
    result = await orchestrator.play(sad_text, "test_user")
    
    assert result['metadata']['emotion'] == 'sad'


@pytest.mark.asyncio
async def test_emotion_detection_calm(orchestrator):
    """Test emotion detection for calm text"""
    calm_text = "Everything is calm and peaceful. The tranquil atmosphere is very relaxing."
    result = await orchestrator.play(calm_text, "test_user")
    
    assert result['metadata']['emotion'] == 'calm'
