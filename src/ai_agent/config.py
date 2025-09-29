"""
Конфигурация AI Agent
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Пути
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    SRC_DIR: Path = BASE_DIR / "src"
    
    # Google API - сначала пробуем JSON файл, потом переменные окружения
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID", "ai-agent-sheets-473515")
    GOOGLE_CLIENT_EMAIL: str = os.getenv("GOOGLE_CLIENT_EMAIL", "ai-agent-sheets@ai-agent-sheets-473515.iam.gserviceaccount.com")
    GOOGLE_PRIVATE_KEY: str = os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n")
    GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ")
    GOOGLE_DRIVE_CALLS_FOLDER_ID: str = os.getenv("GOOGLE_DRIVE_CALLS_FOLDER_ID", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Настройки сканирования
    ROLLING_WINDOW_DAYS: int = 7
    MIN_SAMPLES_DEFAULT: int = 5
    
    # Цвета подсветки
    HIGHLIGHT_COLORS = {
        "bg": "#fff3cd",
        "high": "#ffebee",
        "medium": "#fff3e0", 
        "low": "#e8f5e8"
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет корректность конфигурации"""
        # Проверяем наличие JSON файла или переменных
        has_json_file = cls.GOOGLE_APPLICATION_CREDENTIALS and Path(cls.GOOGLE_APPLICATION_CREDENTIALS).exists()
        has_env_vars = cls.GOOGLE_CLIENT_EMAIL and cls.GOOGLE_PRIVATE_KEY
        
        if not has_json_file and not has_env_vars:
            print("❌ Не настроены Google API credentials")
            print("📝 Укажите GOOGLE_APPLICATION_CREDENTIALS или GOOGLE_CLIENT_EMAIL + GOOGLE_PRIVATE_KEY в .env")
            return False
        
        if not cls.GOOGLE_SHEETS_ID:
            print("❌ GOOGLE_SHEETS_ID не настроен")
            return False
            
        return True

# Глобальная конфигурация
config = Config()
