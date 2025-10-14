"""
Tests for Haptics Emulator Module
"""

import json
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holo.sensory.haptics_emulator import (  # noqa: E402
    HapticsEmulator,
    HapticPattern,
    HapticIntensity,
)


class TestHapticsEmulator:
    """Test cases for HapticsEmulator class."""

    def test_initialization(self):
        """Test emulator initialization."""
        emulator = HapticsEmulator()
        assert emulator.patterns is not None
        assert len(emulator.patterns) > 0
        assert emulator.custom_patterns == {}

    def test_get_pattern_predefined(self):
        """Test getting predefined pattern."""
        emulator = HapticsEmulator()

        pattern = emulator.get_pattern(HapticPattern.HEARTBEAT.value)

        assert pattern is not None
        assert "name" in pattern
        assert "events" in pattern
        assert len(pattern["events"]) > 0

    def test_get_pattern_nonexistent(self):
        """Test getting nonexistent pattern returns None."""
        emulator = HapticsEmulator()

        pattern = emulator.get_pattern("nonexistent_pattern")

        assert pattern is None

    def test_all_predefined_patterns_exist(self):
        """Test that all predefined patterns are available."""
        emulator = HapticsEmulator()

        for pattern_enum in HapticPattern:
            pattern = emulator.get_pattern(pattern_enum.value)
            assert pattern is not None
            assert "events" in pattern

    def test_create_custom_pattern(self):
        """Test creating a custom pattern."""
        emulator = HapticsEmulator()

        events = [
            {"time": 0, "intensity": 0.5, "duration": 100},
            {"time": 200, "intensity": 0.7, "duration": 150},
        ]

        pattern = emulator.create_custom_pattern(
            name="test_pattern",
            events=events,
            description="Test pattern",
            repeat=True,
            repeat_interval=500,
        )

        assert pattern["name"] == "test_pattern"
        assert pattern["events"] == events
        assert pattern["repeat"] is True
        assert pattern["repeat_interval"] == 500

    def test_get_custom_pattern(self):
        """Test retrieving a custom pattern."""
        emulator = HapticsEmulator()

        events = [{"time": 0, "intensity": 0.5, "duration": 100}]
        emulator.create_custom_pattern("my_pattern", events)

        pattern = emulator.get_pattern("my_pattern")

        assert pattern is not None
        assert pattern["name"] == "my_pattern"

    def test_generate_from_text_basic(self):
        """Test generating pattern from text."""
        emulator = HapticsEmulator()

        text = "Hello. How are you? I'm fine!"
        pattern = emulator.generate_from_text(text)

        assert pattern is not None
        assert "events" in pattern
        assert len(pattern["events"]) > 0  # Should have events for punctuation
        assert pattern["repeat"] is False

    def test_generate_from_text_no_punctuation(self):
        """Test generating pattern from text without punctuation."""
        emulator = HapticsEmulator()

        text = "Hello world"
        pattern = emulator.generate_from_text(text)

        assert pattern is not None
        assert "events" in pattern
        assert len(pattern["events"]) == 0  # No punctuation, no events

    def test_generate_from_text_chinese(self):
        """Test generating pattern from Chinese text."""
        emulator = HapticsEmulator()

        text = "你好。你好嗎？我很好！"
        pattern = emulator.generate_from_text(text)

        assert pattern is not None
        assert "events" in pattern
        assert len(pattern["events"]) == 3  # Three Chinese punctuation marks

    def test_generate_from_emotion_happy(self):
        """Test generating pattern from happy emotion."""
        emulator = HapticsEmulator()

        pattern = emulator.generate_from_emotion("happy", intensity=0.7)

        assert pattern is not None
        assert "events" in pattern
        assert len(pattern["events"]) > 0
        assert "happy" in pattern["name"]

    def test_generate_from_emotion_all_types(self):
        """Test generating patterns for all emotion types."""
        emulator = HapticsEmulator()

        emotions = ["happy", "sad", "excited", "calm", "tense", "surprised"]

        for emotion in emotions:
            pattern = emulator.generate_from_emotion(emotion)
            assert pattern is not None
            assert "events" in pattern
            assert len(pattern["events"]) > 0

    def test_generate_from_emotion_unknown(self):
        """Test generating pattern from unknown emotion."""
        emulator = HapticsEmulator()

        pattern = emulator.generate_from_emotion("unknown_emotion")

        # Should fall back to calm pattern
        assert pattern is not None
        assert "events" in pattern

    def test_generate_from_emotion_intensity_scaling(self):
        """Test that emotion intensity scales appropriately."""
        emulator = HapticsEmulator()

        pattern_low = emulator.generate_from_emotion("excited", intensity=0.3)
        pattern_high = emulator.generate_from_emotion("excited", intensity=0.9)

        # Check that high intensity pattern has higher intensity values
        avg_intensity_low = sum(e["intensity"] for e in pattern_low["events"]) / len(
            pattern_low["events"]
        )
        avg_intensity_high = sum(e["intensity"] for e in pattern_high["events"]) / len(
            pattern_high["events"]
        )

        assert avg_intensity_high > avg_intensity_low

    def test_get_all_patterns(self):
        """Test getting all patterns."""
        emulator = HapticsEmulator()

        # Add a custom pattern
        emulator.create_custom_pattern(
            "custom", [{"time": 0, "intensity": 0.5, "duration": 100}]
        )

        all_patterns = emulator.get_all_patterns()

        assert len(all_patterns) > len(emulator.patterns)
        assert "custom" in all_patterns

    def test_export_pattern(self):
        """Test exporting pattern as JSON."""
        emulator = HapticsEmulator()

        json_str = emulator.export_pattern(HapticPattern.HEARTBEAT.value)

        assert json_str != "{}"

        # Verify it's valid JSON
        pattern_dict = json.loads(json_str)
        assert "events" in pattern_dict

    def test_export_nonexistent_pattern(self):
        """Test exporting nonexistent pattern."""
        emulator = HapticsEmulator()

        json_str = emulator.export_pattern("nonexistent")

        assert json_str == "{}"

    def test_validate_pattern_valid(self):
        """Test validating a valid pattern."""
        emulator = HapticsEmulator()

        valid_pattern = {
            "name": "test",
            "events": [{"time": 0, "intensity": 0.5, "duration": 100}],
        }

        assert emulator.validate_pattern(valid_pattern) is True

    def test_validate_pattern_missing_fields(self):
        """Test validating pattern with missing fields."""
        emulator = HapticsEmulator()

        invalid_pattern = {
            "name": "test"
            # Missing "events" field
        }

        assert emulator.validate_pattern(invalid_pattern) is False

    def test_validate_pattern_invalid_intensity(self):
        """Test validating pattern with invalid intensity."""
        emulator = HapticsEmulator()

        invalid_pattern = {
            "name": "test",
            "events": [
                {"time": 0, "intensity": 1.5, "duration": 100}  # Intensity > 1.0
            ],
        }

        assert emulator.validate_pattern(invalid_pattern) is False

    def test_validate_pattern_negative_values(self):
        """Test validating pattern with negative values."""
        emulator = HapticsEmulator()

        invalid_pattern = {
            "name": "test",
            "events": [{"time": -10, "intensity": 0.5, "duration": 100}],
        }

        assert emulator.validate_pattern(invalid_pattern) is False

    def test_haptic_intensity_enum(self):
        """Test HapticIntensity enum values."""
        assert HapticIntensity.LIGHT.value == 0.3
        assert HapticIntensity.MEDIUM.value == 0.6
        assert HapticIntensity.STRONG.value == 1.0
