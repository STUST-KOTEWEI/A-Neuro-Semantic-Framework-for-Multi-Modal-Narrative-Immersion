"""
End-to-End Integration Tests for Week 1 Sprint Features

Tests the complete workflow from text input through segmentation,
TTS, and haptics generation.
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo.ingestion.text_segmenter import TextSegmenter  # noqa: E402
from holo.auditory.elevenlabs_tts import get_tts_engine  # noqa: E402
from holo.sensory.haptics_emulator import HapticsEmulator  # noqa: E402


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def setup_method(self):
        """Setup test fixtures."""
        self.segmenter = TextSegmenter()
        self.tts_engine = get_tts_engine()
        self.haptics = HapticsEmulator()
        self.sample_text = "Hello world! How are you? I'm doing great."

    def test_complete_workflow_english(self):
        """Test complete workflow with English text."""
        # Step 1: Segment the text
        segments = self.segmenter.get_segments_with_metadata(self.sample_text)

        assert segments is not None
        assert "segments" in segments
        assert segments["total_segments"] > 0

        # Step 2: Generate haptic feedback from text
        haptic_pattern = self.haptics.generate_from_text(self.sample_text)

        assert haptic_pattern is not None
        assert "events" in haptic_pattern
        assert len(haptic_pattern["events"]) > 0

        # Step 3: Verify TTS engine is available
        assert self.tts_engine.is_available()
        voices = self.tts_engine.get_available_voices()
        assert "voices" in voices

    def test_complete_workflow_chinese(self):
        """Test complete workflow with Chinese text."""
        chinese_text = "你好！你好嗎？我很好。"

        # Step 1: Segment Chinese text
        segments = self.segmenter.get_segments_with_metadata(chinese_text)

        assert segments is not None
        assert segments["total_segments"] > 0

        # Step 2: Generate haptics from Chinese punctuation
        haptic_pattern = self.haptics.generate_from_text(chinese_text)

        assert haptic_pattern is not None
        assert len(haptic_pattern["events"]) == 3  # Three punctuation marks

    def test_workflow_with_long_text(self):
        """Test workflow with longer narrative text."""
        long_text = (
            "Once upon a time, there was a young adventurer. "
            "She traveled through mystical forests and over towering mountains. "
            "Every day brought new challenges and discoveries.\n\n"
            "One fateful morning, she discovered an ancient temple. "
            "Inside, mysterious symbols glowed with an ethereal light. "
            "This would change her life forever."
        )

        # Segment the long text
        segments = self.segmenter.get_segments_with_metadata(
            long_text, strategy="adaptive"
        )

        assert segments["total_segments"] >= 1
        assert segments["strategy_used"] == "adaptive"

        # Generate haptics
        haptic_pattern = self.haptics.generate_from_text(long_text)

        # Should have multiple haptic events for multiple punctuation marks
        assert len(haptic_pattern["events"]) >= 5

    def test_workflow_with_emotion_based_haptics(self):
        """Test workflow combining text segmentation with emotion-based haptics."""
        text = "This is an exciting adventure! Let's explore the world."

        # Segment text
        segments = self.segmenter.segment_by_sentences(text)

        assert len(segments) > 0

        # Generate emotion-based haptics
        emotions = ["happy", "excited", "calm"]

        for emotion in emotions:
            pattern = self.haptics.generate_from_emotion(emotion)
            assert pattern is not None
            assert "events" in pattern
            assert emotion in pattern["name"]

    def test_workflow_with_multiple_strategies(self):
        """Test workflow using different segmentation strategies."""
        text = (
            "Paragraph one with multiple sentences. This is great."
            "\n\nParagraph two here."
        )

        strategies = ["sentences", "paragraphs", "adaptive"]

        for strategy in strategies:
            segments = self.segmenter.get_segments_with_metadata(
                text, strategy=strategy
            )

            assert segments is not None
            assert segments["strategy_used"] == strategy
            assert segments["total_segments"] > 0

    def test_haptic_pattern_consistency(self):
        """Test that haptic patterns are consistent and valid."""
        patterns_to_test = [
            ("heartbeat", None),
            ("gentle_pulse", None),
            ("sharp_tap", None),
            (None, "happy"),
            (None, "sad"),
        ]

        for pattern_name, emotion in patterns_to_test:
            if pattern_name:
                pattern = self.haptics.get_pattern(pattern_name)
            else:
                pattern = self.haptics.generate_from_emotion(emotion)

            # Validate pattern structure
            assert self.haptics.validate_pattern(pattern)

    def test_segment_and_haptic_correlation(self):
        """Test that segments and haptics can be correlated."""
        text = "First sentence. Second sentence! Third sentence?"

        # Get segments
        segments = self.segmenter.segment_by_sentences(text)

        # Get haptics
        haptics = self.haptics.generate_from_text(text)

        # Should have haptic events for punctuation
        assert len(haptics["events"]) == 3

        # Should have at least one segment
        assert len(segments) > 0

    def test_metadata_completeness(self):
        """Test that all components provide complete metadata."""
        text = "Testing metadata. Is this complete?"

        # Segmenter metadata
        seg_result = self.segmenter.get_segments_with_metadata(text)
        required_seg_fields = [
            "segments",
            "total_segments",
            "total_length",
            "strategy_used",
            "metadata",
        ]
        assert all(field in seg_result for field in required_seg_fields)

        # Haptics metadata
        haptic_pattern = self.haptics.generate_from_text(text)
        required_haptic_fields = ["name", "description", "events", "repeat"]
        assert all(field in haptic_pattern for field in required_haptic_fields)

        # TTS metadata
        voices = self.tts_engine.get_available_voices()
        assert "voices" in voices
        assert len(voices["voices"]) > 0

    def test_empty_input_handling(self):
        """Test handling of empty inputs."""
        empty_text = ""

        # Segmenter should handle empty text
        segments = self.segmenter.get_segments_with_metadata(empty_text)
        assert segments["total_segments"] == 0

        # Haptics should handle empty text
        haptics = self.haptics.generate_from_text(empty_text)
        assert len(haptics["events"]) == 0

    def test_custom_haptic_integration(self):
        """Test creating and using custom haptic patterns."""
        # Create custom pattern
        events = [
            {"time": 0, "intensity": 0.5, "duration": 100},
            {"time": 200, "intensity": 0.7, "duration": 150},
        ]

        self.haptics.create_custom_pattern(
            name="test_custom", events=events, description="Custom test pattern"
        )

        # Verify custom pattern is stored
        retrieved = self.haptics.get_pattern("test_custom")
        assert retrieved is not None
        assert retrieved["name"] == "test_custom"

        # Verify custom pattern is in all patterns list
        all_patterns = self.haptics.get_all_patterns()
        assert "test_custom" in all_patterns
