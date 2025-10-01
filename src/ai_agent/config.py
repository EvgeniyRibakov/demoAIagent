#!/usr/bin/env python3
"""
Конфигурация приложения
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Класс конфигурации"""
    
    def __init__(self):
        # Google API
        self.GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'google-service-account.json')
        self.GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID', 'your-project-id')
        self.GOOGLE_CLIENT_EMAIL = os.getenv('GOOGLE_CLIENT_EMAIL', 'your-service-account@your-project-id.iam.gserviceaccount.com')
        self.GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY', '')
        
        # Google Sheets
        self.SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
        
        # Google Drive
        self.DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', '')
        
        # OpenAI
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
        self.OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        
        # Настройки анализа
        self.minSamplesDefault = int(os.getenv('MIN_SAMPLES_DEFAULT', '7'))
        
    def validate(self):
        """Проверяет наличие обязательных переменных"""
        missing = []
        
        # Проверяем Google credentials
        json_path = Path(self.GOOGLE_APPLICATION_CREDENTIALS)
        if not json_path.exists():
            if not self.GOOGLE_CLIENT_EMAIL or not self.GOOGLE_PRIVATE_KEY:
                missing.extend(['GOOGLE_APPLICATION_CREDENTIALS (JSON file) или GOOGLE_CLIENT_EMAIL + GOOGLE_PRIVATE_KEY'])
        
        if not self.SPREADSHEET_ID:
            missing.append('SPREADSHEET_ID')
        
        if missing:
            print(f"ERROR: Отсутствуют обязательные переменные: {missing}")
            print("ERROR: Неверная конфигурация. Проверьте .env файл")
            return False
        
        return True

# Глобальный экземпляр конфигурации
config = Config()

