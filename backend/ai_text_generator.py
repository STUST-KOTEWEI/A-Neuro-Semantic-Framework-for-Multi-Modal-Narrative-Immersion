"""
AI Text Generator Module

Integrates with Google Generative AI (Gemini) for text generation and enhancement.
Also provides Ollama integration for local LLM processing.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AITextGenerator:
    """
    Handles text generation using Google Gemini and Ollama.
    """
    
    def __init__(self, google_api_key: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        """
        Initialize the text generator.
        
        Args:
            google_api_key: Google Generative AI API key
            ollama_url: Ollama server URL
        """
        self.google_api_key = google_api_key or os.getenv("GOOGLE_GENAI_API_KEY")
        self.ollama_url = ollama_url
        
        # Initialize Google Generative AI
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
            print("Warning: Google API key not configured")
    
    def generate_text_with_gemini(
        self, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using Google Gemini.
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            
        Returns:
            Dictionary with generated text and metadata
        """
        if not self.gemini_model:
            return {"error": "Google Gemini not configured"}
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return {
                "generated_text": response.text,
                "model": "gemini-pro",
                "timestamp": datetime.now().isoformat(),
                "prompt_length": len(prompt),
                "response_length": len(response.text),
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "model": "gemini-pro",
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def generate_text_with_ollama(
        self, 
        prompt: str, 
        model: str = "phi3:mini",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        # Model aliases for different languages and contexts
        self.alias_map = {
            "現代閱讀": "ModernReader",  # 官方中文別名
            "现代阅读": "ModernReader",  # 簡體中文
            "modern-reader": "ModernReader",  # 英文別名
            "現代閱讀器": "ModernReader",  # 完整中文名稱
            "phi3": "phi3:mini"  # 備用模型
        }
        
        # Resolve alias
        if model in self.alias_map:
            model = self.alias_map[model]
            
        """
        Generate text using Ollama.
        
        Args:
            prompt: Input prompt for generation
            model: Ollama model name
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.0-1.0)
            
        Returns:
            Dictionary with generated text and metadata
        """
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                },
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "generated_text": result.get("response", ""),
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "prompt_length": len(prompt),
                    "response_length": len(result.get("response", "")),
                    "success": True,
                    "done": result.get("done", False)
                }
            else:
                return {
                    "error": f"Ollama request failed: {response.status_code}",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                    "success": False
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "model": model,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def enhance_narrative_text(
        self, 
        text: str, 
        style: str = "immersive",
        use_google: bool = True
    ) -> Dict[str, Any]:
        """
        Enhance narrative text for better immersion.
        
        Args:
            text: Original text to enhance
            style: Enhancement style ('immersive', 'dramatic', 'poetic')
            use_google: Whether to use Google Gemini (True) or Ollama (False)
            
        Returns:
            Dictionary with enhanced text and metadata
        """
        style_prompts = {
            "immersive": f"""
            Enhance the following text to make it more immersive and engaging for a multi-sensory reading experience. 
            Add vivid sensory descriptions (sight, sound, touch, smell, taste) while maintaining the original meaning.
            Focus on creating emotional resonance and atmospheric details.
            
            Original text: {text}
            
            Enhanced version:
            """,
            "dramatic": f"""
            Rewrite the following text with more dramatic tension and emotional intensity.
            Enhance the pacing, add compelling details, and strengthen the emotional impact.
            
            Original text: {text}
            
            Dramatic version:
            """,
            "poetic": f"""
            Transform the following text into a more poetic and lyrical version.
            Use beautiful metaphors, rhythm, and evocative imagery while preserving the core message.
            
            Original text: {text}
            
            Poetic version:
            """
        }
        
        prompt = style_prompts.get(style, style_prompts["immersive"])
        
        if use_google and self.gemini_model:
            result = self.generate_text_with_gemini(prompt)
        else:
            result = self.generate_text_with_ollama(prompt)
        
        result["enhancement_style"] = style
        result["original_text"] = text
        return result
    
    def generate_emotional_description(
        self, 
        emotion: str, 
        intensity: float,
        context: str = "",
        use_google: bool = True
    ) -> Dict[str, Any]:
        """
        Generate descriptive text for a specific emotion.
        
        Args:
            emotion: Target emotion (e.g., 'happy', 'sad', 'fear')
            intensity: Emotion intensity (0.0-1.0)
            context: Additional context for generation
            use_google: Whether to use Google Gemini (True) or Ollama (False)
            
        Returns:
            Dictionary with generated description and metadata
        """
        intensity_words = {
            0.0: "barely noticeable",
            0.3: "mild",
            0.5: "moderate", 
            0.7: "strong",
            0.9: "overwhelming",
            1.0: "all-consuming"
        }
        
        # Find closest intensity description
        intensity_desc = min(intensity_words.items(), 
                           key=lambda x: abs(x[0] - intensity))[1]
        
        prompt = f"""
        Generate a vivid, immersive description that captures the emotion of {emotion} 
        at a {intensity_desc} intensity level ({intensity:.1f}/1.0).
        
        Context: {context if context else "General emotional state"}
        
        The description should:
        - Include sensory details (what the character sees, hears, feels, smells)
        - Capture physical sensations and bodily responses
        - Convey the internal emotional experience
        - Be suitable for a multi-sensory narrative experience
        - Be 2-3 sentences long
        
        Description:
        """
        
        if use_google and self.gemini_model:
            result = self.generate_text_with_gemini(prompt, max_tokens=200)
        else:
            result = self.generate_text_with_ollama(prompt, max_tokens=200)
        
        result["emotion"] = emotion
        result["intensity"] = intensity
        result["context"] = context
        return result
    
    def generate_image_prompts(
        self, 
        text: str, 
        count: int = 3,
        style: str = "realistic",
        use_google: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image prompts based on text content.
        
        Args:
            text: Source text for image generation
            count: Number of prompts to generate
            style: Image style (realistic, artistic, abstract)
            use_google: Whether to use Google Gemini (True) or Ollama (False)
            
        Returns:
            Dictionary with generated prompts and metadata
        """
        prompt = f"""
        Based on the following text, generate {count} detailed image prompts for AI image generation.
        Each prompt should capture different visual aspects of the scene, emotion, or atmosphere.
        
        Style preference: {style}
        
        Text: {text}
        
        Generate prompts that include:
        - Visual composition and framing
        - Color palette and lighting
        - Mood and atmosphere
        - Specific details and elements
        
        Format as a numbered list:
        """
        
        if use_google and self.gemini_model:
            result = self.generate_text_with_gemini(prompt, max_tokens=500)
        else:
            result = self.generate_text_with_ollama(prompt, max_tokens=500)
        
        # Parse numbered list from response
        if result.get("success"):
            generated_text = result["generated_text"]
            prompts = []
            
            for line in generated_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering
                    clean_prompt = line.split('.', 1)[-1].strip()
                    if clean_prompt:
                        prompts.append(clean_prompt)
            
            result["image_prompts"] = prompts[:count]
        
        result["style"] = style
        result["prompt_count"] = count
        return result
    
    def check_ollama_status(self) -> Dict[str, Any]:
        """
        Check if Ollama server is running and available.
        
        Returns:
            Dictionary with Ollama status information
        """
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return {
                    "status": "online",
                    "url": self.ollama_url,
                    "available_models": [model["name"] for model in models],
                    "model_count": len(models)
                }
            else:
                return {
                    "status": "error",
                    "url": self.ollama_url,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "url": self.ollama_url,
                "error": str(e)
            }


# Example usage and testing
if __name__ == "__main__":
    generator = AITextGenerator()
    
    # Test Ollama status
    print("Checking Ollama status...")
    ollama_status = generator.check_ollama_status()
    print(f"Ollama status: {ollama_status}")
    
    # Test text enhancement
    test_text = "The old house creaked in the wind, its windows rattling like bones."
    
    print("\nTesting text enhancement with Google Gemini...")
    if generator.gemini_model:
        enhanced = generator.enhance_narrative_text(test_text, style="immersive")
        if enhanced.get("success"):
            print(f"Original: {test_text}")
            print(f"Enhanced: {enhanced['generated_text']}")
        else:
            print(f"Error: {enhanced.get('error')}")
    
    # Test emotional description
    print("\nTesting emotional description...")
    if generator.gemini_model:
        emotion_desc = generator.generate_emotional_description(
            emotion="fear", 
            intensity=0.8, 
            context="old house at night"
        )
        if emotion_desc.get("success"):
            print(f"Fear description: {emotion_desc['generated_text']}")
    
    # Test image prompt generation
    print("\nTesting image prompt generation...")
    if generator.gemini_model:
        image_prompts = generator.generate_image_prompts(test_text, count=2)
        if image_prompts.get("success"):
            print("Generated image prompts:")
            for i, prompt in enumerate(image_prompts.get("image_prompts", []), 1):
                print(f"{i}. {prompt}")