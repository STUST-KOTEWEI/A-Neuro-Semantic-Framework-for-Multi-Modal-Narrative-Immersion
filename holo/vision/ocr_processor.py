# PaddleOCR 整合模組
# 用於從圖片中提取文字，支持多語言和模糊影像

from typing import Dict, Any, List, Optional
import numpy as np

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False


class OCRProcessor:
    """
    OCR 處理器，使用 PaddleOCR
    支持多語言文字識別和模糊圖像處理
    """
    
    def __init__(self, lang: str = 'ch', use_angle_cls: bool = True):
        """
        初始化 OCR 處理器
        
        Args:
            lang: 語言代碼 ('ch' 中文, 'en' 英文, 等)
            use_angle_cls: 是否使用角度分類器
        """
        self.lang = lang
        self.use_angle_cls = use_angle_cls
        
        if PADDLE_AVAILABLE:
            try:
                self.ocr = PaddleOCR(
                    use_angle_cls=use_angle_cls,
                    lang=lang,
                    show_log=False
                )
            except Exception as e:
                print(f"警告：無法初始化 PaddleOCR：{e}")
                self.ocr = None
        else:
            self.ocr = None
    
    def extract_text(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        從圖片中提取文字
        
        Args:
            image_bytes: 圖片的字節數據
            
        Returns:
            包含提取文字和位置信息的字典
        """
        if not self.ocr:
            return self._mock_extraction()
        
        try:
            # 將字節轉換為 numpy 數組
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # 執行 OCR
            result = self.ocr.ocr(img, cls=self.use_angle_cls)
            
            # 解析結果
            extracted_texts = []
            full_text = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        box = line[0]  # 位置信息
                        text_info = line[1]  # 文字和置信度
                        
                        extracted_texts.append({
                            'text': text_info[0],
                            'confidence': float(text_info[1]),
                            'position': {
                                'top_left': box[0],
                                'top_right': box[1],
                                'bottom_right': box[2],
                                'bottom_left': box[3]
                            }
                        })
                        full_text.append(text_info[0])
            
            return {
                'texts': extracted_texts,
                'full_text': ' '.join(full_text),
                'success': True,
                'language': self.lang
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def extract_text_from_file(self, image_path: str) -> Dict[str, Any]:
        """
        從圖片文件中提取文字
        
        Args:
            image_path: 圖片文件路徑
            
        Returns:
            包含提取文字和位置信息的字典
        """
        if not self.ocr:
            return self._mock_extraction()
        
        try:
            result = self.ocr.ocr(image_path, cls=self.use_angle_cls)
            
            extracted_texts = []
            full_text = []
            
            if result and result[0]:
                for line in result[0]:
                    if line:
                        box = line[0]
                        text_info = line[1]
                        
                        extracted_texts.append({
                            'text': text_info[0],
                            'confidence': float(text_info[1]),
                            'position': {
                                'top_left': box[0],
                                'top_right': box[1],
                                'bottom_right': box[2],
                                'bottom_left': box[3]
                            }
                        })
                        full_text.append(text_info[0])
            
            return {
                'texts': extracted_texts,
                'full_text': ' '.join(full_text),
                'success': True,
                'language': self.lang
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _mock_extraction(self) -> Dict[str, Any]:
        """模擬文字提取結果（當 PaddleOCR 不可用時）"""
        return {
            'texts': [
                {
                    'text': '這是示例文字',
                    'confidence': 0.95,
                    'position': {
                        'top_left': [10, 10],
                        'top_right': [100, 10],
                        'bottom_right': [100, 50],
                        'bottom_left': [10, 50]
                    }
                }
            ],
            'full_text': '這是示例文字',
            'success': True,
            'language': self.lang,
            'mock': True
        }
