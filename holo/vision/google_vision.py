# Google Vision API 整合模組
# 用於影像情緒檢測和標籤識別

from typing import Dict, Any, List, Optional
import base64
import os

try:
    from google.cloud import vision
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class GoogleVisionAnalyzer:
    """
    Google Vision API 分析器
    用於檢測圖片中的情緒、標籤、文字等
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        初始化 Google Vision 分析器
        
        Args:
            credentials_path: Google Cloud 憑證檔案路徑
        """
        self.credentials_path = credentials_path
        if credentials_path and os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        if VISION_AVAILABLE:
            try:
                self.client = vision.ImageAnnotatorClient()
            except Exception as e:
                print(f"警告：無法初始化 Google Vision 客戶端：{e}")
                self.client = None
        else:
            self.client = None
    
    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        分析圖片並返回檢測結果
        
        Args:
            image_bytes: 圖片的字節數據
            
        Returns:
            包含情緒、標籤、文字等分析結果的字典
        """
        if not self.client:
            return self._mock_analysis()
        
        try:
            image = vision.Image(content=image_bytes)
            
            # 進行多種檢測
            face_response = self.client.face_detection(image=image)
            label_response = self.client.label_detection(image=image)
            text_response = self.client.text_detection(image=image)
            
            # 處理面部情緒檢測
            emotions = self._extract_emotions(face_response.face_annotations)
            
            # 處理標籤檢測
            labels = self._extract_labels(label_response.label_annotations)
            
            # 處理文字檢測
            texts = self._extract_texts(text_response.text_annotations)
            
            return {
                'emotions': emotions,
                'labels': labels,
                'texts': texts,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _extract_emotions(self, face_annotations: List) -> List[Dict[str, Any]]:
        """提取面部情緒信息"""
        emotions = []
        
        for face in face_annotations:
            emotion_data = {
                'joy': self._likelihood_to_score(face.joy_likelihood),
                'sorrow': self._likelihood_to_score(face.sorrow_likelihood),
                'anger': self._likelihood_to_score(face.anger_likelihood),
                'surprise': self._likelihood_to_score(face.surprise_likelihood),
                'confidence': face.detection_confidence
            }
            emotions.append(emotion_data)
        
        return emotions
    
    def _extract_labels(self, label_annotations: List) -> List[Dict[str, Any]]:
        """提取圖片標籤"""
        labels = []
        
        for label in label_annotations:
            labels.append({
                'description': label.description,
                'score': label.score
            })
        
        return labels
    
    def _extract_texts(self, text_annotations: List) -> List[str]:
        """提取圖片中的文字"""
        texts = []
        
        if text_annotations:
            # 第一個元素通常是完整文本
            texts.append(text_annotations[0].description if text_annotations else '')
        
        return texts
    
    def _likelihood_to_score(self, likelihood) -> float:
        """將可能性等級轉換為分數"""
        likelihood_map = {
            0: 0.0,  # UNKNOWN
            1: 0.1,  # VERY_UNLIKELY
            2: 0.3,  # UNLIKELY
            3: 0.5,  # POSSIBLE
            4: 0.7,  # LIKELY
            5: 0.9   # VERY_LIKELY
        }
        return likelihood_map.get(likelihood, 0.0)
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """模擬分析結果（當 API 不可用時）"""
        return {
            'emotions': [{
                'joy': 0.8,
                'sorrow': 0.1,
                'anger': 0.05,
                'surprise': 0.3,
                'confidence': 0.9
            }],
            'labels': [
                {'description': '人物', 'score': 0.95},
                {'description': '微笑', 'score': 0.87},
                {'description': '快樂', 'score': 0.82}
            ],
            'texts': ['示例文字內容'],
            'success': True,
            'mock': True
        }
