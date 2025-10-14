# 修復型別註釋問題的腳本
import re
import os
from pathlib import Path

def fix_type_annotations():
    """修復專案中的型別註釋問題"""
    
    # 定義需要修復的檔案和對應的修復內容
    fixes = {
        'holo/sensory/haptics_emulator.py': [
            # 修復 custom_patterns 的型別
            ('self.custom_patterns = {}', 'self.custom_patterns: Dict[str, Dict[str, Any]] = {}'),
            # 修復其他型別問題
        ],
        'holo/auditory/elevenlabs_tts.py': [
            # 添加必要的型別導入
            ('import io\nimport os', 'import io\nimport os\nfrom typing import Optional, Dict, Any'),
        ]
    }
    
    for file_path, file_fixes in fixes.items():
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for old_text, new_text in file_fixes:
                content = content.replace(old_text, new_text)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"已修復 {file_path}")

if __name__ == "__main__":
    fix_type_annotations()