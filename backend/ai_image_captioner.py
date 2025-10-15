"""
AI Image Captioner Module

Integrates with Google Vision AI for image analysis, captioning, and emotion detection.
Also provides image generation prompt creation and visual content analysis.
"""

import os
import json
import base64
import requests
from typing import Dict, Any, List, Optional, Union
import google.generativeai as genai
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIImageCaptioner:
    """
    Handles image analysis and captioning using Google Vision AI and Gemini Vision.
    """
    
    def __init__(self, google_api_key: Optional[str] = None):
        """
        Initialize the image captioner.
        
        Args:
            google_api_key: Google Generative AI API key
        """
        self.google_api_key = google_api_key or os.getenv("GOOGLE_GENAI_API_KEY")
        
        # Initialize Google Generative AI
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.gemini_vision_model = genai.GenerativeModel('gemini-pro-vision')
        else:
            self.gemini_vision_model = None
            print("Warning: Google API key not configured")
    
    def analyze_image_with_gemini(
        self, 
        image_path: str, 
        prompt: str = "Describe this image in detail, including mood and emotional content."
    ) -> Dict[str, Any]:
        """
        Analyze an image using Google Gemini Vision.
        
        Args:
            image_path: Path to the image file
            prompt: Analysis prompt
            
        Returns:
            Dictionary with analysis results and metadata
        """
        if not self.gemini_vision_model:
            return {"error": "Google Gemini Vision not configured", "success": False}
        
        try:
            # Load and prepare image
            if not os.path.exists(image_path):
                return {"error": f"Image file not found: {image_path}", "success": False}
            
            # Read image file
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Create image object for Gemini
            image = {
                'mime_type': self._get_mime_type(image_path),
                'data': image_data
            }
            
            response = self.gemini_vision_model.generate_content([prompt, image])
            
            return {
                "description": response.text,
                "model": "gemini-pro-vision",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "prompt": prompt,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "model": "gemini-pro-vision",
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "success": False
            }
    
    def detect_emotion_in_image(
        self, 
        image_path: str
    ) -> Dict[str, Any]:
        """
        Detect emotions conveyed by an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with emotion analysis results
        """
        prompt = """
        Analyze the emotional content and mood of this image. Provide:
        1. Primary emotion conveyed (happy, sad, fear, anger, surprise, disgust, calm, love, etc.)
        2. Emotion intensity on a scale of 0.0 to 1.0
        3. Secondary emotions if present
        4. Visual elements that contribute to the emotional impact
        5. Overall mood description
        
        Format your response as JSON with the following structure:
        {
            "primary_emotion": "emotion_name",
            "intensity": 0.0-1.0,
            "secondary_emotions": ["emotion1", "emotion2"],
            "visual_elements": ["element1", "element2"],
            "mood_description": "detailed description"
        }
        """
        
        result = self.analyze_image_with_gemini(image_path, prompt)
        
        if result.get("success"):
            try:
                # Try to parse JSON from response
                description = result["description"]
                # Extract JSON part if present
                start_idx = description.find('{')
                end_idx = description.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = description[start_idx:end_idx]
                    emotion_data = json.loads(json_str)
                    result["emotion_analysis"] = emotion_data
                else:
                    # Fallback: parse manually
                    result["emotion_analysis"] = self._parse_emotion_text(description)
                    
            except json.JSONDecodeError:
                # If JSON parsing fails, provide manual parsing
                result["emotion_analysis"] = self._parse_emotion_text(result["description"])
        
        return result
    
    def generate_image_metadata(
        self, 
        image_path: str,
        include_tags: bool = True,
        include_colors: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for an image.
        
        Args:
            image_path: Path to the image file
            include_tags: Whether to generate descriptive tags
            include_colors: Whether to analyze color palette
            
        Returns:
            Dictionary with comprehensive image metadata
        """
        prompt = f"""
        Analyze this image and provide comprehensive metadata. Include:
        
        1. Basic description (what's in the image)
        2. Composition and visual style
        3. Color palette and lighting
        4. Mood and atmosphere
        5. Potential use cases for this image
        {"6. Relevant tags (10-15 descriptive keywords)" if include_tags else ""}
        {"7. Dominant colors and color scheme" if include_colors else ""}
        
        Provide detailed, structured information suitable for database storage.
        """
        
        result = self.analyze_image_with_gemini(image_path, prompt)
        
        if result.get("success"):
            # Add technical metadata
            try:
                from PIL import Image
                with Image.open(image_path) as img:
                    result["technical_metadata"] = {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode,
                        "file_size": os.path.getsize(image_path)
                    }
            except ImportError:
                result["technical_metadata"] = {
                    "file_size": os.path.getsize(image_path)
                }
        
        return result
    
    def suggest_similar_images(
        self, 
        image_path: str,
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Suggest similar images that could be generated or found.
        
        Args:
            image_path: Path to the reference image
            count: Number of suggestions to generate
            
        Returns:
            Dictionary with suggestions and metadata
        """
        prompt = f"""
        Based on this image, suggest {count} similar images that would fit well in the same collection.
        For each suggestion, provide:
        1. A detailed description suitable for AI image generation
        2. How it relates to the original image
        3. The emotional tone it would convey
        4. Specific visual elements to include
        
        Format as a numbered list with detailed descriptions.
        """
        
        result = self.analyze_image_with_gemini(image_path, prompt)
        
        if result.get("success"):
            # Parse suggestions from response
            suggestions = self._parse_suggestions(result["description"])
            result["suggestions"] = suggestions
            result["suggestion_count"] = len(suggestions)
        
        return result
    
    def create_image_generation_prompt(
        self, 
        image_path: str,
        style: str = "similar",
        modifications: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create a prompt for generating a similar image.
        
        Args:
            image_path: Path to the reference image
            style: Generation style (similar, enhanced, alternative)
            modifications: List of modifications to apply
            
        Returns:
            Dictionary with generation prompt and metadata
        """
        style_instructions = {
            "similar": "Create an image very similar to this one, maintaining the same mood and composition",
            "enhanced": "Create an enhanced version of this image with better lighting and more dramatic elements",
            "alternative": "Create an alternative version with different but complementary elements"
        }
        
        base_instruction = style_instructions.get(style, style_instructions["similar"])
        
        prompt = f"""
        {base_instruction}.
        
        Analyze this image and create a detailed prompt for AI image generation that would produce a similar result.
        Include:
        1. Composition and framing
        2. Subject matter and objects
        3. Color palette and lighting
        4. Mood and atmosphere
        5. Artistic style and technique
        6. Specific details and textures
        
        {f"Apply these modifications: {', '.join(modifications)}" if modifications else ""}
        
        Provide a single, comprehensive prompt suitable for AI image generation tools.
        """
        
        result = self.analyze_image_with_gemini(image_path, prompt)
        
        if result.get("success"):
            result["generation_style"] = style
            result["modifications"] = modifications or []
        
        return result
    
    def batch_analyze_images(
        self, 
        image_paths: List[str],
        analysis_type: str = "basic"
    ) -> Dict[str, Any]:
        """
        Analyze multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            analysis_type: Type of analysis (basic, emotion, metadata)
            
        Returns:
            Dictionary with batch analysis results
        """
        results = []
        
        for image_path in image_paths:
            if analysis_type == "emotion":
                result = self.detect_emotion_in_image(image_path)
            elif analysis_type == "metadata":
                result = self.generate_image_metadata(image_path)
            else:  # basic
                result = self.analyze_image_with_gemini(image_path)
            
            results.append(result)
        
        # Compile batch statistics
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        
        return {
            "batch_results": results,
            "total_images": len(image_paths),
            "successful_analyses": successful,
            "failed_analyses": failed,
            "success_rate": successful / len(image_paths) if image_paths else 0,
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for image file."""
        extension = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        return mime_types.get(extension, 'image/jpeg')
    
    def _parse_emotion_text(self, text: str) -> Dict[str, Any]:
        """Parse emotion information from text response."""
        # Simple text parsing for emotion data
        emotions = ['happy', 'sad', 'fear', 'anger', 'surprise', 'disgust', 'calm', 'love']
        
        text_lower = text.lower()
        detected_emotions = [emotion for emotion in emotions if emotion in text_lower]
        
        return {
            "primary_emotion": detected_emotions[0] if detected_emotions else "neutral",
            "intensity": 0.5,  # Default intensity
            "secondary_emotions": detected_emotions[1:3],
            "visual_elements": [],
            "mood_description": text[:200] + "..." if len(text) > 200 else text
        }
    
    def _parse_suggestions(self, text: str) -> List[Dict[str, str]]:
        """Parse image suggestions from text response."""
        suggestions = []
        lines = text.split('\n')
        
        current_suggestion = ""
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                if current_suggestion:
                    suggestions.append({
                        "description": current_suggestion.strip(),
                        "type": "similar_image"
                    })
                current_suggestion = line.split('.', 1)[-1].strip()
            elif line and current_suggestion:
                current_suggestion += " " + line
        
        # Add the last suggestion
        if current_suggestion:
            suggestions.append({
                "description": current_suggestion.strip(),
                "type": "similar_image"
            })
        
        return suggestions


# Example usage and testing
if __name__ == "__main__":
    captioner = AIImageCaptioner()
    
    # Test with a sample image (you would need to provide an actual image path)
    sample_image = "sample_image.jpg"
    
    if os.path.exists(sample_image):
        print("Testing image analysis...")
        
        # Basic analysis
        basic_result = captioner.analyze_image_with_gemini(sample_image)
        if basic_result.get("success"):
            print(f"Basic analysis: {basic_result['description']}")
        
        # Emotion detection
        emotion_result = captioner.detect_emotion_in_image(sample_image)
        if emotion_result.get("success"):
            emotion_data = emotion_result.get("emotion_analysis", {})
            print(f"Detected emotion: {emotion_data.get('primary_emotion', 'unknown')}")
            print(f"Intensity: {emotion_data.get('intensity', 0)}")
        
        # Image generation prompt
        gen_prompt = captioner.create_image_generation_prompt(sample_image)
        if gen_prompt.get("success"):
            print(f"Generation prompt: {gen_prompt['description']}")
    
    else:
        print(f"Sample image not found: {sample_image}")
        print("Captioner initialized successfully. Provide image paths for analysis.")