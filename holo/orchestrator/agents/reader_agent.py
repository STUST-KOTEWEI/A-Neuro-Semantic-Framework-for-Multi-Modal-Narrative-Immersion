"""Reader agent for text ingestion, segmentation, and highlight extraction"""
from typing import Dict, Any, List
import re
from .base_agent import BaseAgent


class ReaderAgent(BaseAgent):
    """
    ReaderAgent handles:
    - Text ingestion (epub/txt/URL)
    - Segmentation (paragraph/sentence)
    - Highlight extraction (tf-idf + transformer attention)
    - Generate segment metadata (start/end timestamps, highlight positions)
    """
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process text input and generate segments with metadata
        
        Args:
            data: Dictionary containing 'text' and optional 'segmentation_type'
            
        Returns:
            Dictionary with segments and metadata
        """
        text = data.get('text', '')
        segmentation_type = data.get('segmentation_type', 'paragraph')
        
        # Segment the text
        segments = self._segment_text(text, segmentation_type)
        
        # Extract highlights from each segment
        enriched_segments = []
        cumulative_time = 0.0
        
        for idx, segment in enumerate(segments):
            # Estimate reading time (average 200 words per minute)
            word_count = len(segment.split())
            duration = (word_count / 200) * 60  # in seconds
            
            # Extract highlights (simplified version)
            highlights = self._extract_highlights(segment)
            
            enriched_segment = {
                'id': idx,
                'text': segment,
                'start_time': cumulative_time,
                'end_time': cumulative_time + duration,
                'duration': duration,
                'highlights': highlights,
                'word_count': word_count
            }
            
            enriched_segments.append(enriched_segment)
            cumulative_time += duration
        
        return {
            'segments': enriched_segments,
            'total_duration': cumulative_time,
            'segment_count': len(enriched_segments)
        }
    
    def _segment_text(self, text: str, segmentation_type: str) -> List[str]:
        """
        Segment text by paragraph or sentence
        
        Args:
            text: Input text
            segmentation_type: 'paragraph' or 'sentence'
            
        Returns:
            List of text segments
        """
        if segmentation_type == 'sentence':
            # Simple sentence segmentation
            sentences = re.split(r'[.!?]+\s+', text)
            return [s.strip() for s in sentences if s.strip()]
        else:
            # Paragraph segmentation
            paragraphs = text.split('\n\n')
            return [p.strip() for p in paragraphs if p.strip()]
    
    def _extract_highlights(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract highlights from text (simplified version)
        In a full implementation, this would use tf-idf or transformer attention
        
        Args:
            text: Input text segment
            
        Returns:
            List of highlight dictionaries
        """
        # Simple heuristic: extract words in quotes or capitalized phrases
        highlights = []
        
        # Find quoted text
        quoted = re.findall(r'"([^"]+)"', text)
        for quote in quoted:
            start = text.find(f'"{quote}"')
            if start != -1:
                highlights.append({
                    'text': quote,
                    'start_pos': start,
                    'end_pos': start + len(quote) + 2,
                    'type': 'quote'
                })
        
        # Find emphasized words (simple heuristic: longer words)
        words = text.split()
        for word in words:
            if len(word) > 10:  # Arbitrary threshold for "important" words
                start = text.find(word)
                if start != -1:
                    highlights.append({
                        'text': word,
                        'start_pos': start,
                        'end_pos': start + len(word),
                        'type': 'emphasis'
                    })
        
        return highlights
