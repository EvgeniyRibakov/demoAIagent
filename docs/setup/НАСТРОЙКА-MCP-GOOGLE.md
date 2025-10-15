# 🔧 Настройка MCP для Google сервисов

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

1. Откройте https://console.cloud.google.com/
2. Создайте новый проект `AI-Agent-MCP`
3. Выберите созданный проект

### Шаг 2: Включение необходимых API

- Google Sheets API
- Google Drive API
- Google Docs API
- Google Calendar API (опционально)

### Шаг 3: Создание Service Account

1. Перейдите в "IAM и администрирование" → "Service Accounts"
2. Создайте Service Account: `ai-agent-service`
3. Назначьте роли: Editor, Viewer

### Шаг 4: Создание ключей доступа

1. Найдите созданный Service Account
2. Создайте JSON ключ
3. Сохраните как `google-service-account.json` в корне проекта

### Шаг 5: Настройка .env

```env
GOOGLE_APPLICATION_CREDENTIALS=./google-service-account.json
GOOGLE_SHEETS_ID=your_sheets_id
OPENAI_API_KEY=sk-your-key
```

---

Перенесено в `docs/setup/` для организации проекта.
Полная инструкция доступна в оригинальном файле.

**Дата:** 2025-10-15

