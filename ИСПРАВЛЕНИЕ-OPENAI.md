# Исправление проблемы с OpenAI API

## Проблема
```
ERROR: Ошибка настройки OpenAI: [Errno 13] Permission denied: '\\\\.\\aswMonFltProxy\\FFFFAE8C4D6F39D0'
```

## Причина
Антивирус Avast блокирует доступ к OpenAI API через свой фильтр `aswMonFltProxy`.

## Решения

### Вариант 1: Добавить исключения в Avast (Рекомендуется)
1. Откройте Avast Antivirus
2. Перейдите в Настройки → Исключения
3. Добавьте исключения для:
   - `C:\Users\fisher\AppData\Local\Programs\Python\Python312\python.exe`
   - `C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor\`
   - `C:\Users\fisher\AppData\Local\Programs\Python\Python312\Scripts\poetry.exe`

### Вариант 2: Временно отключить защиту
1. Откройте Avast
2. Перейдите в Настройки → Общие
3. Временно отключите "Защита в реальном времени"
4. Запустите тест
5. Включите защиту обратно

### Вариант 3: Использовать другой антивирус
- Временно отключить Avast
- Установить Windows Defender
- Или использовать другой антивирус

## Проверка исправления
```bash
poetry run python src/ai_agent/setup/test_connections.py
```

Должно показать:
```
OpenAI API           SUCCESS: ПРОЙДЕН
```


