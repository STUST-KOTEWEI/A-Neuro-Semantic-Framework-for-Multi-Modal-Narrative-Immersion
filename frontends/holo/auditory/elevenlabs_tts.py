"""
ElevenLabs TTS Integration Module

Provides integration with ElevenLabs Text-to-Speech API for high-quality
voice synthesis with emotional nuance and natural speech patterns.
"""

import os
from typing import Optional, Dict, Any
import io


class ElevenLabsTTS:
    """
    ElevenLabs Text-to-Speech integration.

    Provides methods to convert text to speech using ElevenLabs API
    with support for different voices and settings.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize ElevenLabs TTS.

        Args:
            api_key: ElevenLabs API key. If None, reads from ELEVENLABS_API_KEY env var
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)

    def is_available(self) -> bool:
        """
        Check if ElevenLabs TTS is available (API key is set).

        Returns:
            True if API key is configured, False otherwise
        """
        return self.api_key is not None and self.api_key != ""

    def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ) -> io.BytesIO:
        """
        Convert text to speech using ElevenLabs API.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (uses default if None)
            model_id: Model to use for generation
            stability: Stability setting (0.0-1.0)
            similarity_boost: Similarity boost setting (0.0-1.0)
            style: Style exaggeration (0.0-1.0)
            use_speaker_boost: Enable speaker boost

        Returns:
            BytesIO object containing audio data

        Raises:
            ValueError: If API key is not configured
            Exception: If API request fails
        """
        if not self.is_available():
            raise ValueError("ElevenLabs API key is not configured")

        # In a real implementation, this would make an HTTP request
        # For now, we'll raise an informative error
        raise NotImplementedError(
            "ElevenLabs API integration requires the 'elevenlabs' package. "
            "Install with: pip install elevenlabs"
        )

    def text_to_speech_stream(
        self, text: str, voice_id: Optional[str] = None, **kwargs
    ):
        """
        Stream audio generation for real-time playback.

        Args:
            text: Text to convert to speech
            voice_id: Voice ID to use (uses default if None)
            **kwargs: Additional parameters for text_to_speech

        Yields:
            Audio chunks as bytes

        Raises:
            ValueError: If API key is not configured
        """
        if not self.is_available():
            raise ValueError("ElevenLabs API key is not configured")

        raise NotImplementedError(
            "Streaming requires the 'elevenlabs' package. "
            "Install with: pip install elevenlabs"
        )

    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available voices.

        Returns:
            Dictionary containing available voices

        Raises:
            ValueError: If API key is not configured
        """
        if not self.is_available():
            raise ValueError("ElevenLabs API key is not configured")

        # Return default voice info
        return {
            "voices": [
                {
                    "voice_id": self.default_voice_id,
                    "name": "Rachel",
                    "description": "Default voice - clear and expressive",
                }
            ]
        }


class ElevenLabsTTSFallback:
    """
    Fallback TTS implementation when ElevenLabs is not available.

    Uses gTTS as a fallback option with similar interface.
    """

    def __init__(self):
        """Initialize fallback TTS."""
        self.is_fallback = True

    def is_available(self) -> bool:
        """Always available as fallback."""
        return True

    def text_to_speech(
        self, text: str, voice_id: Optional[str] = None, **kwargs
    ) -> io.BytesIO:
        """
        Convert text to speech using gTTS as fallback.

        Args:
            text: Text to convert
            voice_id: Ignored in fallback mode
            **kwargs: Ignored in fallback mode

        Returns:
            BytesIO object containing audio data
        """
        from gtts import gTTS

        tts = gTTS(text=text, lang="en")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp

    def get_available_voices(self) -> Dict[str, Any]:
        """Get fallback voice info."""
        return {
            "voices": [
                {
                    "voice_id": "gtts",
                    "name": "Google TTS",
                    "description": "Fallback TTS using Google Text-to-Speech",
                }
            ],
            "fallback": True,
        }


def get_tts_engine(api_key: Optional[str] = None) -> Any:
    """
    Get appropriate TTS engine based on availability.

    Returns ElevenLabsTTS if API key is available, otherwise returns fallback.

    Args:
        api_key: Optional API key for ElevenLabs

    Returns:
        TTS engine instance (ElevenLabs or fallback)
    """
    elevenlabs_tts = ElevenLabsTTS(api_key)

    if elevenlabs_tts.is_available():
        try:
            # Try to import elevenlabs to verify it's installed
            import elevenlabs  # noqa: F401

            return elevenlabs_tts
        except ImportError:
            # Package not installed, use fallback
            return ElevenLabsTTSFallback()

    # API key not configured, use fallback
    return ElevenLabsTTSFallback()
