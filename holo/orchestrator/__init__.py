"""
MultisensoryReader-Orchestrator Module
Orchestrates text -> segments -> TTS -> haptics/scent workflow
"""
from .orchestrator import Orchestrator
from .agents.base_agent import BaseAgent
from .agents.reader_agent import ReaderAgent
from .agents.emotion_agent import EmotionAgent
from .agents.device_agent import DeviceAgent
from .agents.memory_agent import MemoryAgent

__all__ = [
    'Orchestrator',
    'BaseAgent',
    'ReaderAgent',
    'EmotionAgent',
    'DeviceAgent',
    'MemoryAgent',
]
