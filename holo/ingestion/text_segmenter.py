"""
Text Segmentation Module for processing narrative text into meaningful chunks.

This module provides functionality to segment text based on various criteria
including sentences, semantic boundaries, and length constraints.
"""

import re
from typing import List, Dict, Any


class TextSegmenter:
    """
    Segments text into meaningful chunks for processing.
    
    Supports multiple segmentation strategies:
    - Sentence-based: Split by sentence boundaries
    - Length-based: Split by character/word count
    - Semantic-based: Split by paragraphs or topic boundaries
    """
    
    def __init__(self, max_chunk_size: int = 500):
        """
        Initialize the text segmenter.
        
        Args:
            max_chunk_size: Maximum characters per chunk (default: 500)
        """
        self.max_chunk_size = max_chunk_size
        
    def segment_by_sentences(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by sentence boundaries with size constraints.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of text segments with metadata
        """
        # Simple sentence detection using punctuation
        sentences = re.split(r'([.!?]+)', text)
        segments: List[Dict[str, Any]] = []
        current_chunk = ""
        current_index = 0
        
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i].strip()
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            if not sentence:
                continue
                
            full_sentence = sentence + punctuation
            
            # If adding this sentence would exceed max size, save current chunk
            if current_chunk and len(current_chunk) + len(full_sentence) > self.max_chunk_size:
                segments.append({
                    "text": current_chunk.strip(),
                    "index": current_index,
                    "type": "sentence_group",
                    "length": len(current_chunk.strip())
                })
                current_chunk = ""
                current_index += 1
            
            current_chunk += " " + full_sentence if current_chunk else full_sentence
        
        # Add any remaining text
        if current_chunk.strip():
            segments.append({
                "text": current_chunk.strip(),
                "index": current_index,
                "type": "sentence_group",
                "length": len(current_chunk.strip())
            })
        
        return segments
    
    def segment_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text by paragraph boundaries.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of dictionaries containing segment information
        """
        # Split by double newlines or multiple spaces/newlines
        paragraphs = re.split(r'\n\s*\n', text)
        
        segments: List[Dict[str, Any]] = []
        for idx, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If paragraph is too long, further segment it
            if len(paragraph) > self.max_chunk_size:
                sub_segments = self.segment_by_sentences(paragraph)
                for sub_seg in sub_segments:
                    sub_seg["parent_index"] = idx
                    segments.append(sub_seg)
            else:
                segments.append({
                    "text": paragraph,
                    "index": idx,
                    "type": "paragraph",
                    "length": len(paragraph)
                })
        
        return segments
    
    def segment_adaptive(self, text: str) -> List[Dict[str, Any]]:
        """
        Adaptively segment text using a combination of strategies.
        
        This method first tries paragraph-based segmentation, then falls back
        to sentence-based for long paragraphs.
        
        Args:
            text: Input text to segment
            
        Returns:
            List of dictionaries containing segment information
        """
        # First check if text has clear paragraph structure
        if '\n\n' in text or '\n\r\n' in text:
            return self.segment_by_paragraphs(text)
        else:
            return self.segment_by_sentences(text)
    
    def get_segments_with_metadata(self, text: str, strategy: str = "adaptive") -> Dict[str, Any]:
        """
        Get segments with comprehensive metadata.
        
        Args:
            text: Input text to segment
            strategy: Segmentation strategy ("sentences", "paragraphs", "adaptive")
            
        Returns:
            Dictionary containing segments and metadata
        """
        if strategy == "sentences":
            segments = self.segment_by_sentences(text)
        elif strategy == "paragraphs":
            segments = self.segment_by_paragraphs(text)
        else:
            segments = self.segment_adaptive(text)
        
        return {
            "segments": segments,
            "total_segments": len(segments),
            "total_length": len(text),
            "strategy_used": strategy,
            "metadata": {
                "max_chunk_size": self.max_chunk_size,
                "average_segment_length": sum(s["length"] for s in segments) / len(segments) if segments else 0
            }
        }
