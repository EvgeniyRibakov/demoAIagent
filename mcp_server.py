#!/usr/bin/env python3
"""
MCP сервер для Google сервисов
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Устанавливаем правильный путь к JSON файлу
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google-service-account.json'

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_agent.google.sheets import sheets
from src.ai_agent.google.drive import drive
from src.ai_agent.config import config

class GoogleMCPServer:
    """MCP сервер для Google сервисов"""
    
    def __init__(self):
        self.tools = {
            "google_sheets_read": self.read_sheets,
            "google_sheets_write": self.write_sheets,
            "google_drive_list": self.list_drive_files,
            "google_sheets_info": self.get_sheets_info,
            "google_sheets_scan_signals": self.scan_signals,
            "google_sheets_analyze_daily": self.analyze_daily_changes,
        }
    
    async def read_sheets(self, sheet_name: str, range_name: str) -> Dict[str, Any]:
        """Читает данные из Google Sheets"""
        try:
            data = sheets.read_range(sheet_name, range_name)
            return {
                "success": True,
                "data": data,
                "sheet": sheet_name,
                "range": range_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sheet": sheet_name,
                "range": range_name
            }
    
    async def write_sheets(self, sheet_name: str, range_name: str, values: List[List[Any]]) -> Dict[str, Any]:
        """Записывает данные в Google Sheets"""
        try:
            success = sheets.write_range(sheet_name, range_name, values)
            return {
                "success": success,
                "sheet": sheet_name,
                "range": range_name,
                "rows_written": len(values) if success else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sheet": sheet_name,
                "range": range_name
            }
    
    async def list_drive_files(self, folder_id: str = None) -> Dict[str, Any]:
        """Список файлов в Google Drive"""
        try:
            if folder_id:
                files = drive.list_files(folder_id)
            else:
                files = drive.list_files()
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "files": []
            }
    
    async def get_sheets_info(self) -> Dict[str, Any]:
        """Информация о Google Таблице"""
        try:
            info = sheets.get_spreadsheet_info()
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def scan_signals(self) -> Dict[str, Any]:
        """Сканирует сигналы в Google Таблице"""
        try:
            # Импортируем сканер сигналов
            from src.ai_agent.jobs.scan_data_funnel import DataFunnelScanner
            
            scanner = DataFunnelScanner()
            result = scanner.scan_signals()
            
            if result:
                scanner.save_signals()
                return {
                    "success": True,
                    "signals_found": len(scanner.signals),
                    "signals": scanner.signals
                }
            else:
                return {
                    "success": True,
                    "signals_found": 0,
                    "message": "Сигналы не найдены"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_daily_changes(self) -> Dict[str, Any]:
        """Анализирует ежедневные изменения (сегодня vs вчера)"""
        try:
            # Импортируем анализатор
            from src.ai_agent.jobs.august_daily_analyzer import AugustDailyAnalyzer
            
            analyzer = AugustDailyAnalyzer()
            result = analyzer.analyze_daily_changes()
            
            if not result['success']:
                return result
            
            # Генерируем отчет
            report = analyzer.generate_markdown_report()
            report_path = analyzer.save_report(report)
            
            return {
                "success": True,
                "anomalies_found": len(analyzer.anomalies),
                "anomalies": analyzer.anomalies,
                "report": report,
                "report_path": report_path,
                "message": f"Найдено отклонений: {len(analyzer.anomalies)}"
            }
        except Exception as e:
            import traceback
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Обрабатывает MCP запросы"""
        method = request.get("method")
        params = request.get("params", {})
        
        if method in self.tools:
            result = await self.tools[method](**params)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": result
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method {method} not found"
                }
            }

async def main():
    """Запуск MCP сервера"""
    server = GoogleMCPServer()
    
    # Читаем запросы из stdin
    while True:
        try:
            line = input()
            if not line:
                continue
                
            request = json.loads(line)
            response = await server.handle_request(request)
            print(json.dumps(response))
            
        except EOFError:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))

if __name__ == "__main__":
    asyncio.run(main())
