# PowerShell скрипт для настройки автоматического запуска анализа
# Запуск каждый день в 10:00 по московскому времени

$taskName = "AI-Agent Daily Analysis"
$scriptPath = "C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor\run_daily_analysis.bat"
$workingDir = "C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor"

Write-Host "Настройка автоматического запуска анализа..."
Write-Host ""

# Проверяем, существует ли задача
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "[INFO] Задача '$taskName' уже существует. Удаляем..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Создаем действие (запуск bat файла)
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Создаем триггер (каждый день в 10:00)
$trigger = New-ScheduledTaskTrigger -Daily -At "10:00"

# Создаем настройки задачи
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Создаем principal (запуск от имени текущего пользователя)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

# Регистрируем задачу
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Ежедневный анализ данных Google Sheets с автоматическим коммитом в GitHub (10:00 МСК)"

Write-Host ""
Write-Host "[SUCCESS] Задача '$taskName' успешно создана!"
Write-Host ""
Write-Host "Параметры:"
Write-Host "  - Время запуска: 10:00 (ежедневно)"
Write-Host "  - Скрипт: $scriptPath"
Write-Host "  - Рабочая папка: $workingDir"
Write-Host ""
Write-Host "Для просмотра задачи откройте: Планировщик заданий Windows"
Write-Host "Или выполните: Get-ScheduledTask -TaskName '$taskName'"
Write-Host ""
Write-Host "Для тестового запуска выполните:"
Write-Host "  Start-ScheduledTask -TaskName '$taskName'"

