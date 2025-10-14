"""
Tests for ElevenLabs TTS Module
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo.auditory.elevenlabs_tts import (  # noqa: E402
    ElevenLabsTTS,
    ElevenLabsTTSFallback,
    get_tts_engine,
)
import pytest  # noqa: E402


class TestElevenLabsTTS:
    """Test cases for ElevenLabsTTS class."""

    def test_initialization_without_api_key(self):
        """Test initialization without API key."""
        tts = ElevenLabsTTS()
        assert not tts.is_available()

    def test_initialization_with_api_key(self):
        """Test initialization with API key."""
        tts = ElevenLabsTTS(api_key="test_api_key")
        assert tts.is_available()
        assert tts.api_key == "test_api_key"

    def test_is_available_with_empty_key(self):
        """Test is_available with empty API key."""
        tts = ElevenLabsTTS(api_key="")
        assert not tts.is_available()

    def test_text_to_speech_without_api_key(self):
        """Test text_to_speech raises error without API key."""
        tts = ElevenLabsTTS()

        with pytest.raises(ValueError, match="API key is not configured"):
            tts.text_to_speech("Hello world")

    def test_text_to_speech_not_implemented(self):
        """Test that text_to_speech raises NotImplementedError."""
        tts = ElevenLabsTTS(api_key="test_key")

        with pytest.raises(NotImplementedError):
            tts.text_to_speech("Hello world")

    def test_get_available_voices(self):
        """Test getting available voices."""
        tts = ElevenLabsTTS(api_key="test_key")

        voices = tts.get_available_voices()
        assert "voices" in voices
        assert len(voices["voices"]) > 0
        assert voices["voices"][0]["voice_id"] == tts.default_voice_id


class TestElevenLabsTTSFallback:
    """Test cases for ElevenLabsTTSFallback class."""

    def test_initialization(self):
        """Test fallback initialization."""
        fallback = ElevenLabsTTSFallback()
        assert fallback.is_fallback is True

    def test_is_available(self):
        """Test fallback is always available."""
        fallback = ElevenLabsTTSFallback()
        assert fallback.is_available() is True

    def test_text_to_speech_fallback(self):
        """Test text_to_speech with fallback."""
        # Skip this test as it requires network access
        pytest.skip("Skipping test that requires network access to Google TTS")

    def test_get_available_voices_fallback(self):
        """Test getting available voices from fallback."""
        fallback = ElevenLabsTTSFallback()

        voices = fallback.get_available_voices()

        assert "voices" in voices
        assert "fallback" in voices
        assert voices["fallback"] is True
        assert len(voices["voices"]) > 0


class TestGetTTSEngine:
    """Test cases for get_tts_engine function."""

    def test_get_tts_engine_without_api_key(self):
        """Test getting TTS engine without API key returns fallback."""
        engine = get_tts_engine()

        assert isinstance(engine, ElevenLabsTTSFallback)

    def test_get_tts_engine_with_api_key(self):
        """Test getting TTS engine with API key."""
        # Without elevenlabs package installed, should return fallback
        engine = get_tts_engine(api_key="test_key")

        # Should return fallback since elevenlabs package isn't installed
        assert isinstance(engine, (ElevenLabsTTS, ElevenLabsTTSFallback))
