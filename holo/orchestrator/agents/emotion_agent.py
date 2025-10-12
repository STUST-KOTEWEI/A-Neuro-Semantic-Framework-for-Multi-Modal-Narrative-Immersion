"""Emotion agent for predicting emotional tone and mapping to TTS settings"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class EmotionAgent(BaseAgent):
    """
    EmotionAgent handles:
    - Predict emotional tone from user voice sample or text
    - Map label -> TTS voice preset and prosody settings
    """
    
    # Emotion to voice preset mapping
    EMOTION_PRESETS = {
        'happy': {
            'voice': 'cheerful',
            'rate': 1.1,
            'pitch': 1.1,
            'volume': 1.0
        },
        'sad': {
            'voice': 'melancholic',
            'rate': 0.9,
            'pitch': 0.9,
            'volume': 0.8
        },
        'angry': {
            'voice': 'intense',
            'rate': 1.2,
            'pitch': 1.0,
            'volume': 1.1
        },
        'calm': {
            'voice': 'soothing',
            'rate': 0.95,
            'pitch': 1.0,
            'volume': 0.9
        },
        'excited': {
            'voice': 'energetic',
            'rate': 1.15,
            'pitch': 1.05,
            'volume': 1.0
        },
        'neutral': {
            'voice': 'normal',
            'rate': 1.0,
            'pitch': 1.0,
            'volume': 1.0
        }
    }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict emotion and map to TTS settings
        
        Args:
            data: Dictionary containing 'text' or 'voice_sample'
            
        Returns:
            Dictionary with emotion label and TTS settings
        """
        text = data.get('text', '')
        voice_sample = data.get('voice_sample')
        
        # Predict emotion
        emotion = await self._predict_emotion(text, voice_sample)
        
        # Get TTS settings for the emotion
        tts_settings = self._get_tts_settings(emotion)
        
        return {
            'emotion': emotion,
            'tts_settings': tts_settings,
            'confidence': 0.85  # Mock confidence score
        }
    
    async def _predict_emotion(self, text: str, voice_sample: Optional[bytes] = None) -> str:
        """
        Predict emotion from text or voice sample
        
        Args:
            text: Input text
            voice_sample: Optional voice sample bytes
            
        Returns:
            Emotion label
        """
        # In a real implementation, this would call an emotion model API
        # For now, use simple keyword-based heuristic
        
        if voice_sample:
            # Would process voice sample with emotion model
            # For now, return default
            return 'neutral'
        
        # Simple text-based emotion detection
        text_lower = text.lower()
        
        # Define emotion keywords
        emotion_keywords = {
            'happy': ['happy', 'joy', 'delighted', 'pleased', 'cheerful', '😊', '😄'],
            'sad': ['sad', 'unhappy', 'depressed', 'melancholy', 'sorrowful', '😢', '😞'],
            'angry': ['angry', 'furious', 'enraged', 'mad', 'irritated', '😠', '😡'],
            'excited': ['excited', 'thrilled', 'enthusiastic', 'eager', 'pumped', '🎉', '✨'],
            'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'relaxed', '🧘']
        }
        
        # Score each emotion
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Return emotion with highest score, or 'neutral' if no matches
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return 'neutral'
    
    def _get_tts_settings(self, emotion: str) -> Dict[str, Any]:
        """
        Get TTS settings for a given emotion
        
        Args:
            emotion: Emotion label
            
        Returns:
            Dictionary with TTS settings
        """
        return self.EMOTION_PRESETS.get(emotion, self.EMOTION_PRESETS['neutral'])
