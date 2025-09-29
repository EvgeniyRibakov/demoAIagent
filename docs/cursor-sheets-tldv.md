## Связка Cursor ↔ Google Sheets/Drive ↔ tl;dv

### Что получится
- Apps Script в таблице: подсветка отклонений и предложения (Этап 1).
- Node‑скрипт в репозитории: забирает транскрипты из папки Drive `Calls`, извлекает «новые» решения через LLM и пишет их в лист `Proposals` (Этап 2).
- Дальше действия по апруву: интеграции с маркетплейсом/тикетами (Этап 3).

### Настройка tl;dv → Drive
1. В tl;dv включите автосохранение транскриптов в Google Drive (или экспортируйте вручную в TXT/Google Doc).
2. Создайте папку в Drive, назовите `Calls`, положите туда транскрипты. Скопируйте `folderId` из URL.
3. Убедитесь, что сервис‑аккаунт Google имеет доступ «Viewer» к этой папке (или доступ на весь Диск).

### Настройка сервис‑аккаунта Google
1. Создайте сервис‑аккаунт в Google Cloud (IAM → Service Accounts). Скачайте JSON‑ключ.
2. В `.env` пропишите `GOOGLE_CLIENT_EMAIL` и `GOOGLE_PRIVATE_KEY`.
3. Дайте доступ сервис‑аккаунту на таблицу (Share → email сервис‑аккаунта как Editor). Также дайте доступ к папке `Calls`.

### Переменные окружения (.env)
Скопируйте `.env.example` → `.env` и заполните:
- `GOOGLE_SHEETS_ID` — ID вашей таблицы.
- `GOOGLE_DRIVE_CALLS_FOLDER_ID` — ID папки `Calls`.
- `OPENAI_API_KEY` — ключ OpenAI. `OPENAI_MODEL` можно оставить по умолчанию `gpt-4o-mini`.

### Сборка и запуск в Cursor
1. Откройте проект в Cursor. Установите зависимости:
   - В терминале: `npm install`
2. Соберите TypeScript: `npm run build`
3. Запустите задачу Этапа 2: `npm run proposals:from-drive`
   - Скрипт прочитает новые файлы в `Calls`, извлечёт предложения и добавит строки в `Proposals`.

### Привязка к Apps Script (Этап 1)
- В таблице добавьте скрипт из инструкций (меню Agent → Scan signals). Лист `Proposals` создайте/проверьте.
- Node‑скрипт пишет в `Proposals`, менеджер видит кандидатов и апрувит/реджектит.

### Советы по эксплуатации
- Работайте в режиме dry‑run: новые правила только через апрув.
- Храните историю в `Proposals`/`Decisions`, добавляйте краткое обоснование (notes/rationale).
- Для высокой точности извлечения используйте короткую выжимку алгоритма в промпт (опционально — добавить чтение листа `Algorithm`).

### Ссылки
- Шаблон Google Таблицы: https://docs.google.com/spreadsheets/d/18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ/edit?usp=sharing


