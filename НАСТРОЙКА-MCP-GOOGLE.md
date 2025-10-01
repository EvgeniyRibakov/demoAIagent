# 🔧 Подробная инструкция по настройке MCP для Google сервисов

## 🎯 Что такое MCP?

MCP (Model Context Protocol) - это протокол, который позволяет AI-ассистентам напрямую взаимодействовать с различными сервисами, включая Google Sheets, Drive, Docs и другие.

## 📋 Предварительные требования

### 1. Установленные программы:
- **Node.js** (версия 18 или выше)
- **npm** (устанавливается с Node.js)
- **Cursor** (с поддержкой MCP)

### 2. Google Cloud аккаунт:
- Активный Google аккаунт
- Доступ к Google Cloud Console

## 🚀 Пошаговая настройка

### Шаг 1: Создание проекта в Google Cloud Console

1. **Откройте Google Cloud Console**
   - Перейдите на https://console.cloud.google.com/
   - Войдите в свой Google аккаунт

2. **Создайте новый проект**
   - Нажмите на выпадающий список проектов (вверху слева)
   - Нажмите "Новый проект"
   - Введите название: `AI-Agent-MCP`
   - Нажмите "Создать"

3. **Выберите созданный проект**
   - Убедитесь, что проект выбран в выпадающем списке

### Шаг 2: Включение необходимых API

1. **Перейдите в раздел API и сервисы**
   - В левом меню: "API и сервисы" → "Библиотека"

2. **Включите следующие API (поиск по названию):**
   - **Google Sheets API** - для работы с таблицами
   - **Google Drive API** - для работы с файлами
   - **Google Docs API** - для работы с документами
   - **Google Calendar API** - опционально, для календаря

3. **Для каждого API:**
   - Найдите API в поиске
   - Нажмите на него
   - Нажмите "Включить"
   - Дождитесь активации

### Шаг 3: Создание Service Account

1. **Перейдите в IAM и администрирование**
   - В левом меню: "IAM и администрирование" → "Service Accounts"

2. **Создайте Service Account**
   - Нажмите "Создать Service Account"
   - Имя: `ai-agent-service`
   - Описание: `Service account for AI Agent MCP`
   - Нажмите "Создать и продолжить"

3. **Назначьте роли:**
   - **Editor** - для полного доступа к Sheets
   - **Viewer** - для чтения Drive
   - **Editor** - для редактирования Docs
   - Нажмите "Продолжить"

4. **Завершите создание**
   - Нажмите "Готово"

### Шаг 4: Создание ключей доступа

1. **Найдите созданный Service Account**
   - В списке Service Accounts найдите `ai-agent-service@your-project.iam.gserviceaccount.com`

2. **Создайте ключ**
   - Нажмите на email Service Account
   - Перейдите на вкладку "Ключи"
   - Нажмите "Добавить ключ" → "Создать новый ключ"
   - Выберите "JSON"
   - Нажмите "Создать"

3. **Сохраните файл**
   - Файл автоматически скачается
   - Переименуйте его в `google-service-account.json`
   - Переместите в корень вашего проекта

### Шаг 5: Установка MCP сервера

**⚠️ ВАЖНО**: Официальные MCP серверы для Google сервисов пока не доступны в npm registry. Используем альтернативный подход.

1. **Откройте терминал в корне проекта**
   ```bash
   # Убедитесь, что вы в корне проекта AI-agent_with_Cursor
   pwd
   ```

2. **Установите базовые MCP пакеты**
   ```bash
   npm install -g @modelcontextprotocol/cli
   npm install -g @modelcontextprotocol/server-filesystem
   ```

3. **Проверьте установку**
   ```bash
   npx @modelcontextprotocol/cli --help
   ```

### Шаг 6: Настройка переменных окружения

1. **Создайте файл .env в корне проекта**
   ```bash
   # В корне проекта создайте .env файл
   touch .env
   ```

2. **Добавьте в .env следующие строки:**
   ```env
   # Google Service Account
   GOOGLE_APPLICATION_CREDENTIALS=./google-service-account.json
   
   # Google Sheets ID (ваша таблица)
   GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ
   
   # OpenAI API (если нужен)
   OPENAI_API_KEY=your_openai_key_here
   ```

### Шаг 7: Настройка MCP в Cursor

**⚠️ АЛЬТЕРНАТИВНЫЙ ПОДХОД**: Поскольку официальные MCP серверы для Google недоступны, используем встроенные возможности Cursor.

1. **Откройте настройки Cursor**
   - `Ctrl+,` (Windows) или `Cmd+,` (Mac)
   - Или File → Preferences → Settings

2. **Найдите раздел MCP**
   - В поиске введите "MCP"
   - Или перейдите в Extensions → MCP

3. **Добавьте конфигурацию MCP для файловой системы**
   - Создайте файл `.cursor/settings.json` в корне проекта:
   ```json
   {
     "mcp": {
       "servers": {
         "filesystem": {
           "command": "npx",
           "args": ["@modelcontextprotocol/server-filesystem", "."],
           "env": {
             "GOOGLE_APPLICATION_CREDENTIALS": "./google-service-account.json"
           }
         }
       }
     }
   }
   ```

4. **Альтернативный способ - через Python**
   - Используйте существующий Python код для работы с Google API
   - MCP будет работать через файловую систему

### Шаг 8: Предоставление доступа к Google Таблице

1. **Откройте вашу Google Таблицу**
   - https://docs.google.com/spreadsheets/d/18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ/edit

2. **Поделитесь таблицей с Service Account**
   - Нажмите "Поделиться" (Share)
   - В поле "Добавить людей и группы" введите email Service Account:
     `ai-agent-service@your-project.iam.gserviceaccount.com`
   - Выберите роль "Редактор"
   - Нажмите "Отправить"

### Шаг 9: Тестирование MCP

1. **Перезапустите Cursor**
   - Закройте и откройте Cursor заново

2. **Проверьте доступность MCP**
   - `Ctrl+Shift+P` (Windows) или `Cmd+Shift+P` (Mac)
   - Введите "MCP: List Available Tools"
   - Должны появиться файловые инструменты

3. **Протестируйте подключение через Python**
   - Используйте существующий тест: `poetry run python src/ai_agent/setup/test_connections.py`
   - Это проверит подключение к Google API

4. **Альтернативное тестирование**
   - В чате с AI попросите: "Прочитай файл google-service-account.json"
   - AI должен прочитать конфигурацию через MCP

## 🔧 Устранение неполадок

### Проблема: "MCP tools not found"
**Решение:**
1. Убедитесь, что Node.js установлен: `node --version`
2. Переустановите MCP сервер: `npm install -g @modelcontextprotocol/server-google`
3. Перезапустите Cursor

### Проблема: "Permission denied"
**Решение:**
1. Проверьте, что Service Account имеет доступ к таблице
2. Убедитесь, что JSON файл находится в корне проекта
3. Проверьте права доступа к файлу

### Проблема: "API not enabled"
**Решение:**
1. Вернитесь в Google Cloud Console
2. Убедитесь, что все необходимые API включены
3. Дождитесь активации (может занять несколько минут)

### Проблема: "Invalid credentials"
**Решение:**
1. Проверьте путь к JSON файлу в .env
2. Убедитесь, что файл не поврежден
3. Создайте новый ключ, если необходимо

## 📊 Проверка работоспособности

### Тест 1: Базовое подключение
```bash
# В терминале проекта
poetry run python -c "
from src.ai_agent.google.sheets import sheets
info = sheets.get_spreadsheet_info()
print('Подключение к Google Sheets:', 'OK' if info else 'ERROR')
"
```

### Тест 2: Чтение данных
```bash
# В терминале проекта
poetry run python -c "
from src.ai_agent.google.sheets import sheets
data = sheets.read_range('Алгоритм', 'A1:Z5')
print('Чтение данных:', 'OK' if data else 'ERROR')
"
```

### Тест 3: MCP в Cursor
- Откройте чат с AI
- Спросите: "Можешь прочитать данные из Google Таблицы?"
- AI должен ответить положительно

## 🎯 После успешной настройки

### Доступные команды MCP:
- `mcp_filesystem_read_file` - чтение файлов
- `mcp_filesystem_write_file` - запись файлов
- `mcp_filesystem_list_directory` - список файлов
- `mcp_filesystem_search_files` - поиск файлов

### Работа с Google API через Python:
- Используйте существующие модули: `src/ai_agent/google/sheets.py`
- AI может запускать Python скрипты для работы с Google API
- Полная интеграция через файловую систему

### Преимущества:
- AI может напрямую работать с Google сервисами
- Автоматическое тестирование функций
- Прямое взаимодействие с данными
- Упрощенная отладка

## ⚠️ Важные замечания

1. **Безопасность**: Никогда не коммитьте JSON ключи в Git
2. **Права доступа**: Давайте минимально необходимые права
3. **Квоты**: Следите за лимитами API
4. **Резервные копии**: Регулярно создавайте бэкапы данных

## 🎉 Готово!

После выполнения всех шагов у вас будет:
- ✅ Настроенный MCP для Google сервисов
- ✅ Прямой доступ AI к Google Таблицам
- ✅ Возможность автоматического тестирования
- ✅ Полная интеграция с вашим проектом

**AI-агент теперь может самостоятельно работать с Google Таблицами!** 🚀