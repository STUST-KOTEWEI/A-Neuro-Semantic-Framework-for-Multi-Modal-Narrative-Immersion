"""
整合層 - 連接所有子系統
協調四個子系統的運作
"""
from typing import Dict, Any, Optional, List
from .image_recognition import OCRProcessor, ImageClassifier
from .content_generation import ScriptGenerator, SummaryGenerator, BookDataEnricher
from .sensory.subtitle_generator import SubtitleGenerator
from .sensory.image_generator import ImageGenerator
from .sensory.music_generator import MusicGenerator
from .ui_control import AccessibilityManager, PersonalizationManager


class AIReaderIntegration:
    """
    AI Reader 整合系統
    整合四個子系統：
    1. Image Recognition (圖像識別)
    2. AI Content Generation (內容生成)
    3. Multi-sensory Output (多感官輸出)
    4. UI & Control (使用者介面控制)
    """
    
    def __init__(self):
        """初始化整合系統"""
        # 子系統1: Image Recognition
        self.ocr_processor = OCRProcessor()
        self.image_classifier = ImageClassifier()
        
        # 子系統2: AI Content Generation
        self.script_generator = ScriptGenerator()
        self.summary_generator = SummaryGenerator()
        self.book_enricher = BookDataEnricher()
        
        # 子系統3: Multi-sensory Output
        self.subtitle_generator = SubtitleGenerator()
        self.image_generator = ImageGenerator()
        self.music_generator = MusicGenerator()
        
        # 子系統4: UI & Control
        self.accessibility_manager = AccessibilityManager()
        self.personalization_manager = PersonalizationManager()
        
    def process_book_scan(
        self,
        image_data: bytes,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        處理書籍掃描的完整流程
        
        Args:
            image_data: 書籍封面圖像數據
            user_profile: 使用者配置
            
        Returns:
            完整處理結果
        """
        # 1. 圖像識別 - 提取文字和分類
        ocr_result = self.ocr_processor.extract_text(image_data)
        classification = self.image_classifier.classify_image(image_data)
        book_detection = self.image_classifier.detect_book_cover(image_data)
        
        book_title = ocr_result.get('text', '')
        
        # 2. 內容生成 - 擴充書籍資料
        enriched_data = self.book_enricher.enrich_book_data(book_title)
        
        return {
            'ocr_result': ocr_result,
            'classification': classification,
            'book_detection': book_detection,
            'enriched_data': enriched_data,
            'status': 'success'
        }
    
    def generate_immersive_experience(
        self,
        content: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成完整的沉浸式體驗
        
        Args:
            content: 書籍內容或文本
            user_profile: 使用者配置
            
        Returns:
            包含所有輸出的體驗資料
        """
        if user_profile is None:
            user_profile = {}
        
        # 獲取個人化設定
        language = user_profile.get('language', 'zh-TW')
        
        # 2. 內容生成
        podcast_script = self.script_generator.generate_podcast_script(
            content,
            language=language
        )
        summary = self.summary_generator.generate_summary(
            content,
            language=language
        )
        
        # 3. 多感官輸出
        # 生成字幕
        subtitles = self.subtitle_generator.generate_subtitles(
            podcast_script['script'],
            audio_duration=podcast_script['metadata']['estimated_duration'] * 60
        )
        
        # 生成配圖
        illustrations = self.image_generator.generate_scene_illustration(
            content[:200]  # 使用前200字生成場景
        )
        
        # 生成背景音樂
        emotions = self.music_generator.analyze_emotion_from_text(content)
        dominant_mood = max(emotions, key=emotions.get)
        background_music = self.music_generator.generate_background_music(
            mood=dominant_mood
        )
        
        return {
            'content_generation': {
                'podcast_script': podcast_script,
                'summary': summary
            },
            'multi_sensory': {
                'subtitles': subtitles,
                'illustrations': illustrations,
                'background_music': background_music
            },
            'metadata': {
                'language': language,
                'processing_complete': True
            }
        }
    
    def apply_accessibility_features(
        self,
        content: Dict[str, Any],
        accessibility_needs: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        應用無障礙功能
        
        Args:
            content: 內容資料
            accessibility_needs: 無障礙需求
            
        Returns:
            應用無障礙功能後的內容
        """
        # 啟用所需的無障礙功能
        for feature, enabled in accessibility_needs.items():
            if enabled:
                self.accessibility_manager.enable_feature(feature)
        
        # 添加ARIA屬性和鍵盤快捷鍵資訊
        content['accessibility'] = {
            'features_enabled': self.accessibility_manager.features,
            'keyboard_shortcuts': self.accessibility_manager.get_keyboard_shortcuts(),
            'aria_support': True
        }
        
        return content
    
    def get_subsystem_status(self) -> Dict[str, Any]:
        """
        獲取所有子系統的狀態
        
        Returns:
            子系統狀態報告
        """
        return {
            'image_recognition': {
                'ocr_processor': 'active',
                'image_classifier': 'active',
                'supported_languages': self.ocr_processor.supported_languages
            },
            'content_generation': {
                'script_generator': 'active',
                'summary_generator': 'active',
                'book_enricher': 'active'
            },
            'multi_sensory_output': {
                'subtitle_generator': 'active',
                'image_generator': 'active',
                'music_generator': 'active'
            },
            'ui_control': {
                'accessibility_manager': 'active',
                'personalization_manager': 'active'
            }
        }
