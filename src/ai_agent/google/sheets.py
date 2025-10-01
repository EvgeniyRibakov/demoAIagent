#!/usr/bin/env python3
"""
Работа с Google Sheets API
"""

from typing import List, Optional
from ai_agent.config import config
from ai_agent.google.auth import google_auth

class GoogleSheets:
    """Класс для работы с Google Sheets"""
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = config.SPREADSHEET_ID
    
    def _get_service(self):
        """Получает сервис Google Sheets"""
        if not self.service:
            google_auth.authenticate()
            self.service = google_auth.get_sheets_service()
        return self.service
    
    def read_range(self, sheet_name: str, range_name: str) -> List[List]:
        """Читает данные из диапазона"""
        try:
            service = self._get_service()
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            return result.get('values', [])
        except Exception as e:
            print(f"ERROR: Ошибка чтения из {sheet_name}!{range_name}: {e}")
            return []
    
    def write_range(self, sheet_name: str, range_name: str, values: List[List]) -> bool:
        """Записывает данные в диапазон"""
        try:
            service = self._get_service()
            body = {'values': values}
            service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"ERROR: Ошибка записи в {sheet_name}!{range_name}: {e}")
            return False
    
    def append_rows(self, sheet_name: str, rows: List[List]) -> bool:
        """Добавляет строки в конец листа"""
        try:
            service = self._get_service()
            body = {'values': rows}
            service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            return True
        except Exception as e:
            print(f"ERROR: Ошибка добавления строк в {sheet_name}: {e}")
            return False
    
    def clear_range(self, sheet_name: str, range_name: str) -> bool:
        """Очищает диапазон"""
        try:
            service = self._get_service()
            service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            return True
        except Exception as e:
            print(f"ERROR: Ошибка очистки {sheet_name}!{range_name}: {e}")
            return False
    
    def update_cell_format(self, sheet_name: str, row: int, col: int, 
                          background_color: dict, note: str = None) -> bool:
        """Обновляет форматирование ячейки"""
        try:
            service = self._get_service()
            
            # Получаем sheet_id
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                print(f"ERROR: Лист {sheet_name} не найден")
                return False
            
            requests = []
            
            # Форматирование фона
            requests.append({
                'repeatCell': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': row - 1,
                        'endRowIndex': row,
                        'startColumnIndex': col - 1,
                        'endColumnIndex': col
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': background_color
                        }
                    },
                    'fields': 'userEnteredFormat.backgroundColor'
                }
            })
            
            # Добавляем комментарий если есть
            if note:
                requests.append({
                    'updateCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': row - 1,
                            'endRowIndex': row,
                            'startColumnIndex': col - 1,
                            'endColumnIndex': col
                        },
                        'rows': [{
                            'values': [{
                                'note': note
                            }]
                        }],
                        'fields': 'note'
                    }
                })
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка форматирования ячейки: {e}")
            return False

# Глобальный экземпляр
sheets = GoogleSheets()

