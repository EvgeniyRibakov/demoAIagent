#!/usr/bin/env python3
"""
Скрипт для сканирования сигналов в листе Data_Funnel
Адаптирован под структуру: Дата, Метрика, Значение, Блок, Примечание
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import re

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agent.google.sheets import sheets
from ai_agent.config import config

class DataFunnelScanner:
    """Сканер сигналов для листа Data_Funnel"""
    
    def __init__(self):
        self.sheet_name = "Data_Funnel"
        self.signals = []
        self.decisions = []
        
    def parse_number(self, value):
        """Парсит число из строки с учетом форматирования"""
        if not value or value == '' or str(value).strip() == '':
            return None
            
        # Убираем все виды пробелов и заменяем запятые на точки
        clean_value = str(value).replace(' ', '').replace('\xa0', '').replace(',', '.')
        
        # Извлекаем все цифры подряд
        match = re.search(r'\d+', clean_value)
        if match:
            try:
                number_str = match.group()
                return float(number_str)
            except ValueError:
                return None
        return None
    
    def extract_metrics_data(self):
        """Извлекает данные метрик из листа Data_Funnel"""
        print(f"INFO: Читаем данные из листа {self.sheet_name}...")
        
        try:
            # Читаем весь лист
            data = sheets.read_range(self.sheet_name, "A1:Z100")
            
            if not data or len(data) < 2:
                print("WARNING: Нет данных в листе")
                return {}
            
            # Первая строка - заголовки
            headers = data[0]
            print(f"INFO: Заголовки: {headers}")
            
            # В Data_Funnel структура: Дата, Метрика, Значение, Блок, Примечание
            date_col = 0  # Колонка A - Дата
            metric_col = 1  # Колонка B - Метрика
            value_col = 2  # Колонка C - Значение
            block_col = 3  # Колонка D - Блок
            
            metrics_data = {}
            
            # Обрабатываем каждую строку с данными
            for row_idx, row in enumerate(data[1:], start=2):
                if not row or len(row) <= max(date_col, metric_col, value_col, block_col):
                    continue
                
                # Извлекаем данные из строки
                date_str = str(row[date_col]).strip()
                metric_name = str(row[metric_col]).strip()
                value_str = str(row[value_col]).strip()
                block = str(row[block_col]).strip() if len(row) > block_col else 'other'
                
                if not metric_name or not value_str or metric_name == '' or value_str == '':
                    continue
                
                # Парсим значение
                value = self.parse_number(value_str)
                if value is None:
                    continue
                
                # Парсим дату
                try:
                    if len(date_str) >= 10:
                        date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                    else:
                        date_obj = datetime.now()
                except:
                    date_obj = datetime.now()
                
                # Добавляем в данные метрики
                if metric_name not in metrics_data:
                    metrics_data[metric_name] = []
                
                metrics_data[metric_name].append({
                    'date': date_obj,
                    'value': value,
                    'block': block
                })
                
                print(f"INFO: Добавлено значение для {metric_name}: {value} ({block})")
            
            return metrics_data
            
        except Exception as e:
            print(f"ERROR: Ошибка при чтении данных: {e}")
            return {}
    
    def determine_block(self, metric_name):
        """Определяет блок метрики по названию"""
        metric_lower = metric_name.lower()
        
        # Более точное определение блоков
        if any(word in metric_lower for word in ['конверсия', 'корзина', 'переходы', 'cr', 'конверсия в корзину', 'положили в корзину']):
            return 'funnel'
        elif any(word in metric_lower for word in ['показы', 'ctr', 'клики', 'показ', 'показ']):
            return 'ads'
        else:
            return 'other'
    
    def calculate_baseline(self, values, days=7):
        """Вычисляет базовое значение за последние N дней"""
        if len(values) < days:
            return None
            
        recent_values = [v['value'] for v in values[-days:]]
        return sum(recent_values) / len(recent_values)
    
    def check_rule_conditions(self, metric_name, values, rule):
        """Проверяет условия правила для метрики"""
        if not values or len(values) < rule.get('min_samples', 5):
            return False
        
        # Вычисляем базовое значение
        baseline = self.calculate_baseline(values, rule.get('baseline_days', 7))
        if baseline is None:
            return False
        
        # Текущее значение - последнее
        current_value = values[-1]['value']
        
        # Проверяем условие падения
        drop_pct = rule.get('drop_pct', 0.15)
        if current_value < baseline * (1 - drop_pct):
            return {
                'current': current_value,
                'baseline': baseline,
                'drop_pct': ((baseline - current_value) / baseline) * 100,
                'rule_id': rule.get('rule_id', ''),
                'action_type': rule.get('action_type', ''),
                'severity': rule.get('severity', 'medium')
            }
        
        return False
    
    def load_rules(self):
        """Загружает правила из листа Algorithm"""
        try:
            print("INFO: Загружаем правила из Algorithm...")
            rules_data = sheets.read_range("Algorithm", "A1:Z50")
            
            if not rules_data or len(rules_data) < 2:
                print("WARNING: Нет правил в листе Algorithm")
                return []
            
            headers = rules_data[0]
            rules = []
            
            for row in rules_data[1:]:
                if not row or len(row) < 6:
                    continue
                
                # Парсим JSON параметры
                try:
                    condition_params = json.loads(row[4]) if row[4] else {}
                except:
                    condition_params = {}
                
                rule = {
                    'rule_id': str(row[0]).strip(),
                    'block': str(row[1]).strip(),
                    'metric': str(row[2]).strip(),
                    'condition_type': str(row[3]).strip(),
                    'condition_params': condition_params,
                    'action_type': str(row[5]).strip(),
                    'severity': str(row[7]).strip() if len(row) > 7 else 'medium',
                    'active': str(row[9]).strip().upper() == 'Y' if len(row) > 9 else True,
                    'min_samples': condition_params.get('min_samples', 5),
                    'drop_pct': condition_params.get('drop_pct', 0.15)
                }
                
                if rule['active']:
                    rules.append(rule)
            
            print(f"INFO: Загружено {len(rules)} активных правил")
            return rules
            
        except Exception as e:
            print(f"ERROR: Ошибка при загрузке правил: {e}")
            return []
    
    def scan_signals(self):
        """Сканирует сигналы в данных"""
        print("INFO: Начинаем сканирование сигналов...")
        
        # Загружаем данные
        metrics_data = self.extract_metrics_data()
        if not metrics_data:
            print("WARNING: Нет данных для анализа")
            return False
        
        # Загружаем правила
        rules = self.load_rules()
        if not rules:
            print("WARNING: Нет правил для анализа")
            return False
        
        # Сканируем каждую метрику
        signals_found = 0
        
        for metric_name, values in metrics_data.items():
            print(f"INFO: Анализируем метрику: {metric_name}")
            
            # Определяем блок метрики
            block = self.determine_block(metric_name)
            print(f"INFO: Блок метрики: {block}")
            
            # Ищем подходящие правила
            matching_rules = [r for r in rules if r['block'] == block and r['metric'] == metric_name]
            
            if not matching_rules:
                print(f"INFO: Нет правил для метрики {metric_name} (блок: {block})")
                continue
            
            print(f"INFO: Найдено {len(matching_rules)} правил для метрики {metric_name}")
            
            # Проверяем каждое правило
            for rule in matching_rules:
                print(f"DEBUG: Проверяем правило {rule['rule_id']}: {rule['metric']} (блок: {rule['block']})")
                
                condition_result = self.check_rule_conditions(metric_name, values, rule)
                
                if condition_result:
                    signal = {
                        'timestamp': datetime.now().isoformat(),
                        'block': block,
                        'metric': metric_name,
                        'date': values[-1]['date'].strftime('%Y-%m-%d'),
                        'current_value': condition_result['current'],
                        'baseline_value': condition_result['baseline'],
                        'delta_pct': condition_result['drop_pct'],
                        'rule_id': condition_result['rule_id'],
                        'status': 'new',
                        'link_to_cell': f"{self.sheet_name}!C{values[-1].get('row_idx', 2)}",
                        'severity': condition_result['severity']
                    }
                    
                    self.signals.append(signal)
                    signals_found += 1
                    
                    print(f"INFO: Найден сигнал: {metric_name} упала на {condition_result['drop_pct']:.2f}%")
        
        print(f"INFO: Найдено {signals_found} сигналов")
        return signals_found > 0
    
    def save_signals(self):
        """Сохраняет найденные сигналы в лист Signals"""
        if not self.signals:
            print("INFO: Нет сигналов для сохранения")
            return
        
        try:
            print(f"INFO: Сохраняем {len(self.signals)} сигналов в лист Signals...")
            
            # Подготавливаем данные для записи
            signals_data = []
            for signal in self.signals:
                signals_data.append([
                    signal['timestamp'],
                    signal['block'],
                    signal['metric'],
                    signal['date'],
                    signal['current_value'],
                    signal['baseline_value'],
                    signal['delta_pct'],
                    signal['rule_id'],
                    signal['status'],
                    signal['link_to_cell'],
                    signal['severity']
                ])
            
            # Записываем в лист Signals
            sheets.append_rows("Signals", signals_data)
            print("INFO: Сигналы успешно сохранены")
            
        except Exception as e:
            print(f"ERROR: Ошибка при сохранении сигналов: {e}")

def main():
    """Основная функция"""
    scanner = DataFunnelScanner()
    
    if scanner.scan_signals():
        scanner.save_signals()
        print("SUCCESS: Сканирование завершено успешно")
    else:
        print("INFO: Сигналы не найдены")

if __name__ == "__main__":
    main()
