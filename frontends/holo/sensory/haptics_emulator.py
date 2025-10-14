"""
Haptics Emulator Module

Provides haptic feedback patterns for immersive narrative experiences.
Emulates various haptic patterns that can be sent to compatible devices.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
import json


class HapticIntensity(Enum):
    """Haptic feedback intensity levels."""

    LIGHT = 0.3
    MEDIUM = 0.6
    STRONG = 1.0


class HapticPattern(Enum):
    """Predefined haptic patterns."""

    HEARTBEAT = "heartbeat"
    GENTLE_PULSE = "gentle_pulse"
    SHARP_TAP = "sharp_tap"
    RUMBLE = "rumble"
    WAVE = "wave"
    BREATHE = "breathe"


class HapticsEmulator:
    """
    Haptics Emulator for generating haptic feedback patterns.

    Provides functionality to create, manage, and export haptic patterns
    that can be used with various haptic feedback devices.
    """

    def __init__(self):
        """Initialize the haptics emulator."""
        self.patterns = self._initialize_patterns()
        self.custom_patterns = {}

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize predefined haptic patterns.

        Returns:
            Dictionary of pattern definitions
        """
        return {
            HapticPattern.HEARTBEAT.value: {
                "name": "Heartbeat",
                "description": "Simulates a heartbeat rhythm",
                "events": [
                    {"time": 0, "intensity": 0.8, "duration": 100},
                    {"time": 150, "intensity": 0.6, "duration": 80},
                    {"time": 800, "intensity": 0.8, "duration": 100},
                    {"time": 950, "intensity": 0.6, "duration": 80},
                ],
                "repeat": True,
                "repeat_interval": 1000,
            },
            HapticPattern.GENTLE_PULSE.value: {
                "name": "Gentle Pulse",
                "description": "Soft, calming pulse",
                "events": [
                    {"time": 0, "intensity": 0.3, "duration": 200},
                    {"time": 300, "intensity": 0.0, "duration": 200},
                ],
                "repeat": True,
                "repeat_interval": 500,
            },
            HapticPattern.SHARP_TAP.value: {
                "name": "Sharp Tap",
                "description": "Quick, sharp tap for alerts",
                "events": [{"time": 0, "intensity": 1.0, "duration": 50}],
                "repeat": False,
            },
            HapticPattern.RUMBLE.value: {
                "name": "Rumble",
                "description": "Continuous rumbling vibration",
                "events": [
                    {"time": 0, "intensity": 0.7, "duration": 100},
                    {"time": 100, "intensity": 0.5, "duration": 100},
                    {"time": 200, "intensity": 0.7, "duration": 100},
                    {"time": 300, "intensity": 0.5, "duration": 100},
                ],
                "repeat": True,
                "repeat_interval": 400,
            },
            HapticPattern.WAVE.value: {
                "name": "Wave",
                "description": "Gradual wave-like intensity change",
                "events": [
                    {"time": 0, "intensity": 0.2, "duration": 100},
                    {"time": 100, "intensity": 0.4, "duration": 100},
                    {"time": 200, "intensity": 0.6, "duration": 100},
                    {"time": 300, "intensity": 0.8, "duration": 100},
                    {"time": 400, "intensity": 1.0, "duration": 100},
                    {"time": 500, "intensity": 0.8, "duration": 100},
                    {"time": 600, "intensity": 0.6, "duration": 100},
                    {"time": 700, "intensity": 0.4, "duration": 100},
                    {"time": 800, "intensity": 0.2, "duration": 100},
                ],
                "repeat": False,
            },
            HapticPattern.BREATHE.value: {
                "name": "Breathe",
                "description": "Breathing rhythm pattern",
                "events": [
                    {"time": 0, "intensity": 0.3, "duration": 300},
                    {"time": 300, "intensity": 0.5, "duration": 300},
                    {"time": 600, "intensity": 0.7, "duration": 300},
                    {"time": 900, "intensity": 0.5, "duration": 300},
                    {"time": 1200, "intensity": 0.3, "duration": 300},
                    {"time": 1500, "intensity": 0.0, "duration": 500},
                ],
                "repeat": True,
                "repeat_interval": 2000,
            },
        }

    def get_pattern(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a haptic pattern by name.

        Args:
            pattern_name: Name of the pattern to retrieve

        Returns:
            Pattern definition or None if not found
        """
        if pattern_name in self.patterns:
            return self.patterns[pattern_name].copy()
        elif pattern_name in self.custom_patterns:
            return self.custom_patterns[pattern_name].copy()
        return None

    def create_custom_pattern(
        self,
        name: str,
        events: List[Dict[str, Any]],
        description: str = "",
        repeat: bool = False,
        repeat_interval: int = 1000,
    ) -> Dict[str, Any]:
        """
        Create a custom haptic pattern.

        Args:
            name: Name for the custom pattern
            events: List of haptic events (time, intensity, duration)
            description: Optional description
            repeat: Whether pattern should repeat
            repeat_interval: Interval between repeats in milliseconds

        Returns:
            Created pattern definition
        """
        pattern = {
            "name": name,
            "description": description,
            "events": events,
            "repeat": repeat,
            "repeat_interval": repeat_interval,
        }

        self.custom_patterns[name] = pattern
        return pattern

    def generate_from_text(self, text: str) -> Dict[str, Any]:
        """
        Generate haptic patterns from text punctuation.

        Maps punctuation to haptic feedback:
        - Period (.): Light tap
        - Exclamation (!): Sharp tap
        - Question (?): Medium pulse
        - Comma (,): Very light tap
        - Ellipsis (...): Gentle wave

        Args:
            text: Input text to analyze

        Returns:
            Generated haptic pattern
        """
        events = []
        time = 0

        for char in text:
            if char == ".":
                events.append({"time": time, "intensity": 0.4, "duration": 100})
                time += 150
            elif char == "!":
                events.append({"time": time, "intensity": 0.9, "duration": 80})
                time += 120
            elif char == "?":
                events.append({"time": time, "intensity": 0.6, "duration": 120})
                time += 150
            elif char == ",":
                events.append({"time": time, "intensity": 0.2, "duration": 60})
                time += 80
            elif char in ["。", "！", "？", "，"]:  # Chinese punctuation
                intensity_map = {"。": 0.4, "！": 0.9, "？": 0.6, "，": 0.2}
                events.append(
                    {"time": time, "intensity": intensity_map[char], "duration": 100}
                )
                time += 120

        return {
            "name": "text_generated",
            "description": f"Generated from text: {text[:50]}...",
            "events": events,
            "repeat": False,
        }

    def generate_from_emotion(
        self, emotion: str, intensity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Generate haptic pattern based on emotion.

        Args:
            emotion: Emotion type (happy, sad, excited, calm, tense, etc.)
            intensity: Intensity of the emotion (0.0-1.0)

        Returns:
            Generated haptic pattern
        """
        emotion = emotion.lower()

        emotion_patterns = {
            "happy": {
                "base_pattern": HapticPattern.GENTLE_PULSE.value,
                "intensity_multiplier": 1.2,
            },
            "sad": {
                "base_pattern": HapticPattern.BREATHE.value,
                "intensity_multiplier": 0.6,
            },
            "excited": {
                "base_pattern": HapticPattern.HEARTBEAT.value,
                "intensity_multiplier": 1.5,
            },
            "calm": {
                "base_pattern": HapticPattern.GENTLE_PULSE.value,
                "intensity_multiplier": 0.7,
            },
            "tense": {
                "base_pattern": HapticPattern.RUMBLE.value,
                "intensity_multiplier": 1.3,
            },
            "surprised": {
                "base_pattern": HapticPattern.SHARP_TAP.value,
                "intensity_multiplier": 1.0,
            },
        }

        if emotion not in emotion_patterns:
            # Default to calm pattern
            emotion = "calm"

        config = emotion_patterns[emotion]
        base_pattern = self.get_pattern(config["base_pattern"])

        if base_pattern:
            # Adjust intensity based on emotion intensity
            adjusted_events = []
            for event in base_pattern["events"]:
                adjusted_event = event.copy()
                adjusted_event["intensity"] = min(
                    1.0, event["intensity"] * config["intensity_multiplier"] * intensity
                )
                adjusted_events.append(adjusted_event)

            base_pattern["events"] = adjusted_events
            base_pattern["name"] = f"{emotion}_pattern"
            base_pattern["description"] = f"Haptic pattern for {emotion} emotion"

        return base_pattern

    def get_all_patterns(self) -> Dict[str, Any]:
        """
        Get all available patterns.

        Returns:
            Dictionary containing all predefined and custom patterns
        """
        all_patterns = self.patterns.copy()
        all_patterns.update(self.custom_patterns)
        return all_patterns

    def export_pattern(self, pattern_name: str) -> str:
        """
        Export pattern as JSON string.

        Args:
            pattern_name: Name of pattern to export

        Returns:
            JSON string representation of the pattern
        """
        pattern = self.get_pattern(pattern_name)
        if pattern:
            return json.dumps(pattern, indent=2)
        return "{}"

    def validate_pattern(self, pattern: Dict[str, Any]) -> bool:
        """
        Validate a haptic pattern structure.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid, False otherwise
        """
        required_fields = ["name", "events"]

        if not all(field in pattern for field in required_fields):
            return False

        if not isinstance(pattern["events"], list):
            return False

        for event in pattern["events"]:
            if not all(key in event for key in ["time", "intensity", "duration"]):
                return False
            if not (0 <= event["intensity"] <= 1.0):
                return False
            if event["time"] < 0 or event["duration"] < 0:
                return False

        return True
