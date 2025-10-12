"""
個人化管理器
管理使用者偏好設定和個人化體驗
"""
from typing import Dict, Any, Optional


class PersonalizationManager:
    """
    個人化管理器
    處理使用者偏好設定
    """
    
    def __init__(self):
        """初始化個人化管理器"""
        self.default_settings = {
            'language': 'zh-TW',
            'voice_speed': 1.0,
            'voice_gender': 'female',
            'theme': 'light',
            'font_size': 16,
            'reading_mode': 'continuous',
            'auto_play': False,
            'notification_enabled': True
        }
        self.user_settings = self.default_settings.copy()
        
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        獲取使用者配置
        
        Args:
            user_id: 使用者ID
            
        Returns:
            使用者配置資料
        """
        # 實際實作時應從資料庫載入
        return {
            'user_id': user_id,
            'settings': self.user_settings,
            'preferences': {
                'favorite_genres': ['fiction', 'science'],
                'reading_history': [],
                'bookmarks': []
            }
        }
    
    def update_setting(self, key: str, value: Any) -> bool:
        """
        更新設定
        
        Args:
            key: 設定鍵
            value: 設定值
            
        Returns:
            是否成功更新
        """
        if key in self.user_settings:
            self.user_settings[key] = value
            return True
        return False
    
    def get_setting(self, key: str) -> Optional[Any]:
        """
        獲取設定值
        
        Args:
            key: 設定鍵
            
        Returns:
            設定值
        """
        return self.user_settings.get(key)
    
    def reset_to_defaults(self):
        """重置為預設設定"""
        self.user_settings = self.default_settings.copy()
    
    def export_settings(self) -> Dict[str, Any]:
        """
        匯出設定
        
        Returns:
            設定字典
        """
        return self.user_settings.copy()
    
    def import_settings(self, settings: Dict[str, Any]) -> bool:
        """
        匯入設定
        
        Args:
            settings: 設定字典
            
        Returns:
            是否成功匯入
        """
        try:
            for key, value in settings.items():
                if key in self.default_settings:
                    self.user_settings[key] = value
            return True
        except Exception:
            return False
    
    def get_recommended_settings(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        根據使用者情境推薦設定
        
        Args:
            user_context: 使用者情境（如視力狀況、環境等）
            
        Returns:
            推薦設定
        """
        recommendations = self.default_settings.copy()
        
        # 根據情境調整推薦
        if user_context.get('visual_impairment'):
            recommendations['font_size'] = 24
            recommendations['theme'] = 'high-contrast'
            
        if user_context.get('noisy_environment'):
            recommendations['voice_speed'] = 0.9
            
        return recommendations
