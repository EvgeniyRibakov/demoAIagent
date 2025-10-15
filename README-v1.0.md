# AI-агент для Google Sheets - Версия 1.0

## 🎯 Что это

AI-агент для автоматического анализа данных в Google Sheets с интеграцией правил и алгоритмов.

**Конечная цель:** Сверять сегодняшние данные со вчерашними и предлагать действия по алгоритмам на листе.

## ✅ Что работает в версии 1.0

### 1. **Google Apps Script** (в таблице)
- ✅ Автоматическое определение листов месяцев
- ✅ Сканирование по правилам из Algorithm
- ✅ Запись сигналов в Signals
- ✅ Генерация решений в Decisions
- ✅ Боковая панель для управления
- ✅ Автоматическое расписание (9:00 каждый день)

### 2. **Python анализатор**
- ✅ Автоматический выбор последнего листа месяца
- ✅ Интеграция с листом Algorithm
- ✅ Запись в Signals и Decisions
- ✅ Подсветка ячеек с комментариями
- ✅ Генерация MD отчетов
- ✅ Git автоматизация (commit + push)

### 3. **MCP интеграция**
- ✅ Прямой доступ к Google Sheets из Cursor
- ✅ Автоматический анализ через AI

## 📊 Структура Google Таблицы

### Листы с данными
- **"Август 2025"**, **"Сентябрь 2025"** и т.д.
- Формат: "Месяц Год"
- Автоматически определяются агентом

### Системные листы
- **Algorithm** - правила для анализа (формат "если...то...")
- **Signals** - найденные отклонения
- **Decisions** - предложенные решения
- **Изменения** - история действий агента
- **Proposals** - предложения из созвонов (для будущих версий)

## 🚀 Быстрый старт

### 1. Установка Python зависимостей
```bash
cd demoAIagent
poetry install
# или
pip install -r requirements.txt
```

### 2. Настройка .env файла
Скопируйте `env.example` в `.env` и заполните:
```env
GOOGLE_APPLICATION_CREDENTIALS=google-service-account.json
SPREADSHEET_ID=ваш_id_таблицы
```

### 3. Установка Apps Script
1. Откройте вашу Google Таблицу
2. Extensions → Apps Script
3. Скопируйте код из `src/apps-script/enhanced-agent.gs`
4. Сохраните (Ctrl+S)
5. В таблице появится меню "🤖 AI Агент"

### 4. Настройка схемы
В меню "🤖 AI Агент":
1. Нажмите "🔧 Настройка схемы"
2. Нажмите "⚙️ Добавить правила" (стартовые правила)
3. Нажмите "🔄 Настроить расписание" (автозапуск в 9:00)

## 💻 Использование

### Через Apps Script (в таблице)
1. **Ручное сканирование:** Меню → "📊 Сканировать сигналы"
2. **Саммари:** Меню → "📈 Саммари изменений"
3. **Панель управления:** Меню → "📋 Панель управления"

### Через Python (локально)
```bash
# Анализ с интеграцией Algorithm
poetry run python src/ai_agent/jobs/daily_analyzer_with_algorithm.py

# Старый анализатор (только для "Август 2025")
poetry run python src/ai_agent/jobs/august_daily_analyzer.py
```

### Через MCP (в Cursor)
Просто спросите AI:
```
"Проанализируй сегодняшние данные в таблице"
```

## 🔧 Исправленные баги в v1.0

### 1. ❌ → ✅ Баг в `clearAllHighlights()`
**Было:**
```javascript
CONFIG.dataSheetNames.forEach(name => { // undefined!
```
**Стало:**
```javascript
const dataSheets = findDataSheets(); // правильно
dataSheets.forEach(name => {
```

### 2. ❌ → ✅ Удален устаревший `scan_data_funnel.py`
- Конфликтовал с новой логикой
- Не использовался

### 3. ✅ Создан новый `daily_analyzer_with_algorithm.py`
- Интеграция с Algorithm
- Автоопределение листов месяцев
- Запись в Signals/Decisions
- Полная совместимость с Apps Script

## 📝 Формат правил в Algorithm

### Структура листа Algorithm:
| RuleId | Block | Metric | ConditionType | ConditionParams | ActionType | ActionParams | Severity | AutoApply | Active |
|--------|-------|--------|---------------|-----------------|------------|--------------|----------|-----------|--------|
| R001 | funnel | Конверсия в корзину, % | ratio | `{"drop_pct":0.15,"min_samples":5}` | price_adjust | {...} | high | N | Y |

### Пример правила:
- **RuleId:** R001
- **Metric:** Конверсия в корзину, %
- **ConditionParams:** 
  - `drop_pct: 0.15` - порог падения 15%
  - `min_samples: 5` - минимум 5 дней данных
- **ActionType:** price_adjust (корректировка цены)
- **Severity:** high (высокая критичность)
- **Active:** Y (правило активно)

## 🎯 Workflow агента

### Ежедневный автоматический цикл (9:00):

1. **Apps Script сканирует:**
   - Находит все листы месяцев
   - Загружает правила из Algorithm
   - Сравнивает последние 2 даты
   - Находит отклонения по правилам
   - Записывает в Signals и Decisions
   - Подсвечивает проблемные ячейки

2. **Пользователь проверяет:**
   - Открывает саммари изменений
   - Просматривает Signals
   - Одобряет/отклоняет Decisions

3. **Python анализатор (опционально):**
   - Более детальный анализ
   - MD отчеты
   - Git автоматизация

## 🔄 Автозапуск

### Windows Task Scheduler (для Python)
```bash
# Настройка автозапуска в 10:00
.\setup_scheduler.ps1

# Ручной запуск для теста
.\run_daily_analysis.bat
```

### Apps Script триггер
Настраивается через меню "🔄 Настроить расписание" (9:00 каждый день)

## 📂 Структура проекта

```
demoAIagent/
├── src/
│   ├── ai_agent/
│   │   ├── google/
│   │   │   ├── auth.py              # Аутентификация Google API
│   │   │   └── sheets.py            # Работа с Sheets
│   │   ├── jobs/
│   │   │   ├── august_daily_analyzer.py           # Старый анализатор
│   │   │   └── daily_analyzer_with_algorithm.py   # ✨ Новый с Algorithm
│   │   └── config.py                # Конфигурация
│   └── apps-script/
│       └── enhanced-agent.gs        # ✨ Исправленный Apps Script
│
├── reports/                         # Автогенерируемые отчеты
├── docs/                            # Документация
├── .env                             # Конфигурация (не в Git)
├── google-service-account.json      # Ключ доступа (не в Git)
├── pyproject.toml                   # Poetry зависимости
├── requirements.txt                 # pip зависимости
└── README-v1.0.md                   # ✨ Эта документация
```

## 🛠️ Технологии

**Backend:**
- Python 3.9+
- Poetry для управления зависимостей
- Google Sheets API
- Google Apps Script

**Интеграции:**
- MCP (Model Context Protocol) для Cursor
- Git для версионирования отчетов

## 📊 Метрики версии 1.0

✅ **Функциональность:**
- 2 способа анализа (Apps Script + Python)
- Интеграция с Algorithm
- Автоматическое определение листов
- Запись в Signals/Decisions
- Боковая панель для управления

✅ **Автоматизация:**
- Apps Script триггер (9:00)
- Task Scheduler (10:00)
- Git автоматизация

✅ **Баги исправлены:**
- clearAllHighlights() фикс
- Удален устаревший код
- Создан новый интегрированный анализатор

## 🚀 Что дальше (v1.5)

- [ ] Telegram уведомления
- [ ] Расширенная аналитика (тренды)
- [ ] Интеграция с tl;dv (анализ созвонов)
- [ ] Автоприменение действий (с подтверждением)

## 📞 Поддержка

**Основные команды:**
```bash
# Анализ с Algorithm
poetry run python src/ai_agent/jobs/daily_analyzer_with_algorithm.py

# Старый анализатор
poetry run python src/ai_agent/jobs/august_daily_analyzer.py

# Через MCP в Cursor
# Просто спросите AI: "Проанализируй данные"
```

**Документация:**
- `БЫСТРЫЙ-СТАРТ.md` - быстрый старт
- `ИНСТРУКЦИЯ-ПО-РАБОТЕ.md` - инструкция пользователя
- `АВТОЗАПУСК-ГОТОВ.md` - настройка автозапуска
- `MVP-ИТОГ.md` - итоги MVP

---

**Версия:** 1.0  
**Дата:** 2025-10-15  
**Статус:** ✅ Готово к использованию

**GitHub:** https://github.com/EvgeniyRibakov/demoAIagent

