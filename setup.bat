@echo off
echo 🚀 Настройка AI Agent проекта...
echo.

echo 🔍 Проверяем Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js не найден!
    echo 📥 Скачайте и установите Node.js с https://nodejs.org/
    echo Перезапустите терминал после установки
    pause
    exit /b 1
)

echo ✅ Node.js найден
node --version
npm --version
echo.

echo 📦 Устанавливаем зависимости...
npm install
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей
    pause
    exit /b 1
)

echo ✅ Зависимости установлены
echo.

echo 🔨 Собираем проект...
npm run build
if %errorlevel% neq 0 (
    echo ❌ Ошибка сборки проекта
    pause
    exit /b 1
)

echo ✅ Проект собран
echo.

echo 🎯 Настраиваем Google Sheets...
npm run setup:google
if %errorlevel% neq 0 (
    echo ❌ Ошибка настройки Google Sheets
    echo Проверьте .env файл
    pause
    exit /b 1
)

echo.
echo 🎉 Настройка завершена успешно!
echo.
echo 📋 Следующие шаги:
echo 1. Добавьте Apps Script в Google Таблицу
echo 2. Скопируйте код из src/apps-script/enhanced-agent.gs
echo 3. Появится меню "🤖 AI Agent"
echo.
pause
