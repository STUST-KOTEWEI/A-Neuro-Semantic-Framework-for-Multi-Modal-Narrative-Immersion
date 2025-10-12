"""Tests for individual agents"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from holo.orchestrator.agents import ReaderAgent, EmotionAgent, DeviceAgent, MemoryAgent


@pytest.mark.asyncio
async def test_reader_agent_paragraph_segmentation():
    """Test ReaderAgent paragraph segmentation"""
    agent = ReaderAgent('test_reader')
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    
    result = await agent.process({
        'text': text,
        'segmentation_type': 'paragraph'
    })
    
    assert 'segments' in result
    assert len(result['segments']) == 3
    assert result['segment_count'] == 3
    assert 'total_duration' in result


@pytest.mark.asyncio
async def test_reader_agent_sentence_segmentation():
    """Test ReaderAgent sentence segmentation"""
    agent = ReaderAgent('test_reader')
    text = "First sentence. Second sentence! Third sentence?"
    
    result = await agent.process({
        'text': text,
        'segmentation_type': 'sentence'
    })
    
    assert 'segments' in result
    assert len(result['segments']) == 3


@pytest.mark.asyncio
async def test_reader_agent_highlights():
    """Test ReaderAgent highlight extraction"""
    agent = ReaderAgent('test_reader')
    text = 'He said "This is important" and emphasized significant details.'
    
    result = await agent.process({
        'text': text,
        'segmentation_type': 'paragraph'
    })
    
    segments = result['segments']
    assert len(segments) > 0
    highlights = segments[0]['highlights']
    assert len(highlights) > 0


@pytest.mark.asyncio
async def test_emotion_agent_happy():
    """Test EmotionAgent happy emotion detection"""
    agent = EmotionAgent('test_emotion')
    text = "I am so happy and joyful today! 😊"
    
    result = await agent.process({'text': text})
    
    assert result['emotion'] == 'happy'
    assert 'tts_settings' in result
    assert result['tts_settings']['voice'] == 'cheerful'


@pytest.mark.asyncio
async def test_emotion_agent_sad():
    """Test EmotionAgent sad emotion detection"""
    agent = EmotionAgent('test_emotion')
    text = "I feel sad and depressed 😢"
    
    result = await agent.process({'text': text})
    
    assert result['emotion'] == 'sad'
    assert result['tts_settings']['voice'] == 'melancholic'


@pytest.mark.asyncio
async def test_emotion_agent_calm():
    """Test EmotionAgent calm emotion detection"""
    agent = EmotionAgent('test_emotion')
    text = "Everything is calm and peaceful 🧘"
    
    result = await agent.process({'text': text})
    
    assert result['emotion'] == 'calm'
    assert result['tts_settings']['voice'] == 'soothing'


@pytest.mark.asyncio
async def test_device_agent_haptics():
    """Test DeviceAgent haptic pattern generation"""
    agent = DeviceAgent('test_device')
    highlights = [
        {'text': 'highlight1', 'start_pos': 0, 'type': 'quote'},
        {'text': 'highlight2', 'start_pos': 10, 'type': 'emphasis'}
    ]
    
    result = await agent.process({
        'highlights': highlights,
        'emotion': 'happy',
        'timestamps': [0.0, 1.5]
    })
    
    assert 'haptic_events' in result
    assert len(result['haptic_events']) == 2
    assert result['haptic_events'][0]['pattern'] == 'gentle_pulse'


@pytest.mark.asyncio
async def test_device_agent_scent():
    """Test DeviceAgent scent trigger generation"""
    agent = DeviceAgent('test_device')
    
    result = await agent.process({
        'highlights': [],
        'emotion': 'calm',
        'timestamps': []
    })
    
    assert 'scent_events' in result
    assert len(result['scent_events']) == 1
    assert result['scent_events'][0]['scent'] == 'chamomile'


@pytest.mark.asyncio
async def test_memory_agent_get_preferences():
    """Test MemoryAgent get preferences"""
    agent = MemoryAgent('test_memory')
    
    result = await agent.process({
        'operation': 'get_preferences',
        'user_id': 'test_user'
    })
    
    assert 'user_id' in result
    assert 'preferences' in result
    assert 'reading_speed' in result['preferences']


@pytest.mark.asyncio
async def test_memory_agent_set_preferences():
    """Test MemoryAgent set preferences"""
    agent = MemoryAgent('test_memory')
    
    result = await agent.process({
        'operation': 'set_preferences',
        'user_id': 'test_user',
        'preferences': {'reading_speed': 1.5}
    })
    
    assert result['success'] is True
    assert 'updated_preferences' in result


@pytest.mark.asyncio
async def test_memory_agent_search_sessions():
    """Test MemoryAgent search sessions"""
    agent = MemoryAgent('test_memory')
    
    result = await agent.process({
        'operation': 'search_sessions',
        'user_id': 'test_user',
        'query': 'test query'
    })
    
    assert 'query' in result
    assert 'results' in result
    assert 'result_count' in result


@pytest.mark.asyncio
async def test_memory_agent_save_bookmark():
    """Test MemoryAgent save bookmark"""
    agent = MemoryAgent('test_memory')
    
    result = await agent.process({
        'operation': 'save_bookmark',
        'user_id': 'test_user',
        'bookmark': {'segment': 5, 'note': 'Important'}
    })
    
    assert result['success'] is True
    assert 'bookmark_id' in result
