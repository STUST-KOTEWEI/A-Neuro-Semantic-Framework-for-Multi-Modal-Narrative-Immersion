"""Device agent for mapping highlights/emotions to haptics and scent"""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class DeviceAgent(BaseAgent):
    """
    DeviceAgent handles:
    - Map segment highlights/emotion events -> haptics patterns
    - Call HAPTICS SDK / SCENT API
    """
    
    # Emotion to haptic pattern mapping
    EMOTION_HAPTICS = {
        'happy': {
            'pattern': 'gentle_pulse',
            'intensity': 0.6,
            'duration': 200
        },
        'sad': {
            'pattern': 'slow_wave',
            'intensity': 0.4,
            'duration': 500
        },
        'angry': {
            'pattern': 'sharp_burst',
            'intensity': 0.9,
            'duration': 150
        },
        'calm': {
            'pattern': 'smooth_wave',
            'intensity': 0.3,
            'duration': 300
        },
        'excited': {
            'pattern': 'rapid_pulse',
            'intensity': 0.8,
            'duration': 100
        },
        'neutral': {
            'pattern': 'subtle_tap',
            'intensity': 0.5,
            'duration': 200
        }
    }
    
    # Emotion to scent mapping
    EMOTION_SCENTS = {
        'happy': 'citrus',
        'sad': 'lavender',
        'angry': 'peppermint',
        'calm': 'chamomile',
        'excited': 'eucalyptus',
        'neutral': 'vanilla'
    }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map highlights and emotions to device outputs
        
        Args:
            data: Dictionary containing 'highlights', 'emotion', and 'timestamps'
            
        Returns:
            Dictionary with haptic patterns and scent triggers
        """
        highlights = data.get('highlights', [])
        emotion = data.get('emotion', 'neutral')
        timestamps = data.get('timestamps', [])
        
        # Generate haptic patterns
        haptic_events = await self._generate_haptic_patterns(highlights, emotion, timestamps)
        
        # Generate scent triggers
        scent_events = await self._generate_scent_triggers(emotion)
        
        return {
            'haptic_events': haptic_events,
            'scent_events': scent_events
        }
    
    async def _generate_haptic_patterns(
        self, 
        highlights: List[Dict[str, Any]], 
        emotion: str,
        timestamps: List[float]
    ) -> List[Dict[str, Any]]:
        """
        Generate haptic patterns for highlights and emotion
        
        Args:
            highlights: List of highlight dictionaries
            emotion: Emotion label
            timestamps: List of timestamp values
            
        Returns:
            List of haptic event dictionaries
        """
        haptic_events = []
        
        # Base emotion haptic
        emotion_haptic = self.EMOTION_HAPTICS.get(emotion, self.EMOTION_HAPTICS['neutral'])
        
        # Create haptic event for each highlight
        for idx, highlight in enumerate(highlights):
            timestamp = timestamps[idx] if idx < len(timestamps) else 0.0
            
            haptic_event = {
                'timestamp': timestamp,
                'pattern': emotion_haptic['pattern'],
                'intensity': emotion_haptic['intensity'],
                'duration': emotion_haptic['duration'],
                'trigger': 'highlight',
                'metadata': {
                    'highlight_text': highlight.get('text', ''),
                    'highlight_type': highlight.get('type', 'unknown')
                }
            }
            haptic_events.append(haptic_event)
        
        # In a real implementation, would call bhapticsSDK
        # connector = self.get_connector('bhapticsSDK')
        # if connector:
        #     await connector.trigger_haptics(haptic_events)
        
        return haptic_events
    
    async def _generate_scent_triggers(self, emotion: str) -> List[Dict[str, Any]]:
        """
        Generate scent triggers for emotion
        
        Args:
            emotion: Emotion label
            
        Returns:
            List of scent event dictionaries
        """
        scent = self.EMOTION_SCENTS.get(emotion, self.EMOTION_SCENTS['neutral'])
        
        scent_event = {
            'scent': scent,
            'intensity': 0.5,
            'duration': 3000,  # milliseconds
            'trigger': 'emotion'
        }
        
        # In a real implementation, would call aromajoinAPI
        # connector = self.get_connector('aromajoinAPI')
        # if connector:
        #     await connector.trigger_scent([scent_event])
        
        return [scent_event]
