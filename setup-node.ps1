# PowerShell скрипт для установки Node.js и настройки проекта

Write-Host "🚀 Настройка AI Agent проекта..." -ForegroundColor Green

# Проверяем, установлен ли Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js уже установлен: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js не найден. Устанавливаем..." -ForegroundColor Red
    
    # Скачиваем и устанавливаем Node.js
    $nodeUrl = "https://nodejs.org/dist/v20.10.0/node-v20.10.0-x64.msi"
    $nodeInstaller = "$env:TEMP\nodejs-installer.msi"
    
    Write-Host "📥 Скачиваем Node.js..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller
    
    Write-Host "🔧 Устанавливаем Node.js..." -ForegroundColor Yellow
    Start-Process msiexec.exe -Wait -ArgumentList "/i $nodeInstaller /quiet"
    
    # Обновляем PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Host "✅ Node.js установлен! Перезапустите терминал." -ForegroundColor Green
    Write-Host "Затем выполните: npm install" -ForegroundColor Cyan
    exit
}

# Проверяем npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm найден: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm не найден. Переустановите Node.js." -ForegroundColor Red
    exit 1
}

# Устанавливаем зависимости
Write-Host "📦 Устанавливаем зависимости..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Зависимости установлены!" -ForegroundColor Green
    
    # Собираем проект
    Write-Host "🔨 Собираем проект..." -ForegroundColor Yellow
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Проект собран!" -ForegroundColor Green
        
        Write-Host "`n🎉 Готово! Теперь выполните:" -ForegroundColor Green
        Write-Host "1. Настройте .env файл (скопируйте из .env.example)" -ForegroundColor Cyan
        Write-Host "2. Запустите: npm run setup:google" -ForegroundColor Cyan
        Write-Host "3. Следуйте инструкциям в docs/google-sheets-setup-guide.md" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Ошибка сборки проекта" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Ошибка установки зависимостей" -ForegroundColor Red
}
