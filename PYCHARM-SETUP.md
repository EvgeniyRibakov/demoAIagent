# 🐍 Настройка проекта в PyCharm

## 🎯 Что мы сделали
Переделали проект под Python с использованием Poetry и создали конфигурации для PyCharm.

## 🚀 Быстрая настройка

### 1. Установка Poetry
```bash
# Windows
curl -sSL https://install.python-poetry.org | python3 -

# Или через pip
pip install poetry
```

### 2. Настройка виртуального окружения
```bash
# В корне проекта
poetry install

# Или активируйте окружение
poetry shell
```

### 3. Установка зависимостей
```bash
# Через Poetry (рекомендуется)
poetry install

# Или через pip
pip install -r requirements.txt
```

## 🔧 Настройка PyCharm

### 1. Откройте проект в PyCharm
- File → Open
- Выберите папку `AI-agent_with_Cursor`

### 2. Настройте интерпретатор Python
- File → Settings → Project → Python Interpreter
- Добавьте интерпретатор из Poetry:
  - ⚙️ → Add → Poetry Environment
  - Или выберите существующий Python 3.9+

### 3. Настройте структуру проекта
- File → Settings → Project Structure
- Mark as Sources Root: `src/`
- Exclude: `__pycache__/`, `*.pyc`

### 4. Конфигурации запуска
В PyCharm уже настроены конфигурации:
- **Setup Google Sheets** - настройка Google Таблицы
- **Proposals from Drive** - обработка транскриптов

### 5. Настройте .env файл
Создайте `.env` в корне проекта:
```env
# Google Cloud Service Account
GOOGLE_PROJECT_ID=ai-agent-sheets-473515
GOOGLE_CLIENT_EMAIL=ai-agent-sheets@ai-agent-sheets-473515.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

# Google Sheets
GOOGLE_SHEETS_ID=18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ

# Google Drive
GOOGLE_DRIVE_CALLS_FOLDER_ID=

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

## 🎯 Запуск в PyCharm

### 1. Настройка Google Sheets
- Запустите конфигурацию "Setup Google Sheets"
- Или: Run → Run 'Setup Google Sheets'
- Это создаст листы и добавит стартовые правила

### 2. Обработка транскриптов
- Запустите конфигурацию "Proposals from Drive"
- Или: Run → Run 'Proposals from Drive'

### 3. Создание собственных скриптов
```python
# Пример скрипта
from ai_agent.google.sheets import sheets
from ai_agent.config import config

def my_script():
    # Ваш код здесь
    info = sheets.get_spreadsheet_info()
    print(f"Таблица: {info['title']}")

if __name__ == "__main__":
    my_script()
```

## 🔧 Полезные команды Poetry

```bash
# Установка зависимостей
poetry install

# Добавление новой зависимости
poetry add requests

# Добавление dev зависимости
poetry add --group dev pytest

# Активация окружения
poetry shell

# Запуск скрипта
poetry run python src/ai_agent/setup/google_setup.py

# Обновление зависимостей
poetry update
```

## 📁 Структура проекта

```
AI-agent_with_Cursor/
├── src/
│   └── ai_agent/
│       ├── __init__.py
│       ├── config.py
│       ├── google/
│       │   ├── auth.py
│       │   └── sheets.py
│       ├── setup/
│       │   └── google_setup.py
│       └── jobs/
├── .idea/                    # PyCharm настройки
├── pyproject.toml           # Poetry конфигурация
├── requirements.txt         # pip зависимости
├── .env                     # Переменные окружения
└── README.md
```

## 🎯 Преимущества Python версии

1. **Привычный синтаксис** - работа в PyCharm как обычно
2. **Poetry** - современное управление зависимостями
3. **Типизация** - mypy для проверки типов
4. **Форматирование** - black + isort
5. **Тестирование** - pytest
6. **Конфигурации PyCharm** - готовые run configurations

## 🚨 Решение проблем

### Poetry не найден
```bash
# Установите Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Добавьте в PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Ошибки импорта
```bash
# Установите зависимости
poetry install

# Или активируйте окружение
poetry shell
```

### Проблемы с .env
- Убедитесь, что файл `.env` в корне проекта
- Проверьте синтаксис (без пробелов вокруг =)
- Используйте кавычки для значений с пробелами

---

**Теперь работайте в PyCharm как привыкли!** 🎉
