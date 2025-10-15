# 🎉 MCP Google - ГОТОВ К РАБОТЕ!

## ✅ Статус: ПОЛНОСТЬЮ НАСТРОЕН

MCP Google сервер полностью настроен и готов к работе с Cursor.

## 🚀 Как использовать

### 1. Ручной запуск MCP
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="google-service-account.json"
poetry run python mcp_server.py
```

### 2. Тестирование команд
```powershell
# Информация о таблице
echo '{"jsonrpc": "2.0", "id": 1, "method": "google_sheets_info", "params": {}}' | poetry run python mcp_server.py

# Сканирование сигналов
echo '{"jsonrpc": "2.0", "id": 2, "method": "google_sheets_scan_signals", "params": {}}' | poetry run python mcp_server.py
```

## 📋 Доступные команды MCP

- ✅ `google_sheets_info` - информация о Google Таблице
- ✅ `google_sheets_read` - чтение данных из таблиц
- ✅ `google_sheets_write` - запись данных в таблицы
- ✅ `google_sheets_scan_signals` - сканирование сигналов
- ✅ `google_drive_list` - список файлов в Google Drive

## ✨ Готово!

**MCP Google полностью подключен и готов к работе!**

AI-агент теперь может:
- Читать данные из Google Таблиц
- Записывать данные в Google Таблицы
- Сканировать сигналы автоматически
- Работать с Google Drive
- Выполнять все функции AI-агента через MCP

---

Перенесено в `docs/setup/` для организации проекта.

**Дата:** 2025-10-15

