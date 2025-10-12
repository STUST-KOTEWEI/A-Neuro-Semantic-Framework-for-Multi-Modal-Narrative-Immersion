# OpenAI GPT-4 整合模組
# 用於生成表情文字、播客腳本等內容

from typing import Dict, Any, List, Optional
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GPTGenerator:
    """
    GPT-4 內容生成器
    用於生成表情文字、播客腳本和其他創意內容
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 GPT 生成器
        
        Args:
            api_key: OpenAI API 金鑰
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"警告：無法初始化 OpenAI 客戶端：{e}")
                self.client = None
        else:
            self.client = None
    
    def generate_emoticon(self, emotion: str, context: str = '') -> Dict[str, Any]:
        """
        根據情緒生成表情文字
        
        Args:
            emotion: 情緒類型（如 'happy', 'sad', 'angry'）
            context: 上下文信息
            
        Returns:
            包含生成的表情文字的字典
        """
        if not self.client:
            return self._mock_emoticon(emotion)
        
        try:
            prompt = f"根據以下情緒和情境生成適當的表情符號或顏文字：\n情緒：{emotion}\n情境：{context}\n請只回覆表情符號，不要其他說明。"
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一個專門生成表情符號的助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7
            )
            
            emoticon = response.choices[0].message.content.strip()
            
            return {
                'emoticon': emoticon,
                'emotion': emotion,
                'context': context,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_podcast_script(
        self, 
        text: str, 
        style: str = 'narrative',
        duration_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        根據文本生成播客腳本
        
        Args:
            text: 輸入文本
            style: 播客風格（narrative, interview, educational）
            duration_minutes: 預期時長（分鐘）
            
        Returns:
            包含播客腳本的字典
        """
        if not self.client:
            return self._mock_podcast_script(text, style)
        
        try:
            prompt = f"""
請根據以下文本生成一個{duration_minutes}分鐘的播客腳本。
風格：{style}
文本內容：{text}

請包含：
1. 開場白
2. 主要內容（分段）
3. 結尾總結

請使用口語化的語言，適合播客播放。
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一個專業的播客腳本撰寫者。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            script = response.choices[0].message.content.strip()
            
            return {
                'script': script,
                'style': style,
                'duration_minutes': duration_minutes,
                'word_count': len(script),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def generate_story_content(
        self,
        text: str,
        content_type: str = 'summary'
    ) -> Dict[str, Any]:
        """
        生成故事相關內容
        
        Args:
            text: 輸入文本
            content_type: 內容類型（summary, analysis, continuation）
            
        Returns:
            包含生成內容的字典
        """
        if not self.client:
            return self._mock_story_content(text, content_type)
        
        try:
            prompts = {
                'summary': f"請為以下文本生成簡潔的摘要：\n{text}",
                'analysis': f"請分析以下文本的情感、主題和文學手法：\n{text}",
                'continuation': f"請為以下故事創作合理的後續內容：\n{text}"
            }
            
            prompt = prompts.get(content_type, prompts['summary'])
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一個專業的文學分析和創作助手。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'content': content,
                'content_type': content_type,
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def _mock_emoticon(self, emotion: str) -> Dict[str, Any]:
        """模擬表情文字生成（當 API 不可用時）"""
        emoticon_map = {
            'happy': '😊 ✨',
            'sad': '😢 💔',
            'angry': '😠 💢',
            'surprise': '😮 ❗',
            'joy': '😄 🎉',
            'fear': '😨 👻',
            'disgust': '🤢 🚫'
        }
        
        return {
            'emoticon': emoticon_map.get(emotion.lower(), '😐'),
            'emotion': emotion,
            'success': True,
            'mock': True
        }
    
    def _mock_podcast_script(self, text: str, style: str) -> Dict[str, Any]:
        """模擬播客腳本生成（當 API 不可用時）"""
        script = f"""
【開場白】
大家好，歡迎收聽本期節目。今天我們要來談談一個有趣的主題。

【主要內容】
{text[:200]}...

讓我們深入探討這個話題。這個故事告訴我們很多關於人性的思考。

【結尾】
感謝大家的收聽，我們下次再見！
"""
        
        return {
            'script': script,
            'style': style,
            'duration_minutes': 5,
            'word_count': len(script),
            'success': True,
            'mock': True
        }
    
    def _mock_story_content(self, text: str, content_type: str) -> Dict[str, Any]:
        """模擬故事內容生成（當 API 不可用時）"""
        content_map = {
            'summary': f"這是一個關於{text[:50]}...的故事摘要。",
            'analysis': f"這個文本展現了豐富的情感和深刻的主題。文本開頭為：{text[:50]}...",
            'continuation': f"故事繼續發展...(基於：{text[:50]}...)"
        }
        
        return {
            'content': content_map.get(content_type, content_map['summary']),
            'content_type': content_type,
            'success': True,
            'mock': True
        }
