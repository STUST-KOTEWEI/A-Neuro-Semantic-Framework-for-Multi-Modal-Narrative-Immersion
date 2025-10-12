"""
UI & Control Subsystem
目標：提供使用者介面控制，支援掃描、播放與互動
強調無障礙設計與個人化設定
"""
from .accessibility import AccessibilityManager
from .personalization import PersonalizationManager

__all__ = ['AccessibilityManager', 'PersonalizationManager']
