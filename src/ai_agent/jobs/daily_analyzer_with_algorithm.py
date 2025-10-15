#!/usr/bin/env python3
"""
Улучшенный анализатор ежедневных изменений с интеграцией Algorithm
Версия: 1.0
Дата: 2025-10-15

Особенности:
- Работает с любым листом месяца (автоопределение)
- Использует правила из листа Algorithm
- Создает записи в Signals и Decisions
- Совместим с Google Apps Script
"""

import sys
from pathlib import Path
from datetime import datetime
import re
import json
from typing import Dict, List, Tuple, Optional

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agent.google.sheets import sheets
from ai_agent.config import config

class DailyAnalyzerWithAlgorithm:
    """Анализатор ежедневных изменений с интеграцией листа Algorithm"""
    
    def __init__(self, sheet_name: str = None):
        """
        Args:
            sheet_name: Название листа для анализа. Если None, использует последний найденный лист месяца
        """
        self.sheet_name = sheet_name
        self.anomalies = []
        self.rules = []
        self.today_date_str = None
        self.yesterday_date_str = None
        
        # Явно устанавливаем SPREADSHEET_ID если не задан
        if not sheets.spreadsheet_id or sheets.spreadsheet_id == '':
            sheets.spreadsheet_id = "18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ"
            print("INFO: Использую SPREADSHEET_ID из кода")
    
    def find_month_sheets(self) -> List[str]:
        """Находит все листы с данными по паттерну 'Месяц Год'"""
        try:
            # Получаем информацию о таблице
            service = sheets._get_service()
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=sheets.spreadsheet_id
            ).execute()
            
            # Паттерн для листов месяцев (январь-декабрь + год)
            month_pattern = re.compile(
                r'^(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)\s+\d{4}$',
                re.IGNORECASE
            )
            
            month_sheets = []
            for sheet in spreadsheet['sheets']:
                sheet_name = sheet['properties']['title']
                if month_pattern.match(sheet_name):
                    month_sheets.append(sheet_name)
            
            return month_sheets
            
        except Exception as e:
            print(f"ERROR: Ошибка при поиске листов месяцев: {e}")
            return []
    
    def load_rules(self) -> List[Dict]:
        """Загружает активные правила из листа Algorithm"""
        try:
            print("INFO: Загружаем правила из Algorithm...")
            rules_data = sheets.read_range("Algorithm", "A1:L100")
            
            if not rules_data or len(rules_data) < 2:
                print("WARNING: Нет правил в листе Algorithm")
                return []
            
            headers = rules_data[0]
            rules = []
            
            for row in rules_data[1:]:
                if not row or len(row) < 6:
                    continue
                
                # Проверяем активность правила
                active = str(row[9]).strip().upper() == 'Y' if len(row) > 9 else False
                if not active:
                    continue
                
                # Парсим JSON параметры
                try:
                    condition_params = json.loads(row[4]) if len(row) > 4 and row[4] else {}
                except:
                    condition_params = {}
                
                rule = {
                    'rule_id': str(row[0]).strip(),
                    'block': str(row[1]).strip(),
                    'metric': str(row[2]).strip(),
                    'condition_type': str(row[3]).strip() if len(row) > 3 else 'ratio',
                    'condition_params': condition_params,
                    'action_type': str(row[5]).strip(),
                    'action_params': str(row[6]).strip() if len(row) > 6 else '',
                    'severity': str(row[7]).strip() if len(row) > 7 else 'medium',
                    'drop_pct': condition_params.get('drop_pct', 0.15),
                    'min_samples': condition_params.get('min_samples', 5)
                }
                
                rules.append(rule)
            
            print(f"INFO: Загружено {len(rules)} активных правил")
            self.rules = rules
            return rules
            
        except Exception as e:
            print(f"ERROR: Ошибка при загрузке правил: {e}")
            return []
    
    def parse_number(self, value):
        """Парсит число из строки с учетом форматирования"""
        if not value or value == '' or str(value).strip() == '':
            return None
            
        # Убираем все виды пробелов и заменяем запятые на точки
        clean_value = str(value).replace(' ', '').replace('\xa0', '').replace(',', '.')
        
        # Убираем % если есть
        clean_value = clean_value.replace('%', '')
        
        # Извлекаем число
        match = re.search(r'-?\d+\.?\d*', clean_value)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None
    
    def match_rule(self, metric_name: str, delta_pct: float, baseline_values: List[float]) -> Optional[Dict]:
        """Находит подходящее правило для метрики"""
        for rule in self.rules:
            # Проверяем совпадение имени метрики
            if rule['metric'] != metric_name:
                continue
            
            # Проверяем условие
            if rule['condition_type'] == 'ratio':
                # Проверяем минимальное количество образцов
                if len(baseline_values) < rule['min_samples']:
                    continue
                
                # Проверяем падение (delta_pct отрицательно при падении)
                if delta_pct <= -rule['drop_pct']:
                    return rule
        
        return None
    
    def find_date_columns(self, headers: List) -> List[Tuple[int, str]]:
        """Находит колонки с датами в заголовках"""
        date_columns = []
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{2,4}'
        
        for i, header in enumerate(headers):
            if not header:
                continue
            
            header_str = str(header).strip()
            match = re.search(date_pattern, header_str)
            if match:
                date_columns.append((i, match.group()))
        
        return date_columns
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из строки"""
        try:
            for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def find_last_two_dates(self, date_columns: List[Tuple[int, str]]) -> Tuple[Optional[int], Optional[int]]:
        """Находит две последние даты"""
        if len(date_columns) < 2:
            return None, None
        
        parsed_dates = []
        for col_idx, date_str in date_columns:
            date_obj = self.parse_date(date_str)
            if date_obj:
                parsed_dates.append((col_idx, date_obj, date_str))
        
        if len(parsed_dates) < 2:
            return None, None
        
        # Сортируем по дате
        parsed_dates.sort(key=lambda x: x[1])
        
        # Берем две последние
        today_col = parsed_dates[-1][0]
        yesterday_col = parsed_dates[-2][0]
        
        self.today_date_str = parsed_dates[-1][2]
        self.yesterday_date_str = parsed_dates[-2][2]
        
        print(f"INFO: Найдены даты - Сегодня: {self.today_date_str}, Вчера: {self.yesterday_date_str}")
        
        return today_col, yesterday_col
    
    def analyze_sheet(self, sheet_name: str) -> Dict:
        """Анализирует один лист"""
        print(f"\nINFO: Анализируем лист '{sheet_name}'...")
        
        try:
            # Читаем данные
            data = sheets.read_range(sheet_name, "A1:ZZ200")
            
            if not data or len(data) < 3:
                print("WARNING: Недостаточно данных")
                return {'success': False, 'error': 'Недостаточно данных'}
            
            headers = data[0]
            
            # Находим даты
            date_columns = self.find_date_columns(headers)
            if len(date_columns) < 2:
                return {'success': False, 'error': 'Недостаточно дат'}
            
            today_col, yesterday_col = self.find_last_two_dates(date_columns)
            if today_col is None or yesterday_col is None:
                return {'success': False, 'error': 'Не удалось определить даты'}
            
            # Анализируем метрики
            anomalies = []
            
            for row_idx, row in enumerate(data[2:], start=3):
                if not row or len(row) <= max(today_col, yesterday_col):
                    continue
                
                metric_name = str(row[0]).strip() if len(row) > 0 else ""
                if not metric_name:
                    continue
                
                # Получаем значения
                today_value = self.parse_number(row[today_col]) if today_col < len(row) else None
                yesterday_value = self.parse_number(row[yesterday_col]) if yesterday_col < len(row) else None
                
                if today_value is None or yesterday_value is None:
                    continue
                
                if today_value == 0 and yesterday_value == 0:
                    continue
                
                # Вычисляем изменение
                if yesterday_value == 0:
                    change_pct = 100 if today_value > 0 else 0
                else:
                    change_pct = ((today_value - yesterday_value) / abs(yesterday_value)) * 100
                
                delta_pct = change_pct / 100  # Переводим в десятичное
                
                # Проверяем правило
                baseline_values = [yesterday_value]  # Упрощенно
                rule = self.match_rule(metric_name, delta_pct, baseline_values)
                
                if rule:
                    anomaly = {
                        'sheet': sheet_name,
                        'row': row_idx,
                        'col_today': today_col,
                        'metric': metric_name,
                        'yesterday_value': yesterday_value,
                        'today_value': today_value,
                        'change_pct': round(change_pct, 2),
                        'delta_pct': delta_pct,
                        'rule_id': rule['rule_id'],
                        'action_type': rule['action_type'],
                        'severity': rule['severity'],
                        'direction': '⬆️' if change_pct > 0 else '⬇️'
                    }
                    
                    anomalies.append(anomaly)
                    print(f"INFO: Найдено отклонение - {metric_name}: {change_pct:+.1f}% (правило: {rule['rule_id']})")
            
            self.anomalies.extend(anomalies)
            
            return {
                'success': True,
                'anomalies': anomalies,
                'sheet_name': sheet_name
            }
            
        except Exception as e:
            print(f"ERROR: Ошибка при анализе: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def save_to_signals(self):
        """Сохраняет аномалии в лист Signals"""
        if not self.anomalies:
            print("INFO: Нет аномалий для сохранения")
            return
        
        try:
            print(f"INFO: Сохраняем {len(self.anomalies)} сигналов в Signals...")
            
            rows = []
            for anomaly in self.anomalies:
                row = [
                    datetime.now().isoformat(),  # Timestamp
                    '',  # Block (можно добавить)
                    anomaly['metric'],
                    self.today_date_str,
                    anomaly['today_value'],
                    anomaly['yesterday_value'],
                    anomaly['change_pct'],
                    anomaly['rule_id'],
                    'new',  # Status
                    f"{anomaly['sheet']}!{anomaly['row']}",  # Link
                    anomaly['severity']
                ]
                rows.append(row)
            
            sheets.append_rows("Signals", rows)
            print("SUCCESS: Сигналы сохранены")
            
        except Exception as e:
            print(f"ERROR: Ошибка при сохранении сигналов: {e}")
    
    def save_to_decisions(self):
        """Сохраняет решения в лист Decisions"""
        if not self.anomalies:
            return
        
        try:
            print(f"INFO: Сохраняем {len(self.anomalies)} решений в Decisions...")
            
            rows = []
            for i, anomaly in enumerate(self.anomalies, 1):
                signal_id = f"S{datetime.now().strftime('%Y%m%d')}{i:03d}"
                rationale = f"Падение на {abs(anomaly['change_pct']):.1f}% (правило: {anomaly['rule_id']})"
                
                row = [
                    signal_id,  # SignalId
                    anomaly['action_type'],  # SuggestedActionType
                    '',  # ActionParams
                    rationale,  # Rationale
                    'pending',  # Status
                    '',  # ApprovedBy
                    '',  # AppliedAt
                    '',  # AuditLog
                    0.8  # Confidence
                ]
                rows.append(row)
            
            sheets.append_rows("Decisions", rows)
            print("SUCCESS: Решения сохранены")
            
        except Exception as e:
            print(f"ERROR: Ошибка при сохранении решений: {e}")
    
    def run(self):
        """Запускает полный цикл анализа"""
        print("=" * 60)
        print("АНАЛИЗ С ИНТЕГРАЦИЕЙ ALGORITHM")
        print("=" * 60)
        
        # Загружаем правила
        if not self.load_rules():
            print("ERROR: Не удалось загрузить правила из Algorithm")
            return False
        
        # Определяем лист для анализа
        if not self.sheet_name:
            month_sheets = self.find_month_sheets()
            if not month_sheets:
                print("ERROR: Не найдены листы месяцев")
                return False
            self.sheet_name = month_sheets[-1]  # Берем последний
            print(f"INFO: Автоматически выбран лист: {self.sheet_name}")
        
        # Анализируем
        result = self.analyze_sheet(self.sheet_name)
        
        if not result['success']:
            print(f"ERROR: {result.get('error')}")
            return False
        
        # Сохраняем результаты
        self.save_to_signals()
        self.save_to_decisions()
        
        print("\n" + "=" * 60)
        print("АНАЛИЗ ЗАВЕРШЕН")
        print("=" * 60)
        print(f"Найдено отклонений: {len(self.anomalies)}")
        print(f"Использовано правил: {len(self.rules)}")
        
        return True

def main():
    """Основная функция"""
    analyzer = DailyAnalyzerWithAlgorithm()
    analyzer.run()

if __name__ == "__main__":
    main()

