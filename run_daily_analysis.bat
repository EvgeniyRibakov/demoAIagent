@echo off
REM Скрипт для ежедневного автоматического запуска анализа
REM Запускается через Windows Task Scheduler в 10:00 МСК

cd /d C:\Users\fisher\PycharmProjects\AI-agent_with_Cursor

REM Активируем виртуальное окружение Poetry и запускаем анализ
poetry run python src/ai_agent/jobs/august_daily_analyzer.py

REM Логируем результат
echo %date% %time% - Daily analysis completed >> logs\daily_analysis.log

