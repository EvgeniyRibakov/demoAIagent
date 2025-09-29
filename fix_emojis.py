#!/usr/bin/env python3
"""
Скрипт для замены эмодзи на обычные символы в файлах проекта
"""

import os
import re
from pathlib import Path

def replace_emojis_in_file(file_path):
    """Заменяет эмодзи в файле"""
    emoji_replacements = {
        '❌': 'ERROR:',
        '✅': 'SUCCESS:',
        '⚠️': 'WARNING:',
        '🔑': 'INFO:',
        '📊': 'INFO:',
        '💾': 'INFO:',
        '🤖': 'INFO:',
        '🚀': 'INFO:',
        '📋': 'INFO:',
        '🎉': 'SUCCESS:',
        '📝': 'INFO:',
        '🔍': 'INFO:',
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Основная функция"""
    project_root = Path(__file__).parent
    src_dir = project_root / "src" / "ai_agent"
    
    if not src_dir.exists():
        print("Source directory not found")
        return
    
    fixed_files = 0
    total_files = 0
    
    for py_file in src_dir.rglob("*.py"):
        total_files += 1
        if replace_emojis_in_file(py_file):
            fixed_files += 1
    
    print(f"\nProcessed {total_files} files, fixed {fixed_files} files")

if __name__ == "__main__":
    main()
