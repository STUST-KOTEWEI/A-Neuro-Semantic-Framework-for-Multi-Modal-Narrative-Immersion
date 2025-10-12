"""Main orchestrator for the MultisensoryReader workflow"""
from typing import Dict, Any, List, Optional
from .agents.reader_agent import ReaderAgent
from .agents.emotion_agent import EmotionAgent
from .agents.device_agent import DeviceAgent
from .agents.memory_agent import MemoryAgent
from .connectors.http_connector import HTTPConnector
from .connectors.pinecone_connector import PineconeConnector
from .connectors.postgres_connector import PostgresConnector


class Orchestrator:
    """
    Orchestrator for MultisensoryReader workflow
    
    Orchestrates: text -> segments -> TTS -> haptics/scent
    Supports: emotion-aware voice style and memory lookup
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the orchestrator with agents and connectors
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Initialize connectors
        self.connectors = self._initialize_connectors()
        
        # Initialize agents
        self.reader_agent = ReaderAgent('reader', self.connectors)
        self.emotion_agent = EmotionAgent('emotion', self.connectors)
        self.device_agent = DeviceAgent('device', self.connectors)
        self.memory_agent = MemoryAgent('memory', self.connectors)
        
        # Playback state
        self.current_state = {
            'is_playing': False,
            'current_segment': 0,
            'segments': [],
            'playback_url': None
        }
    
    def _initialize_connectors(self) -> Dict[str, Any]:
        """Initialize all connectors from config"""
        connectors = {}
        
        connector_configs = self.config.get('connectors', {})
        
        # Initialize HTTP connectors
        for name in ['textPreprocessor', 'emotionModelAPI', 'TTS', 'bhapticsSDK', 'aromajoinAPI']:
            if name in connector_configs and connector_configs[name].get('type') == 'http':
                connectors[name] = HTTPConnector(connector_configs[name])
        
        # Initialize Pinecone connector
        if 'vectorDB' in connector_configs and connector_configs['vectorDB'].get('type') == 'pinecone':
            connectors['vectorDB'] = PineconeConnector(connector_configs['vectorDB'])
        
        # Initialize Postgres connector
        if 'postgres' in connector_configs and connector_configs['postgres'].get('type') == 'sql':
            connectors['postgres'] = PostgresConnector(connector_configs['postgres'])
        
        return connectors
    
    async def play(self, text: str, user_id: str = 'default') -> Dict[str, Any]:
        """
        Start playback of text with multisensory experience
        
        Args:
            text: Text content to play
            user_id: User identifier
            
        Returns:
            Dictionary with playback URL and metadata
        """
        # Step 1: Get user preferences
        prefs_result = await self.memory_agent.process({
            'operation': 'get_preferences',
            'user_id': user_id
        })
        user_prefs = prefs_result.get('preferences', {})
        
        # Step 2: Segment the text
        reader_result = await self.reader_agent.process({
            'text': text,
            'segmentation_type': 'paragraph'
        })
        segments = reader_result.get('segments', [])
        
        if not segments:
            return {
                'error': 'No segments generated',
                'playback_url': None
            }
        
        # Step 3: Predict emotion from text
        emotion_result = await self.emotion_agent.process({
            'text': text
        })
        emotion = emotion_result.get('emotion', 'neutral')
        tts_settings = emotion_result.get('tts_settings', {})
        
        # Step 4: Generate device outputs for first segment
        first_segment = segments[0]
        device_result = await self.device_agent.process({
            'highlights': first_segment.get('highlights', []),
            'emotion': emotion,
            'timestamps': [h.get('start_pos', 0) for h in first_segment.get('highlights', [])]
        })
        
        # Step 5: Synthesize TTS (mock URL for now)
        # In real implementation, would call TTS connector
        playback_url = f"https://api.tts.example.com/audio/{user_id}/segment_0.mp3"
        
        # Update state
        self.current_state = {
            'is_playing': True,
            'current_segment': 0,
            'segments': segments,
            'playback_url': playback_url,
            'emotion': emotion,
            'tts_settings': tts_settings,
            'device_outputs': device_result
        }
        
        return {
            'playback_url': playback_url,
            'metadata': {
                'total_segments': len(segments),
                'current_segment': 0,
                'emotion': emotion,
                'tts_settings': tts_settings,
                'haptic_events': device_result.get('haptic_events', []),
                'scent_events': device_result.get('scent_events', []),
                'total_duration': reader_result.get('total_duration', 0)
            }
        }
    
    async def pause(self) -> Dict[str, Any]:
        """
        Pause current playback
        
        Returns:
            Current playback state
        """
        self.current_state['is_playing'] = False
        
        return {
            'status': 'paused',
            'current_segment': self.current_state.get('current_segment', 0),
            'is_playing': False
        }
    
    async def seek(self, segment_index: int) -> Dict[str, Any]:
        """
        Seek to a specific segment
        
        Args:
            segment_index: Index of segment to seek to
            
        Returns:
            Updated playback state
        """
        segments = self.current_state.get('segments', [])
        
        if not segments:
            return {
                'status': 'error',
                'error': 'No segments available',
                'current_segment': 0,
                'playback_url': '',
                'segment_text': '',
                'segment_duration': 0.0
            }
        
        if segment_index < 0 or segment_index >= len(segments):
            return {
                'status': 'error',
                'error': 'Invalid segment index',
                'current_segment': self.current_state.get('current_segment', 0),
                'playback_url': self.current_state.get('playback_url', ''),
                'segment_text': '',
                'segment_duration': 0.0
            }
        
        self.current_state['current_segment'] = segment_index
        segment = segments[segment_index]
        
        # Generate new playback URL for this segment
        playback_url = f"https://api.tts.example.com/audio/segment_{segment_index}.mp3"
        self.current_state['playback_url'] = playback_url
        
        return {
            'status': 'seeked',
            'current_segment': segment_index,
            'playback_url': playback_url,
            'segment_text': segment.get('text', ''),
            'segment_duration': segment.get('duration', 0)
        }
    
    async def summary(self) -> Dict[str, Any]:
        """
        Get summary of current session
        
        Returns:
            Summary dictionary with key information
        """
        segments = self.current_state.get('segments', [])
        
        # Extract key highlights from all segments
        all_highlights = []
        for segment in segments:
            all_highlights.extend(segment.get('highlights', []))
        
        # Generate summary (simplified version)
        summary_text = self._generate_summary(segments)
        
        return {
            'summary': summary_text,
            'total_segments': len(segments),
            'total_highlights': len(all_highlights),
            'emotion': self.current_state.get('emotion', 'neutral'),
            'current_position': self.current_state.get('current_segment', 0),
            'is_playing': self.current_state.get('is_playing', False)
        }
    
    def _generate_summary(self, segments: List[Dict[str, Any]]) -> str:
        """
        Generate a text summary from segments
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            Summary text
        """
        if not segments:
            return "No content available."
        
        # Simple summary: take first sentence from each segment
        summary_parts = []
        for segment in segments[:3]:  # Take first 3 segments
            text = segment.get('text', '')
            # Get first sentence
            first_sentence = text.split('.')[0] + '.' if '.' in text else text[:100]
            summary_parts.append(first_sentence)
        
        summary = ' '.join(summary_parts)
        if len(segments) > 3:
            summary += f" ... ({len(segments) - 3} more segments)"
        
        return summary
