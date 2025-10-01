#!/usr/bin/env python3
"""
Скрипт для проверки данных в листе Август 2025
"""

import sys
from pathlib import Path

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ai_agent.google.sheets import sheets

def main():
    print("Проверка данных в листе Август 2025...")
    
    try:
        # Читаем данные из листа Август 2025
        data = sheets.read_range('Август 2025', 'A1:Z50')
        print(f"Строк в листе: {len(data)}")
        
        if data:
            print("\nПервые 15 строк:")
            for i, row in enumerate(data[:15]):
                print(f"{i+1:2d}: {row}")
        else:
            print("Лист пустой")
            
        # Проверяем структуру данных
        if len(data) > 1:
            headers = data[0]
            print(f"\nЗаголовки ({len(headers)}): {headers}")
            
            # Ищем метрики
            metrics_found = []
            for i, row in enumerate(data[1:], 1):
                if len(row) > 1 and row[1]:  # Есть значение во втором столбце
                    metric = row[1] if len(row) > 1 else ""
                    if any(keyword in str(metric).lower() for keyword in ['конверсия', 'ctr', 'переходы', 'корзина', 'cr', 'показы']):
                        metrics_found.append((i+1, row))
            
            if metrics_found:
                print(f"\nНайдены метрики ({len(metrics_found)}):")
                for line_num, row in metrics_found[:10]:  # Показываем первые 10
                    print(f"  Строка {line_num}: {row}")
            else:
                print("\nМетрики не найдены в стандартном формате")
                
    except Exception as e:
        print(f"Ошибка чтения листа: {e}")

if __name__ == "__main__":
    main()

