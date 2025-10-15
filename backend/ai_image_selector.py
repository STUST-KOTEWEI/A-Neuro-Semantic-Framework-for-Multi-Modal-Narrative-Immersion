"""
AI Image Selector Module

Selects appropriate images based on emotion analysis and text content.
Integrates with local image database and Google API for additional generation.
"""

import json
import os
import random
from typing import List, Dict, Any, Optional
import requests
from pathlib import Path


class AIImageSelector:
    """
    Selects and manages AI-generated images based on emotional context.
    """
    
    def __init__(self, db_path: str = "backend/db/images.json"):
        """
        Initialize the image selector.
        
        Args:
            db_path: Path to the images database JSON file
        """
        self.db_path = db_path
        self.images_db = self._load_images_db()
        
    def _load_images_db(self) -> List[Dict[str, Any]]:
        """Load images database from JSON file."""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: Images database not found at {self.db_path}")
                return []
        except Exception as e:
            print(f"Error loading images database: {e}")
            return []
    
    def get_images_by_emotion(
        self, 
        emotion: str, 
        intensity: Optional[float] = None,
        count: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get images matching a specific emotion.
        
        Args:
            emotion: Target emotion (e.g., 'happy', 'sad', 'fear')
            intensity: Optional intensity filter (0.0-1.0)
            count: Number of images to return
            
        Returns:
            List of image dictionaries
        """
        matching_images = [
            img for img in self.images_db 
            if img.get('emotion', '').lower() == emotion.lower()
        ]
        
        # Filter by intensity if specified
        if intensity is not None:
            tolerance = 0.2  # Allow some variance
            matching_images = [
                img for img in matching_images
                if abs(img.get('intensity', 0.5) - intensity) <= tolerance
            ]
        
        # Randomly select from matching images
        if matching_images:
            selected = random.sample(
                matching_images, 
                min(count, len(matching_images))
            )
            return selected
        
        return []
    
    def get_images_by_tags(
        self, 
        tags: List[str], 
        count: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get images that match any of the specified tags.
        
        Args:
            tags: List of tags to match
            count: Number of images to return
            
        Returns:
            List of image dictionaries
        """
        matching_images = []
        
        for img in self.images_db:
            img_tags = img.get('tags', [])
            if any(tag.lower() in [t.lower() for t in img_tags] for tag in tags):
                matching_images.append(img)
        
        if matching_images:
            selected = random.sample(
                matching_images, 
                min(count, len(matching_images))
            )
            return selected
        
        return []
    
    def analyze_text_emotion(self, text: str) -> Dict[str, Any]:
        """
        Analyze text to determine primary emotion and intensity.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with emotion, intensity, and keywords
        """
        # Simple keyword-based emotion detection
        # In production, this would use a proper sentiment analysis model
        
        emotion_keywords = {
            'happy': ['happy', 'joy', 'glad', 'cheerful', 'bright', 'sunny', 'laugh', 'smile', 'celebration'],
            'sad': ['sad', 'cry', 'tears', 'sorrow', 'grief', 'lonely', 'empty', 'loss', 'melancholy'],
            'fear': ['fear', 'scared', 'afraid', 'terror', 'horror', 'panic', 'dread', 'frightened'],
            'anger': ['angry', 'rage', 'fury', 'mad', 'livid', 'furious', 'outraged', 'violent'],
            'surprise': ['surprise', 'shocked', 'amazed', 'astonished', 'unexpected', 'sudden'],
            'disgust': ['disgust', 'revolting', 'sick', 'nausea', 'repulsive', 'vile'],
            'love': ['love', 'adore', 'cherish', 'romantic', 'affection', 'heart', 'beloved'],
            'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'quiet', 'still', 'relaxed'],
            'excitement': ['excited', 'thrilled', 'energetic', 'enthusiastic', 'pumped'],
            'curiosity': ['curious', 'wonder', 'explore', 'discover', 'investigate', 'mystery']
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            # Simple intensity calculation based on keyword density
            intensity = min(1.0, emotion_scores[primary_emotion] / 3.0)
            
            return {
                'emotion': primary_emotion,
                'intensity': intensity,
                'keywords': [k for k in emotion_keywords[primary_emotion] if k in text_lower]
            }
        
        # Default to calm if no strong emotion detected
        return {
            'emotion': 'calm',
            'intensity': 0.5,
            'keywords': []
        }
    
    def select_images_for_text(
        self, 
        text: str, 
        count: int = 3
    ) -> Dict[str, Any]:
        """
        Select appropriate images for a given text.
        
        Args:
            text: Input text to analyze
            count: Number of images to select
            
        Returns:
            Dictionary with emotion analysis and selected images
        """
        emotion_analysis = self.analyze_text_emotion(text)
        
        # Get images based on detected emotion
        primary_images = self.get_images_by_emotion(
            emotion_analysis['emotion'],
            emotion_analysis['intensity'],
            count
        )
        
        # If not enough images found, get more from similar emotions
        if len(primary_images) < count:
            additional_needed = count - len(primary_images)
            
            # Try related emotions or tags
            if emotion_analysis['keywords']:
                additional_images = self.get_images_by_tags(
                    emotion_analysis['keywords'],
                    additional_needed
                )
                primary_images.extend(additional_images)
        
        return {
            'emotion_analysis': emotion_analysis,
            'selected_images': primary_images[:count],
            'total_available': len(self.images_db)
        }
    
    def add_image_to_db(self, image_data: Dict[str, Any]) -> bool:
        """
        Add a new image to the database.
        
        Args:
            image_data: Image information dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.images_db.append(image_data)
            self._save_images_db()
            return True
        except Exception as e:
            print(f"Error adding image to database: {e}")
            return False
    
    def _save_images_db(self) -> None:
        """Save the current images database to file."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.images_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving images database: {e}")
    
    def get_emotion_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available emotions and images.
        
        Returns:
            Dictionary with emotion counts and statistics
        """
        emotion_counts = {}
        total_images = len(self.images_db)
        
        for img in self.images_db:
            emotion = img.get('emotion', 'unknown')
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return {
            'total_images': total_images,
            'emotion_counts': emotion_counts,
            'available_emotions': list(emotion_counts.keys())
        }


# Example usage and testing
if __name__ == "__main__":
    selector = AIImageSelector()
    
    # Test emotion analysis
    test_texts = [
        "The old house creaked in the wind, its windows rattling like bones.",
        "Children were laughing and playing in the sunny garden.",
        "She felt a deep sadness as the rain began to fall.",
        "The surprise party was amazing with everyone jumping out!"
    ]
    
    for text in test_texts:
        result = selector.select_images_for_text(text, count=2)
        print(f"\nText: {text}")
        print(f"Detected emotion: {result['emotion_analysis']['emotion']}")
        print(f"Intensity: {result['emotion_analysis']['intensity']:.2f}")
        print(f"Selected images: {len(result['selected_images'])}")
        for img in result['selected_images']:
            print(f"  - {img['id']}: {img['description']}")
    
    # Print statistics
    stats = selector.get_emotion_statistics()
    print(f"\nDatabase Statistics:")
    print(f"Total images: {stats['total_images']}")
    print(f"Available emotions: {', '.join(stats['available_emotions'])}")