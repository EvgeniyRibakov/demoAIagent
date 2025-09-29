#!/usr/bin/env python3
"""
Скрипт для тестирования соединений с Google API и OpenAI API
"""

import sys
import os
from pathlib import Path

# Устанавливаем кодировку UTF-8 для Windows
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agent.config import config
from ai_agent.google.auth import GoogleAuth
from ai_agent.google.sheets import sheets
from ai_agent.google.drive import drive
from ai_agent.llm.extract import LLMExtractor


def test_config():
    """Тестирует конфигурацию приложения"""
    print("INFO: Проверка конфигурации...")
    
    if not config.validate():
        print("ERROR: Конфигурация неверна")
        return False
    
    print("SUCCESS: Конфигурация корректна")
    return True


def test_google_auth():
    """Тестирует аутентификацию в Google API"""
    print("\nINFO: Тестирование Google API аутентификации...")
    
    auth = GoogleAuth()
    if not auth.authenticate():
        print("ERROR: Ошибка аутентификации в Google API")
        return False
    
    print("SUCCESS: Google API аутентификация успешна")
    return True


def test_google_sheets():
    """Тестирует соединение с Google Sheets"""
    print("\nINFO: Тестирование Google Sheets...")
    
    try:
        # Пробуем получить информацию о таблице
        spreadsheet_info = sheets.get_spreadsheet_info()
        if spreadsheet_info and spreadsheet_info.get('title'):
            print(f"SUCCESS: Подключение к Google Sheets успешно")
            print(f"   Название: {spreadsheet_info.get('title', 'Неизвестно')}")
            print(f"   ID: {config.GOOGLE_SHEETS_ID}")
            print(f"   Листы: {', '.join(spreadsheet_info.get('sheets', []))}")
            return True
        else:
            print("ERROR: Не удалось получить данные таблицы")
            return False
            
    except Exception as e:
        print(f"ERROR: Ошибка при работе с Google Sheets: {e}")
        return False


def test_google_drive():
    """Тестирует соединение с Google Drive"""
    print("\nINFO: Тестирование Google Drive...")
    
    try:
        # Пробуем получить информацию о папке с звонками
        if config.GOOGLE_DRIVE_CALLS_FOLDER_ID:
            folder = drive.get_folder_info(config.GOOGLE_DRIVE_CALLS_FOLDER_ID)
            if folder:
                print(f"SUCCESS: Подключение к Google Drive успешно")
                print(f"   Папка звонков: {folder.get('name', 'Неизвестно')}")
                return True
            else:
                print("ERROR: Не удалось получить данные папки звонков")
                return False
        else:
            print("WARNING: GOOGLE_DRIVE_CALLS_FOLDER_ID не настроен")
            return True
            
    except Exception as e:
        print(f"ERROR: Ошибка при работе с Google Drive: {e}")
        return False


def test_openai():
    """Тестирует соединение с OpenAI API"""
    print("\nINFO: Тестирование OpenAI API...")
    
    if not config.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY не настроен")
        return False
    
    try:
        extractor = LLMExtractor()
        
        # Простой тест с коротким запросом
        test_text = "Тест соединения с OpenAI API"
        result = extractor.extract_proposals(test_text)
        
        if result:
            print("SUCCESS: OpenAI API работает корректно")
            return True
        else:
            print("ERROR: OpenAI API вернул пустой результат")
            return False
            
    except Exception as e:
        print(f"ERROR: Ошибка при работе с OpenAI API: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("INFO: Тестирование соединений AI-агента\n")
    
    tests = [
        ("Конфигурация", test_config),
        ("Google Auth", test_google_auth),
        ("Google Sheets", test_google_sheets),
        ("Google Drive", test_google_drive),
        ("OpenAI API", test_openai),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR: Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "="*50)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "SUCCESS: ПРОЙДЕН" if result else "ERROR: ПРОВАЛЕН"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("SUCCESS: Все тесты пройдены успешно!")
        return 0
    else:
        print("WARNING: Некоторые тесты не пройдены. Проверьте настройки.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
