"""
Job для обработки транскриптов из Google Drive
"""

import sys
import traceback
from typing import List, Dict, Any

from ai_agent.config import config
from ai_agent.google.auth import google_auth
from ai_agent.google.drive import drive
from ai_agent.google.sheets import sheets
from ai_agent.llm.extract import llm_extractor


def main():
    """Основная функция обработки транскриптов"""
    print("INFO: Запуск обработки транскриптов из Google Drive...\n")
    
    try:
        # Проверяем конфигурацию
        if not config.validate():
            print("ERROR: Неверная конфигурация. Проверьте .env файл")
            return False
        
        # Проверяем наличие папки Calls
        if not config.GOOGLE_DRIVE_CALLS_FOLDER_ID:
            print("ERROR: GOOGLE_DRIVE_CALLS_FOLDER_ID не настроен")
            print("INFO: Создайте папку 'Calls' в Google Drive и укажите её ID в .env")
            return False
        
        # Аутентификация
        if not google_auth.authenticate():
            print("ERROR: Ошибка аутентификации в Google API")
            return False
        
        # Получаем список файлов транскриптов
        print("📁 Получаем список файлов из папки Calls...")
        transcript_files = drive.get_transcripts_from_calls_folder()
        
        if not transcript_files:
            print("ℹ️ Новых транскриптов не найдено")
            return True
        
        print(f"📄 Найдено {len(transcript_files)} файлов для обработки")
        
        # Загружаем содержимое файлов
        transcripts_data = []
        for file_info in transcript_files:
            content = drive.process_transcript_file(file_info)
            if content:
                transcripts_data.append({
                    "filename": file_info["name"],
                    "content": content,
                    "modified_time": file_info["modifiedTime"]
                })
        
        if not transcripts_data:
            print("WARNING: Не удалось загрузить ни одного транскрипта")
            return False
        
        # Получаем превью алгоритма для контекста
        print("INFO: Получаем информацию об алгоритме...")
        algorithm_data = sheets.read_range("Algorithm", "A2:L1000")
        algorithm_preview = "\n".join([
            f"Правило {row[0]}: {row[2]} ({row[3]}) → {row[5]}"
            for row in algorithm_data if len(row) >= 6
        ])
        
        # Извлекаем предложения через LLM
        print("INFO: Обрабатываем транскрипты через LLM...")
        proposals = llm_extractor.extract_from_multiple_transcripts(
            transcripts_data, 
            algorithm_preview
        )
        
        if not proposals:
            print("ℹ️ Предложений для добавления не найдено")
            return True
        
        # Записываем предложения в Google Sheets
        print("INFO: Записываем предложения в лист Proposals...")
        
        proposals_rows = []
        for proposal in proposals:
            row = [
                proposal.call_date,
                proposal.extracted_case,
                "Y" if proposal.existing_rule_matched else "N",
                proposal.suggested_rule_diff,
                proposal.confidence,
                proposal.status,
                proposal.notes,
                proposal.rule_id
            ]
            proposals_rows.append(row)
        
        success = sheets.append_rows("Proposals", proposals_rows)
        
        if success:
            print(f"SUCCESS: Успешно добавлено {len(proposals)} предложений в лист Proposals")
            
            # Показываем статистику
            new_proposals = [p for p in proposals if not p.existing_rule_matched]
            existing_proposals = [p for p in proposals if p.existing_rule_matched]
            
            print(f"\nINFO: Статистика:")
            print(f"  - Новых предложений: {len(new_proposals)}")
            print(f"  - По существующим правилам: {len(existing_proposals)}")
            print(f"  - Средняя уверенность: {sum(p.confidence for p in proposals) / len(proposals):.2f}")
            
            return True
        else:
            print("ERROR: Ошибка записи предложений в Google Sheets")
            return False
    
    except Exception as e:
        print(f"ERROR: Критическая ошибка: {e}")
        print(f"INFO: Детали ошибки:")
        traceback.print_exc()
        return False


def test_connection():
    """Тестирует подключение к сервисам"""
    print("INFO: Тестирование подключений...")
    
    # Тест Google API
    if not google_auth.authenticate():
        print("ERROR: Google API: Ошибка")
        return False
    print("SUCCESS: Google API: OK")
    
    # Тест Google Sheets
    info = sheets.get_spreadsheet_info()
    if info:
        print(f"SUCCESS: Google Sheets: OK ({info['title']})")
    else:
        print("ERROR: Google Sheets: Ошибка")
        return False
    
    # Тест Google Drive
    if config.GOOGLE_DRIVE_CALLS_FOLDER_ID:
        files = drive.list_files_in_folder(config.GOOGLE_DRIVE_CALLS_FOLDER_ID)
        print(f"SUCCESS: Google Drive: OK ({len(files)} файлов в папке)")
    else:
        print("WARNING: Google Drive: Не настроен")
    
    # Тест OpenAI
    if llm_extractor.client:
        print("SUCCESS: OpenAI: OK")
    else:
        print("ERROR: OpenAI: Ошибка")
        return False
    
    print("SUCCESS: Все тесты пройдены!")
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Обработка транскриптов из Google Drive")
    parser.add_argument("--test", action="store_true", help="Только тестирование подключений")
    
    args = parser.parse_args()
    
    if args.test:
        success = test_connection()
    else:
        success = main()
    
    sys.exit(0 if success else 1)
