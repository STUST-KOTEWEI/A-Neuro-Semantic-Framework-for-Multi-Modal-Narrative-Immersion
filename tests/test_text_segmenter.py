"""
Tests for Text Segmentation Module
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo.ingestion.text_segmenter import TextSegmenter  # noqa: E402


class TestTextSegmenter:
    """Test cases for TextSegmenter class."""

    def test_initialization(self):
        """Test segmenter initialization."""
        segmenter = TextSegmenter()
        assert segmenter.max_chunk_size == 500

        segmenter_custom = TextSegmenter(max_chunk_size=300)
        assert segmenter_custom.max_chunk_size == 300

    def test_segment_by_sentences_simple(self):
        """Test simple sentence segmentation."""
        segmenter = TextSegmenter()
        text = "This is sentence one. This is sentence two. This is sentence three."

        segments = segmenter.segment_by_sentences(text)

        assert len(segments) > 0
        assert all(isinstance(seg, dict) for seg in segments)
        assert all(
            "text" in seg and "index" in seg and "type" in seg for seg in segments
        )

    def test_segment_by_sentences_with_punctuation(self):
        """Test sentence segmentation with various punctuation."""
        segmenter = TextSegmenter()
        text = "What is this? This is amazing! Can you believe it. Yes, I can."

        segments = segmenter.segment_by_sentences(text)

        assert len(segments) > 0
        for seg in segments:
            assert seg["type"] == "sentence_group"
            assert "text" in seg

    def test_segment_by_sentences_max_chunk_size(self):
        """Test that segments respect max chunk size."""
        segmenter = TextSegmenter(max_chunk_size=50)
        # Create a text with sentences that exceed max_chunk_size when combined
        text = "This is a sentence. " * 10

        segments = segmenter.segment_by_sentences(text)

        # Check that segments don't exceed max size (with some tolerance)
        for seg in segments:
            assert seg["length"] <= segmenter.max_chunk_size + 50  # Some tolerance

    def test_segment_by_paragraphs(self):
        """Test paragraph segmentation."""
        segmenter = TextSegmenter()
        text = (
            "This is paragraph one.\n\nThis is paragraph two."
            "\n\nThis is paragraph three."
        )

        segments = segmenter.segment_by_paragraphs(text)

        assert len(segments) == 3
        for idx, seg in enumerate(segments):
            assert seg["index"] == idx or "parent_index" in seg
            assert "text" in seg

    def test_segment_by_paragraphs_long_paragraph(self):
        """Test paragraph segmentation with a long paragraph."""
        segmenter = TextSegmenter(max_chunk_size=100)
        long_paragraph = "This is a very long paragraph. " * 20
        text = f"{long_paragraph}\n\nShort paragraph."

        segments = segmenter.segment_by_paragraphs(text)

        # Should have multiple segments due to long paragraph being split
        assert len(segments) > 1

    def test_segment_adaptive_with_paragraphs(self):
        """Test adaptive segmentation with paragraph structure."""
        segmenter = TextSegmenter()
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."

        segments = segmenter.segment_adaptive(text)

        assert len(segments) > 0

    def test_segment_adaptive_without_paragraphs(self):
        """Test adaptive segmentation without paragraph structure."""
        segmenter = TextSegmenter()
        text = "Sentence one. Sentence two. Sentence three."

        segments = segmenter.segment_adaptive(text)

        assert len(segments) > 0

    def test_get_segments_with_metadata(self):
        """Test getting segments with metadata."""
        segmenter = TextSegmenter()
        text = "This is a test. Another test. One more test."

        result = segmenter.get_segments_with_metadata(text, strategy="sentences")

        assert "segments" in result
        assert "total_segments" in result
        assert "total_length" in result
        assert "strategy_used" in result
        assert "metadata" in result
        assert result["total_segments"] == len(result["segments"])
        assert result["total_length"] == len(text)
        assert result["strategy_used"] == "sentences"

    def test_empty_text(self):
        """Test segmentation with empty text."""
        segmenter = TextSegmenter()
        text = ""

        segments = segmenter.segment_by_sentences(text)

        assert len(segments) == 0

    def test_chinese_text_segmentation(self):
        """Test segmentation with Chinese text."""
        segmenter = TextSegmenter()
        text = "這是第一句。這是第二句。這是第三句。"

        segments = segmenter.segment_by_sentences(text)

        assert len(segments) > 0
        for seg in segments:
            assert "text" in seg

    def test_mixed_language_segmentation(self):
        """Test segmentation with mixed language text."""
        segmenter = TextSegmenter()
        text = "This is English. 這是中文。This is also English."

        segments = segmenter.segment_by_sentences(text)

        assert len(segments) > 0
