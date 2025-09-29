"""
Google Drive интеграция
"""

from typing import List, Dict, Any
from googleapiclient.errors import HttpError

from ai_agent.config import config
from ai_agent.google.auth import google_auth


class GoogleDrive:
    """Класс для работы с Google Drive"""
    
    def __init__(self):
        self.service = None
        
    def _get_service(self):
        """Получает сервис Google Drive"""
        if not self.service:
            self.service = google_auth.get_drive_service()
        return self.service
    
    def list_files_in_folder(self, folder_id: str, file_types: List[str] = None) -> List[Dict[str, Any]]:
        """Получает список файлов в папке"""
        try:
            service = self._get_service()
            
            # Формируем запрос
            query = f"'{folder_id}' in parents and trashed = false"
            
            if file_types:
                mime_types = []
                for file_type in file_types:
                    if file_type == 'text':
                        mime_types.extend([
                            "mimeType='text/plain'",
                            "mimeType='application/json'"
                        ])
                    elif file_type == 'docs':
                        mime_types.append("mimeType='application/vnd.google-apps.document'")
                
                if mime_types:
                    query += f" and ({' or '.join(mime_types)})"
            
            # Выполняем запрос
            results = service.files().list(
                q=query,
                fields="files(id,name,mimeType,modifiedTime,createdTime)",
                orderBy="modifiedTime desc"
            ).execute()
            
            files = results.get('files', [])
            
            return [{
                'id': file.get('id'),
                'name': file.get('name'),
                'mimeType': file.get('mimeType'),
                'modifiedTime': file.get('modifiedTime'),
                'createdTime': file.get('createdTime')
            } for file in files]
            
        except HttpError as e:
            print(f"❌ Ошибка получения списка файлов: {e}")
            return []
    
    def download_file_content(self, file_id: str, mime_type: str = None) -> str:
        """Скачивает содержимое файла"""
        try:
            service = self._get_service()
            
            # Для Google Docs экспортируем как текст
            if mime_type == 'application/vnd.google-apps.document':
                content = service.files().export(
                    fileId=file_id,
                    mimeType='text/plain'
                ).execute()
                return content.decode('utf-8')
            else:
                # Для обычных файлов скачиваем напрямую
                content = service.files().get_media(fileId=file_id).execute()
                return content.decode('utf-8')
                
        except HttpError as e:
            print(f"❌ Ошибка скачивания файла {file_id}: {e}")
            return ""
    
    def get_transcripts_from_calls_folder(self) -> List[Dict[str, Any]]:
        """Получает транскрипты из папки Calls"""
        if not config.GOOGLE_DRIVE_CALLS_FOLDER_ID:
            print("❌ GOOGLE_DRIVE_CALLS_FOLDER_ID не настроен")
            return []
        
        # Получаем файлы транскриптов
        files = self.list_files_in_folder(
            config.GOOGLE_DRIVE_CALLS_FOLDER_ID,
            file_types=['text', 'docs']
        )
        
        # Фильтруем только новые файлы (последние 7 дней)
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=7)
        
        recent_files = []
        for file in files:
            try:
                # Парсим дату модификации
                mod_time = datetime.fromisoformat(
                    file['modifiedTime'].replace('Z', '+00:00')
                )
                
                if mod_time.replace(tzinfo=None) > cutoff_date:
                    recent_files.append(file)
            except (ValueError, TypeError):
                # Если не можем распарсить дату, включаем файл
                recent_files.append(file)
        
        return recent_files
    
    def process_transcript_file(self, file_info: Dict[str, Any]) -> str:
        """Обрабатывает файл транскрипта и возвращает текст"""
        print(f"📄 Обрабатываем файл: {file_info['name']}")
        
        content = self.download_file_content(
            file_info['id'],
            file_info['mimeType']
        )
        
        if not content:
            print(f"⚠️ Пустой файл: {file_info['name']}")
            return ""
        
        # Очищаем текст от лишних символов
        content = content.strip()
        
        print(f"✅ Загружено {len(content)} символов из {file_info['name']}")
        return content


# Глобальный экземпляр
drive = GoogleDrive()
