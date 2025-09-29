"""
Google API аутентификация
"""

from typing import List
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ai_agent.config import config


class GoogleAuth:
    """Класс для работы с Google API"""
    
    def __init__(self):
        self.credentials = None
        self.sheets_service = None
        self.drive_service = None
        
    def authenticate(self) -> bool:
        """Аутентификация в Google API"""
        try:
            if not config.validate():
                return False
            
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
            
            # Пробуем использовать JSON файл
            if config.GOOGLE_APPLICATION_CREDENTIALS and Path(config.GOOGLE_APPLICATION_CREDENTIALS).exists():
                print(f"🔑 Используем JSON файл: {config.GOOGLE_APPLICATION_CREDENTIALS}")
                self.credentials = Credentials.from_service_account_file(
                    config.GOOGLE_APPLICATION_CREDENTIALS, scopes=scopes
                )
            elif config.GOOGLE_CLIENT_EMAIL and config.GOOGLE_PRIVATE_KEY:
                print("🔑 Используем переменные окружения")
                # Создаем credentials из переменных
                credentials_info = {
                    "type": "service_account",
                    "project_id": config.GOOGLE_PROJECT_ID,
                    "private_key_id": "",
                    "private_key": config.GOOGLE_PRIVATE_KEY,
                    "client_email": config.GOOGLE_CLIENT_EMAIL,
                    "client_id": "",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                self.credentials = Credentials.from_service_account_info(
                    credentials_info, scopes=scopes
                )
            else:
                print("❌ Не найдены credentials для Google API")
                return False
            
            # Создаем сервисы
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
            
            print("✅ Успешная аутентификация в Google API")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка аутентификации: {e}")
            return False
    
    def get_sheets_service(self):
        """Возвращает сервис Google Sheets"""
        if not self.sheets_service:
            self.authenticate()
        return self.sheets_service
    
    def get_drive_service(self):
        """Возвращает сервис Google Drive"""
        if not self.drive_service:
            self.authenticate()
        return self.drive_service


# Глобальный экземпляр
google_auth = GoogleAuth()
