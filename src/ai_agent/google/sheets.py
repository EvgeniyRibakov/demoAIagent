"""
Google Sheets интеграция
"""

from typing import List, Dict, Any, Optional
from googleapiclient.errors import HttpError

from ai_agent.config import config
from ai_agent.google.auth import google_auth


class GoogleSheets:
    """Класс для работы с Google Sheets"""
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = config.GOOGLE_SHEETS_ID
        
    def _get_service(self):
        """Получает сервис Google Sheets"""
        if not self.service:
            if not google_auth.authenticate():
                return None
            self.service = google_auth.sheets_service
        return self.service
    
    def get_spreadsheet_info(self) -> Dict[str, Any]:
        """Получает информацию о таблице"""
        try:
            service = self._get_service()
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            return {
                "title": spreadsheet.get("properties", {}).get("title", ""),
                "sheets": [sheet.get("properties", {}).get("title", "") 
                          for sheet in spreadsheet.get("sheets", [])]
            }
        except HttpError as e:
            print(f"ERROR: Ошибка получения информации о таблице: {e}")
            return {}
    
    def create_sheet(self, sheet_name: str) -> bool:
        """Создает новый лист"""
        try:
            service = self._get_service()
            
            request_body = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheet_name,
                            "gridProperties": {
                                "rowCount": 1000,
                                "columnCount": 20
                            }
                        }
                    }
                }]
            }
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            print(f"SUCCESS: Создан лист: {sheet_name}")
            return True
            
        except HttpError as e:
            if "already exists" in str(e):
                print(f"INFO: Лист {sheet_name} уже существует")
                return True
            print(f"ERROR: Ошибка создания листа {sheet_name}: {e}")
            return False
    
    def set_headers(self, sheet_name: str, headers: List[str]) -> bool:
        """Устанавливает заголовки листа"""
        try:
            service = self._get_service()
            
            # Определяем диапазон для заголовков
            end_col = chr(ord('A') + len(headers) - 1)
            range_name = f"{sheet_name}!A1:{end_col}1"
            
            service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            print(f"SUCCESS: Заголовки установлены для листа: {sheet_name}")
            return True
            
        except HttpError as e:
            print(f"ERROR: Ошибка установки заголовков: {e}")
            return False
    
    def append_rows(self, sheet_name: str, rows: List[List[Any]]) -> bool:
        """Добавляет строки в лист"""
        try:
            service = self._get_service()
            
            service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A:Z",
                valueInputOption='USER_ENTERED',
                body={'values': rows}
            ).execute()
            
            print(f"SUCCESS: Добавлено {len(rows)} строк в лист {sheet_name}")
            return True
            
        except HttpError as e:
            print(f"ERROR: Ошибка добавления строк: {e}")
            return False
    
    def read_range(self, sheet_name: str, range_name: str) -> List[List[Any]]:
        """Читает данные из диапазона"""
        try:
            service = self._get_service()
            
            result = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            
            return result.get('values', [])
            
        except HttpError as e:
            print(f"ERROR: Ошибка чтения данных: {e}")
            return []
    
    def setup_schema(self) -> bool:
        """Создает схему листов и заголовков"""
        try:
            # Схема листов
            sheets_config = {
                'Algorithm': [
                    'RuleId', 'Block', 'Metric', 'ConditionType', 'ConditionParams',
                    'ActionType', 'ActionParams', 'Severity', 'AutoApply', 'Active',
                    'CreatedAt', 'Notes'
                ],
                'Signals': [
                    'Timestamp', 'Block', 'Metric', 'Date', 'CurrentValue',
                    'BaselineValue', 'DeltaPct', 'RuleId', 'Status', 'LinkToCell', 'Severity'
                ],
                'Decisions': [
                    'SignalId', 'SuggestedActionType', 'ActionParams', 'Rationale',
                    'Status', 'ApprovedBy', 'AppliedAt', 'AuditLog', 'Confidence'
                ],
                'Proposals': [
                    'CallDate', 'ExtractedCase', 'ExistingRuleMatched',
                    'SuggestedRuleDiff', 'Confidence', 'Status', 'Notes', 'RuleId'
                ]
            }
            
            # Создаем листы и заголовки
            for sheet_name, headers in sheets_config.items():
                self.create_sheet(sheet_name)
                self.set_headers(sheet_name, headers)
            
            print("SUCCESS: Схема листов создана")
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка создания схемы: {e}")
            return False
    
    def add_starter_rules(self) -> bool:
        """Добавляет стартовые правила в лист Algorithm"""
        try:
            from datetime import datetime
            
            starter_rules = [
                [
                    'R001', 'funnel', 'Конверсия в корзину, %', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}',
                    'price_adjust',
                    '{"competitor_scan":"on","target_delta_pct":"match_top3-1%","floor_margin_pct":12}',
                    'high', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ],
                [
                    'R002', 'ads', 'CTR', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}',
                    'content_ticket',
                    '{"task":"replace_main_image","priority":"high","assignee":"content_manager"}',
                    'medium', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ],
                [
                    'R003', 'funnel', 'Переходы в карточку', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.2,"min_samples":5}',
                    'ads_bid_adjust',
                    '{"target":"clicks","delta":"-10% to +10%","guard":"acos<=0.3"}',
                    'medium', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ],
                [
                    'R004', 'funnel', 'Положили в корзину', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.15,"min_samples":5}',
                    'price_adjust',
                    '{"competitor_scan":"on","target_delta_pct":"match_top3-2%","floor_margin_pct":10}',
                    'high', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ],
                [
                    'R005', 'funnel', 'CR', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.1,"min_samples":5}',
                    'content_ticket',
                    '{"task":"review_product_description","priority":"high","assignee":"content_manager"}',
                    'high', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ],
                [
                    'R006', 'ads', 'Показы', 'ratio',
                    '{"baseline":"rolling_7d","drop_pct":0.3,"min_samples":5}',
                    'ads_budget_adjust',
                    '{"target":"impressions","delta":"+20%","max_budget_increase":5000}',
                    'low', 'N', 'Y', datetime.now().isoformat(), 'Автоматически добавлено'
                ]
            ]
            
            # Проверяем, есть ли уже данные
            existing_data = self.read_range('Algorithm', 'A2:L1000')
            if existing_data:
                print("INFO: В Algorithm уже есть данные, пропускаем добавление правил")
                return True
            
            # Добавляем правила
            self.append_rows('Algorithm', starter_rules)
            print(f"SUCCESS: Добавлено {len(starter_rules)} стартовых правил")
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка добавления стартовых правил: {e}")
            return False


# Глобальный экземпляр
sheets = GoogleSheets()
