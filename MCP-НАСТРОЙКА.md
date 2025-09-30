# 🔗 Настройка MCP Google для Cursor

## ✅ Что уже настроено:

1. **MCP конфигурация** в `~/.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\User\\Downloads\\demoAIagent-main\\ai-agent-sheets-473515-12c6cb0e6fab.json"
      }
    }
  }
}
```

2. **Универсальные пути** в проекте настроены
3. **Тестовый JSON файл** создан для проверки

## 🚀 Следующие шаги:

### 1. Получите реальный JSON файл от Google Cloud Console:

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте проект или выберите существующий
3. Включите Google Sheets API и Google Drive API
4. Создайте Service Account:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Название: "ai-agent-sheets"
   - Role: "Editor"
5. Создайте ключ:
   - Keys → Add Key → Create new key → JSON
   - Скачайте JSON файл

### 2. Замените тестовый JSON файл:

```bash
# Удалите тестовый файл
rm ai-agent-sheets-473515-12c6cb0e6fab.json

# Поместите реальный JSON файл в корень проекта
# Переименуйте его в: ai-agent-sheets-473515-12c6cb0e6fab.json
```

### 3. Обновите .env файл:

```env
# Используйте относительный путь
GOOGLE_APPLICATION_CREDENTIALS=./ai-agent-sheets-473515-12c6cb0e6fab.json

# Остальные настройки
GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ
GOOGLE_DRIVE_CALLS_FOLDER_ID=your-folder-id
OPENAI_API_KEY=sk-your-real-openai-key-here
```

### 4. Дайте доступ Service Account к таблице:

1. Откройте Google Таблицу
2. Share → Добавьте email из JSON файла (client_email)
3. Права: Editor

### 5. Установите MCP Google сервер:

```bash
# Через npm (глобально)
npm install -g @modelcontextprotocol/server-google

# Или через npx (автоматически)
# Уже настроено в mcp.json
```

### 6. Перезапустите Cursor

После настройки перезапустите Cursor для применения MCP конфигурации.

## 🎯 Проверка работы:

### В Cursor попробуйте:
```
Покажи информацию о моей Google Таблице
Прочитай лист Algorithm из Google Sheets
Найди файлы в папке Calls в Google Drive
```

### Через терминал:
```bash
# Тест подключений
poetry run python src/ai_agent/setup/test_connections.py

# Настройка Google Sheets
poetry run python src/ai_agent/setup/google_setup.py
```

## 🔧 Исправленные проблемы:

1. ✅ **Универсальные пути** - проект работает на любом компьютере
2. ✅ **Автоматический поиск JSON** - код сам находит файлы credentials
3. ✅ **MCP конфигурация** - настроена для Cursor
4. ✅ **Конфигурация Python** - исправлены ошибки в коде

## 📊 Текущий статус:

- ✅ **Конфигурация**: РАБОТАЕТ
- ❌ **Google Auth**: Нужен реальный JSON файл
- ❌ **Google Sheets**: Нужен реальный JSON файл  
- ✅ **Google Drive**: РАБОТАЕТ
- ❌ **OpenAI API**: Проблема с регионом (403 ошибка)

## 🎉 После настройки:

Cursor сможет напрямую работать с Google Sheets:
- Читать данные из таблиц
- Записывать новые правила
- Анализировать транскрипты
- Автоматизировать процессы

---

**Готово! Осталось только получить реальный JSON файл от Google Cloud Console!** 🚀
