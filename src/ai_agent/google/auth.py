#!/usr/bin/env python3
"""
Аутентификация для Google API
"""

import json
from pathlib import Path
from oauth2client.service_account import ServiceAccountCredentials

from ai_agent.config import config

class GoogleAuth:
    """Класс для аутентификации в Google API"""
    
    def __init__(self):
        self.credentials = None
        self.sheets_service = None
        self.drive_service = None
    
    def authenticate(self):
        """Аутентифицируется в Google API"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            # Приоритет: JSON файл
            json_path = Path(config.GOOGLE_APPLICATION_CREDENTIALS)
            if json_path.exists():
                print(f"INFO: Используем JSON файл: {json_path}")
                self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    str(json_path),
                    scopes
                )
            else:
                # Альтернатива: переменные окружения
                print("INFO: Используем переменные окружения для аутентификации")
                keyfile_dict = {
                    'type': 'service_account',
                    'project_id': config.GOOGLE_PROJECT_ID,
                    'client_email': config.GOOGLE_CLIENT_EMAIL,
                    'private_key': config.GOOGLE_PRIVATE_KEY.replace('\\n', '\n'),
                }
                self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    keyfile_dict,
                    scopes
                )
            
            print("SUCCESS: Аутентификация успешна")
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка аутентификации: {e}")
            return False
    
    def get_sheets_service(self):
        """Возвращает сервис для работы с Google Sheets"""
        if not self.credentials:
            self.authenticate()
        
        if not self.sheets_service:
            from googleapiclient.discovery import build
            self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        
        return self.sheets_service
    
    def get_drive_service(self):
        """Возвращает сервис для работы с Google Drive"""
        if not self.credentials:
            self.authenticate()
        
        if not self.drive_service:
            from googleapiclient.discovery import build
            self.drive_service = build('drive', 'v3', credentials=self.credentials)
        
        return self.drive_service

# Глобальный экземпляр
google_auth = GoogleAuth()

