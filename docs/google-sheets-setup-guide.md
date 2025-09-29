# 🔗 Гайд: Связка Google Таблиц и Cursor

## 🎯 Что мы делаем
Настраиваем автоматическую связку между Cursor (Node.js) и Google Таблицами через Google Sheets API, чтобы агент мог читать/писать данные без ручного вмешательства.

## 📋 Пошаговая настройка

### Шаг 1: Создание Google Cloud Project

1. **Откройте Google Cloud Console**
   - Перейдите: https://console.cloud.google.com/
   - Войдите в Google аккаунт

2. **Создайте новый проект**
   - Нажмите "Select a project" → "New Project"
   - Название: `ai-agent-sheets` (или любое другое)
   - Нажмите "Create"

3. **Включите необходимые API**
   - Перейдите: APIs & Services → Library
   - Найдите и включите:
     - **Google Sheets API** → Enable
     - **Google Drive API** → Enable

### Шаг 2: Создание Service Account

1. **Создайте Service Account**
   - Перейдите: IAM & Admin → Service Accounts
   - Нажмите "Create Service Account"
   - Название: `ai-agent-sheets`
   - Описание: `Service account for AI Agent automation`
   - Нажмите "Create and Continue"

2. **Назначьте роли**
   - Role: `Editor` (или создайте кастомную роль)
   - Нажмите "Continue" → "Done"

3. **Создайте ключ**
   - Найдите созданный Service Account
   - Нажмите на него
   - Перейдите: Keys → Add Key → Create new key
   - Выберите: JSON
   - Нажмите "Create"
   - **Скачайте JSON файл** (он понадобится)

### Шаг 3: Настройка переменных окружения

1. **Создайте .env файл**
   ```bash
   cp .env.example .env
   ```

2. **Заполните .env из скачанного JSON**
   ```env
   # Из JSON файла
   GOOGLE_PROJECT_ID=your-project-id
   GOOGLE_CLIENT_EMAIL=ai-agent-sheets@your-project.iam.gserviceaccount.com
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   
   # ID вашей Google Таблицы (из URL)
   GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ
   
   # ID папки в Google Drive для транскриптов (создайте позже)
   GOOGLE_DRIVE_CALLS_FOLDER_ID=
   
   # OpenAI API ключ для LLM
   OPENAI_API_KEY=sk-...
   ```

3. **Важно для GOOGLE_PRIVATE_KEY**
   - Скопируйте private_key из JSON
   - Оберните в кавычки
   - Замените все `\n` на `\\n`
   - Пример:
   ```env
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\\n-----END PRIVATE KEY-----\\n"
   ```

### Шаг 4: Предоставление доступа к таблице

1. **Откройте вашу Google Таблицу**
   - https://docs.google.com/spreadsheets/d/18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ/edit

2. **Добавьте Service Account**
   - Нажмите "Share" (правый верхний угол)
   - Добавьте email из `GOOGLE_CLIENT_EMAIL`
   - Права: **Editor**
   - Нажмите "Send"

### Шаг 5: Автоматическая настройка

1. **Установите зависимости**
   ```bash
   poetry install
   # или
   pip install -r requirements.txt
   ```

2. **Запустите автоматическую настройку**
   ```bash
   poetry run python src/ai_agent/setup/google_setup.py
   # или
   python src/ai_agent/setup/google_setup.py
   ```

   Этот скрипт:
   - Проверит доступ к таблице
   - Создаст листы: Algorithm, Signals, Decisions, Proposals
   - Добавит заголовки
   - Вставит 6 стартовых правил

### Шаг 6: Добавление Apps Script

1. **Откройте Google Таблицу**
2. **Extensions → Apps Script**
3. **Удалите весь существующий код**
4. **Скопируйте код из файла**
   - Откройте: `src/apps-script/enhanced-agent.gs`
   - Скопируйте весь код
   - Вставьте в Apps Script
5. **Сохраните** (Ctrl+S)
6. **Вернитесь в таблицу**
7. **Обновите страницу** (F5)
8. **Появится меню "🤖 AI Agent"**

### Шаг 7: Тестирование

1. **Проверьте схему**
   - 🤖 AI Agent → 🔧 Настройка схемы

2. **Протестируйте сканирование**
   - 🤖 AI Agent → 📊 Сканировать сигналы

3. **Откройте панель управления**
   - 🤖 AI Agent → 📋 Панель управления

## 🔧 Команды для управления

```bash
# Полная настройка
npm run setup:all

# Только Google Sheets
npm run setup:google

# Обработка транскриптов
npm run proposals:from-drive

# Сборка проекта
npm run build
```

## 🐛 Решение проблем

### Ошибка "PERMISSION_DENIED"
- Проверьте, что Service Account добавлен в таблицу
- Убедитесь, что права установлены как "Editor"
- Проверьте правильность GOOGLE_SHEETS_ID

### Ошибка "Invalid credentials"
- Проверьте формат GOOGLE_PRIVATE_KEY (должны быть \\n)
- Убедитесь, что JSON ключ не поврежден
- Проверьте, что GOOGLE_CLIENT_EMAIL правильный

### Ошибка "Spreadsheet not found"
- Проверьте GOOGLE_SHEETS_ID в .env
- Убедитесь, что таблица существует и доступна

## ✅ Проверка работоспособности

После настройки в таблице должны появиться:
- Лист **Algorithm** с 6 правилами
- Листы **Signals**, **Decisions**, **Proposals** с заголовками
- Меню **🤖 AI Agent** в интерфейсе

## 🎯 Следующие шаги

1. ✅ Настройте базовую связку (этот гайд)
2. 🔄 Протестируйте сканирование сигналов
3. 📞 Настройте tl;dv → Google Drive
4. 🚀 Добавьте новые правила и действия

---

**Готово!** Теперь Cursor может автоматически работать с Google Таблицами. 🎉
