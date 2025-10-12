"""
字幕生成器
為音訊內容生成同步字幕
"""
from typing import Dict, Any, List


class SubtitleGenerator:
    """
    字幕生成器
    支援多種字幕格式（SRT, VTT, ASS）
    """
    
    def __init__(self, format: str = 'srt'):
        """
        初始化字幕生成器
        
        Args:
            format: 字幕格式 ('srt', 'vtt', 'ass')
        """
        self.format = format
        
    def generate_subtitles(
        self,
        text: str,
        audio_duration: float,
        language: str = 'zh-TW'
    ) -> List[Dict[str, Any]]:
        """
        生成字幕
        
        Args:
            text: 文本內容
            audio_duration: 音訊時長（秒）
            language: 語言
            
        Returns:
            字幕片段列表
        """
        # 將文本分段並分配時間戳
        words = text.split()
        words_per_segment = 10
        segments = []
        
        num_segments = len(words) // words_per_segment + 1
        time_per_segment = audio_duration / num_segments
        
        for i in range(0, len(words), words_per_segment):
            segment_words = words[i:i + words_per_segment]
            segment_text = ' '.join(segment_words)
            
            start_time = (i // words_per_segment) * time_per_segment
            end_time = start_time + time_per_segment
            
            segments.append({
                'index': i // words_per_segment + 1,
                'start_time': start_time,
                'end_time': end_time,
                'text': segment_text
            })
            
        return segments
    
    def format_as_srt(self, segments: List[Dict[str, Any]]) -> str:
        """
        格式化為SRT格式
        
        Args:
            segments: 字幕片段列表
            
        Returns:
            SRT格式字幕
        """
        srt_content = []
        for segment in segments:
            start = self._format_time(segment['start_time'])
            end = self._format_time(segment['end_time'])
            srt_content.append(f"{segment['index']}")
            srt_content.append(f"{start} --> {end}")
            srt_content.append(segment['text'])
            srt_content.append("")  # 空行
            
        return '\n'.join(srt_content)
    
    def _format_time(self, seconds: float) -> str:
        """格式化時間為SRT格式 (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
