# 🔧 Настройка MCP через Python (без npm)

## 🎯 Альтернативный подход через Python

Поскольку npm пакеты MCP недоступны, используем Python-реализацию MCP сервера.

## 🚀 Установка MCP через Python

### Шаг 1: Установка MCP сервера

```bash
# Установка через pip
pip install mcp

# Или через poetry (рекомендуется)
poetry add mcp
```

### Шаг 2: Создание MCP сервера для Google

Создайте файл `mcp_server.py` в корне проекта:

```python
#!/usr/bin/env python3
"""
MCP сервер для Google сервисов
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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
```

### Шаг 3: Настройка Cursor для MCP

Создайте файл `.cursor/mcp.json`:

```json
{
  "mcp": {
    "servers": {
      "google": {
        "command": "python",
        "args": ["mcp_server.py"],
        "cwd": "C:\\Users\\fisher\\PycharmProjects\\AI-agent_with_Cursor",
        "env": {
          "GOOGLE_APPLICATION_CREDENTIALS": "google-service-account.json"
        }
      }
    }
  }
}
```

**⚠️ ВАЖНО**: Замените путь `cwd` на ваш реальный путь к проекту!

### Шаг 4: Тестирование MCP

1. **Запустите MCP сервер вручную:**
   ```bash
   # Windows PowerShell
   $env:GOOGLE_APPLICATION_CREDENTIALS="google-service-account.json"
   poetry run python mcp_server.py
   
   # Или через bat файл
   test_mcp.bat
   ```

2. **Отправьте тестовый запрос:**
   ```bash
   # Windows PowerShell
   $env:GOOGLE_APPLICATION_CREDENTIALS="google-service-account.json"
   echo '{"jsonrpc": "2.0", "id": 1, "method": "google_sheets_info", "params": {}}' | poetry run python mcp_server.py
   ```

3. **Проверьте в Cursor:**
   - `Ctrl+Shift+P` → "MCP: List Available Tools"
   - Должны появиться Google инструменты
   - Перезапустите Cursor после настройки MCP

## 🎯 Альтернативный подход - через Poetry

### Добавьте в pyproject.toml:

```toml
[tool.poetry.dependencies]
mcp = "^0.1.0"
# ... остальные зависимости

[tool.poetry.scripts]
mcp-server = "mcp_server:main"
```

### Запуск через Poetry:

```bash
# Установка зависимостей
poetry install

# Запуск MCP сервера
poetry run mcp-server
```

## 🔧 Устранение неполадок

### Проблема: "Module not found"
**Решение:**
```bash
# Убедитесь, что все зависимости установлены
poetry install
# или
pip install -r requirements.txt
```

### Проблема: "Permission denied"
**Решение:**
```bash
# Проверьте права доступа к JSON файлу
chmod 600 google-service-account.json
```

### Проблема: "MCP not working in Cursor"
**Решение:**
1. Перезапустите Cursor
2. Проверьте `.cursor/settings.json`
3. Убедитесь, что путь к Python правильный

## 🎉 Готово!

После настройки у вас будет:
- ✅ MCP сервер на Python
- ✅ Прямой доступ к Google API
- ✅ Интеграция с Cursor
- ✅ Полная функциональность AI-агента

**AI теперь может напрямую работать с Google Таблицами через MCP!** 🚀
