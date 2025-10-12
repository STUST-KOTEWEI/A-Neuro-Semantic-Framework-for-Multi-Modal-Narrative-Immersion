"""
Image Recognition Subsystem
目標：辨識書籍封面圖像與文字，支援模糊影像、低光源、多語言OCR
"""
from .ocr_processor import OCRProcessor
from .image_classifier import ImageClassifier

__all__ = ['OCRProcessor', 'ImageClassifier']
