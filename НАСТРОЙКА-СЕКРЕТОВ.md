# Настройка секретов для GitHub

## Проблема
GitHub заблокировал загрузку кода из-за обнаружения секретов в файлах:
- `ai-agent-sheets-473515-12c6cb0e6fab.json` (Google Service Account ключ)
- `.cursor/rules/.env` (OpenAI API ключ)

## Решение

### 1. Создайте файл `.env` в корне проекта
```bash
# Скопируйте env.example в .env
copy env.example .env
```

### 2. Настройте переменные окружения в `.env`
```env
# Google API - используйте JSON файл
GOOGLE_APPLICATION_CREDENTIALS=./ai-agent-sheets-473515-12c6cb0e6fab.json
GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ
GOOGLE_DRIVE_CALLS_FOLDER_ID=your_calls_folder_id

# OpenAI API
OPENAI_API_KEY=sk-your-openai-api-key-here

# Дополнительные настройки
OPENAI_MODEL=gpt-4o-mini
ROLLING_WINDOW_DAYS=7
MIN_SAMPLES_DEFAULT=5
```

### 3. Поместите JSON файл в корень проекта
- Скопируйте `ai-agent-sheets-473515-12c6cb0e6fab.json` в корень проекта
- Убедитесь, что файл не добавлен в Git (он в `.gitignore`)

### 4. Настройте GitHub Secrets (опционально)
Если планируете использовать GitHub Actions:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте следующие секреты:
   - `GOOGLE_APPLICATION_CREDENTIALS` (содержимое JSON файла)
   - `OPENAI_API_KEY`
   - `GOOGLE_SHEETS_ID`
   - `GOOGLE_DRIVE_CALLS_FOLDER_ID`

### 5. Проверьте настройку
```bash
# Активируйте виртуальное окружение
poetry shell

# Проверьте соединения
poetry run python src/ai_agent/setup/test_connections.py
```

## Важные замечания

- ✅ Файл `.env` добавлен в `.gitignore` - секреты не попадут в репозиторий
- ✅ JSON файл Service Account добавлен в `.gitignore`
- ✅ Создан `env.example` как шаблон для других разработчиков
- ⚠️ Никогда не коммитьте файлы с секретами в Git!

## Структура файлов
```
AI-agent_with_Cursor/
├── .env                    # Ваши секреты (НЕ в Git)
├── .env.example           # Шаблон (в Git)
├── .gitignore             # Исключает секреты (в Git)
├── ai-agent-sheets-*.json # Service Account ключ (НЕ в Git)
└── ...
```


