# 🐍 Настройка проекта в PyCharm

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

### 3. Настройка PyCharm
1. Откройте проект в PyCharm
2. File → Settings → Project → Python Interpreter
3. Add Interpreter → Poetry Environment
4. Выберите существующее окружение Poetry

### 4. Запуск тестов
```bash
poetry run python src/ai_agent/setup/test_connections.py
```

---

Перенесено в `docs/setup/` для организации проекта.

**Дата:** 2025-10-15

