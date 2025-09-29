# 🔗 Настройка MCP Google для Cursor

## Что такое MCP Google?
MCP (Model Context Protocol) Google позволяет Cursor напрямую работать с Google Sheets, Drive и другими сервисами Google без промежуточных скриптов.

## 🚀 Настройка MCP Google в Cursor

### 1. Откройте настройки Cursor
- `Ctrl + ,` (или Cursor → Settings)
- Найдите "MCP" в поиске

### 2. Добавьте MCP Google конфигурацию
В файле настроек MCP добавьте:

```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "path/to/your/service-account.json"
      }
    }
  }
}
```

### 3. Настройте переменные окружения
В вашем `.env` файле (или системных переменных):

```env
# Путь к JSON файлу сервис-аккаунта
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor\ai-agent-sheets-473515-12c6cb0e6fab.json

# Или используйте переменные из .env
GOOGLE_PROJECT_ID=ai-agent-sheets-473515
GOOGLE_CLIENT_EMAIL=ai-agent-sheets@ai-agent-sheets-473515.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### 4. Установите MCP Google сервер
```bash
# Через Poetry
poetry add @modelcontextprotocol/server-google

# Или через pip
pip install @modelcontextprotocol/server-google
```

### 5. Перезапустите Cursor
После настройки перезапустите Cursor для применения изменений.

## 🎯 Использование MCP Google

После настройки вы сможете в Cursor:

### Читать Google Sheets:
```
Прочитай данные из Google Sheets таблицы [ID]
Покажи содержимое листа "Algorithm"
```

### Писать в Google Sheets:
```
Добавь новое правило в лист Algorithm
Обнови данные в листе Signals
```

### Работать с Google Drive:
```
Найди файлы в папке Calls
Загрузи транскрипт из Google Drive
```

## 🔧 Альтернативная настройка (через mcp.json)

Создайте файл `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "google": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\fisher\\PycharmProjects\\AI-agent_with_Cursor\\ai-agent-sheets-473515-12c6cb0e6fab.json"
      }
    }
  }
}
```

## 📋 Проверка работы MCP Google

После настройки в Cursor попробуйте:
```
Покажи информацию о моей Google Таблице
Прочитай лист Algorithm из Google Sheets
```

## 🚨 Возможные проблемы:

### 1. "MCP server not found"
```bash
# Через Poetry
poetry add @modelcontextprotocol/server-google

# Или через pip
pip install @modelcontextprotocol/server-google
```

### 2. "Permission denied"
- Проверьте путь к JSON файлу сервис-аккаунта
- Убедитесь, что сервис-аккаунт имеет доступ к таблице

### 3. "Invalid credentials"
- Проверьте JSON файл сервис-аккаунта
- Убедитесь, что API включены в Google Cloud Console

## 🎯 Преимущества MCP Google:

1. **Прямая интеграция** - работа с Google сервисами прямо в Cursor
2. **Автоматизация** - не нужны промежуточные скрипты
3. **Контекст** - Cursor понимает структуру ваших данных
4. **Удобство** - естественные команды на русском языке

---

**После настройки MCP Google Cursor сможет напрямую работать с вашими Google Таблицами!** 🎉
