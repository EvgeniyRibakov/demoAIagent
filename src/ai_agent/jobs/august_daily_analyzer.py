#!/usr/bin/env python3
"""
Анализатор ежедневных изменений для листа "Август 2025"
Структура данных: 
- Строка 1-2: Заголовки (даты и описание)
- Строки 3+: Метрики по товарам
- Каждый день добавляется 3 новых столбца справа (дата1, дата2, дата3)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional

# Добавляем корневую папку проекта в путь
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agent.google.sheets import sheets
from ai_agent.config import config

class AugustDailyAnalyzer:
    """Анализатор ежедневных изменений для листа Август 2025"""
    
    def __init__(self):
        self.sheet_name = "Август 2025"
        self.anomalies = []
        
        # Явно устанавливаем SPREADSHEET_ID если не задан
        if not sheets.spreadsheet_id or sheets.spreadsheet_id == '':
            sheets.spreadsheet_id = "18otXyOlqG4FAbLqyZReCwSPkKLGuhEWsVKFNoxctyvQ"
            print("INFO: Использую SPREADSHEET_ID из кода")
        
        # Пороги отклонений по типам метрик (в процентах)
        self.thresholds = {
            'critical': {  # Красный цвет - критично
                'keywords': ['cr', 'конверсия', 'заказы', 'm3', 'выручка', 'прибыль'],
                'threshold': 10  # 10% изменение
            },
            'important': {  # Желтый цвет - важно
                'keywords': ['ctr', 'клики', 'добавления', 'корзина', 'переходы', 'показы'],
                'threshold': 15  # 15% изменение
            },
            'normal': {  # Зеленый цвет - норма
                'keywords': ['*'],  # все остальные
                'threshold': 20  # 20% изменение
            }
        }
    
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
    
    def classify_metric(self, metric_name: str) -> str:
        """Определяет критичность метрики"""
        metric_lower = metric_name.lower()
        
        for category in ['critical', 'important']:
            keywords = self.thresholds[category]['keywords']
            if any(keyword in metric_lower for keyword in keywords):
                return category
        
        return 'normal'
    
    def get_threshold(self, metric_name: str) -> float:
        """Возвращает порог отклонения для метрики"""
        category = self.classify_metric(metric_name)
        return self.thresholds[category]['threshold']
    
    def find_date_columns(self, headers: List) -> List[Tuple[int, str]]:
        """Находит колонки с датами в заголовках
        
        Returns:
            List[Tuple[int, str]]: Список (индекс_колонки, дата_строка)
        """
        date_columns = []
        
        # Паттерн для дат: DD.MM.YYYY или DD.MM.YY
        date_pattern = r'\d{1,2}\.\d{1,2}\.\d{2,4}'
        
        for i, header in enumerate(headers):
            if not header:
                continue
            
            header_str = str(header).strip()
            # Ищем дату в заголовке
            match = re.search(date_pattern, header_str)
            if match:
                date_columns.append((i, match.group()))
        
        return date_columns
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из строки"""
        try:
            # Пробуем разные форматы
            for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def find_last_two_dates(self, date_columns: List[Tuple[int, str]]) -> Tuple[Optional[int], Optional[int]]:
        """Находит две последние даты (сегодня и вчера)
        
        Returns:
            Tuple[Optional[int], Optional[int]]: (индекс_сегодня, индекс_вчера)
        """
        if len(date_columns) < 2:
            return None, None
        
        # Парсим даты и сортируем
        parsed_dates = []
        for col_idx, date_str in date_columns:
            date_obj = self.parse_date(date_str)
            if date_obj:
                parsed_dates.append((col_idx, date_obj, date_str))
        
        if len(parsed_dates) < 2:
            return None, None
        
        # Сортируем по дате (самая свежая в конце)
        parsed_dates.sort(key=lambda x: x[1])
        
        # Берем две последние
        today_col = parsed_dates[-1][0]
        yesterday_col = parsed_dates[-2][0]
        
        print(f"INFO: Найдены даты - Сегодня: колонка {today_col} ({parsed_dates[-1][2]}), "
              f"Вчера: колонка {yesterday_col} ({parsed_dates[-2][2]})")
        
        return today_col, yesterday_col
    
    def analyze_daily_changes(self) -> Dict:
        """Анализирует изменения между сегодня и вчера
        
        Returns:
            Dict: Результаты анализа с аномалиями
        """
        print(f"INFO: Начинаем анализ листа {self.sheet_name}...")
        
        try:
            # Читаем весь лист (расширенный диапазон для всех данных)
            data = sheets.read_range(self.sheet_name, "A1:ZZ200")
            
            if not data or len(data) < 3:
                print("ERROR: Недостаточно данных в листе")
                return {'success': False, 'error': 'Недостаточно данных'}
            
            # Первая строка - заголовки с датами
            headers = data[0]
            print(f"INFO: Всего колонок: {len(headers)}")
            
            # Находим колонки с датами
            date_columns = self.find_date_columns(headers)
            print(f"INFO: Найдено колонок с датами: {len(date_columns)}")
            
            if len(date_columns) < 2:
                return {
                    'success': False,
                    'error': 'Недостаточно дат для сравнения (нужно минимум 2 дня)'
                }
            
            # Находим две последние даты
            today_col, yesterday_col = self.find_last_two_dates(date_columns)
            
            if today_col is None or yesterday_col is None:
                return {
                    'success': False,
                    'error': 'Не удалось определить последние две даты'
                }
            
            # Анализируем каждую строку с метриками
            anomalies = []
            metrics_analyzed = 0
            
            for row_idx, row in enumerate(data[2:], start=3):  # Начинаем с 3-й строки
                if not row or len(row) <= max(today_col, yesterday_col):
                    continue
                
                # Первая колонка - название метрики
                metric_name = str(row[0]).strip() if len(row) > 0 else ""
                if not metric_name:
                    continue
                
                # Получаем значения
                today_value = self.parse_number(row[today_col]) if today_col < len(row) else None
                yesterday_value = self.parse_number(row[yesterday_col]) if yesterday_col < len(row) else None
                
                if today_value is None or yesterday_value is None:
                    continue
                
                # Пропускаем если оба значения нулевые
                if today_value == 0 and yesterday_value == 0:
                    continue
                
                # Вычисляем изменение в процентах
                if yesterday_value == 0:
                    if today_value == 0:
                        continue
                    change_pct = 100  # Рост с нуля
                else:
                    change_pct = ((today_value - yesterday_value) / abs(yesterday_value)) * 100
                
                metrics_analyzed += 1
                
                # Проверяем порог
                threshold = self.get_threshold(metric_name)
                if abs(change_pct) >= threshold:
                    category = self.classify_metric(metric_name)
                    
                    anomaly = {
                        'row': row_idx,
                        'col_today': today_col,
                        'col_yesterday': yesterday_col,
                        'metric': metric_name,
                        'yesterday_value': yesterday_value,
                        'today_value': today_value,
                        'change_pct': round(change_pct, 2),
                        'category': category,
                        'threshold': threshold,
                        'direction': '⬆️' if change_pct > 0 else '⬇️'
                    }
                    
                    anomalies.append(anomaly)
                    print(f"INFO: Найдено отклонение - {metric_name}: {change_pct:+.1f}% ({category})")
            
            self.anomalies = anomalies
            
            print(f"INFO: Проанализировано метрик: {metrics_analyzed}")
            print(f"INFO: Найдено отклонений: {len(anomalies)}")
            
            return {
                'success': True,
                'anomalies': anomalies,
                'metrics_analyzed': metrics_analyzed,
                'today_col': today_col,
                'yesterday_col': yesterday_col,
                'sheet_name': self.sheet_name
            }
            
        except Exception as e:
            print(f"ERROR: Ошибка при анализе: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def highlight_cells(self) -> bool:
        """Подсвечивает ячейки с отклонениями в Google Sheets"""
        if not self.anomalies:
            print("INFO: Нет отклонений для подсветки")
            return True
        
        print(f"INFO: Подсвечиваем {len(self.anomalies)} ячеек...")
        
        try:
            # Группируем по категориям для цветовой подсветки
            color_mappings = {
                'critical': {
                    'red': 1.0,
                    'green': 0.92,
                    'blue': 0.92
                },  # Светло-красный
                'important': {
                    'red': 1.0,
                    'green': 0.95,
                    'blue': 0.88
                },  # Светло-желтый
                'normal': {
                    'red': 0.91,
                    'green': 0.96,
                    'blue': 0.91
                }  # Светло-зеленый
            }
            
            for anomaly in self.anomalies:
                row = anomaly['row']
                col = anomaly['col_today']
                category = anomaly['category']
                background_color = color_mappings.get(category, color_mappings['normal'])
                
                # Формируем комментарий
                note = (f"AI Агент: {anomaly['direction']} {abs(anomaly['change_pct']):.1f}%\n"
                       f"Вчера: {anomaly['yesterday_value']}\n"
                       f"Сегодня: {anomaly['today_value']}")
                
                # Подсвечиваем через Google Sheets API
                success = sheets.update_cell_format(
                    self.sheet_name,
                    row,
                    col,
                    background_color,
                    note
                )
                
                if success:
                    icon = '[CRITICAL]' if category == 'critical' else '[IMPORTANT]' if category == 'important' else '[NORMAL]'
                    print(f"  {icon} Подсвечено: {anomaly['metric']} (строка {row}, колонка {col})")
                else:
                    print(f"  WARNING: Не удалось подсветить {anomaly['metric']}")
            
            print(f"SUCCESS: Подсветка завершена ({len(self.anomalies)} ячеек)")
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка при подсветке ячеек: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_markdown_report(self) -> str:
        """Генерирует MD отчет с найденными отклонениями"""
        if not self.anomalies:
            return "# Ежедневный анализ\n\nОтклонений не найдено ✅"
        
        # Группируем по категориям
        by_category = {
            'critical': [],
            'important': [],
            'normal': []
        }
        
        for anomaly in self.anomalies:
            category = anomaly['category']
            by_category[category].append(anomaly)
        
        # Генерируем отчет
        today = datetime.now().strftime('%Y-%m-%d')
        report = f"# Ежедневный анализ: {today}\n\n"
        report += f"**Лист:** {self.sheet_name}\n\n"
        report += "---\n\n"
        
        # Критичные отклонения
        if by_category['critical']:
            report += "## 🔴 Критичные отклонения (требуют немедленного внимания)\n\n"
            for anomaly in sorted(by_category['critical'], key=lambda x: abs(x['change_pct']), reverse=True):
                report += f"### {anomaly['metric']}\n"
                report += f"- **Вчера**: {anomaly['yesterday_value']}\n"
                report += f"- **Сегодня**: {anomaly['today_value']}\n"
                report += f"- **Изменение**: **{anomaly['change_pct']:+.1f}%** {anomaly['direction']}\n"
                report += f"- **Строка**: {anomaly['row']}\n\n"
            report += "---\n\n"
        
        # Важные отклонения
        if by_category['important']:
            report += "## 🟡 Важные отклонения (рекомендуется проверить)\n\n"
            for anomaly in sorted(by_category['important'], key=lambda x: abs(x['change_pct']), reverse=True):
                report += f"### {anomaly['metric']}\n"
                report += f"- **Вчера**: {anomaly['yesterday_value']}\n"
                report += f"- **Сегодня**: {anomaly['today_value']}\n"
                report += f"- **Изменение**: **{anomaly['change_pct']:+.1f}%** {anomaly['direction']}\n"
                report += f"- **Строка**: {anomaly['row']}\n\n"
            report += "---\n\n"
        
        # Статистика
        report += "## 📊 Статистика\n\n"
        report += f"- Критичных отклонений: {len(by_category['critical'])}\n"
        report += f"- Важных отклонений: {len(by_category['important'])}\n"
        report += f"- Всего отклонений: {len(self.anomalies)}\n\n"
        
        # Рекомендации
        report += "## 💡 Рекомендации\n\n"
        if by_category['critical']:
            report += "1. **Приоритет 1**: Проверить критичные метрики (CR, конверсия, выручка)\n"
        if by_category['important']:
            report += "2. **Приоритет 2**: Проанализировать важные метрики (CTR, клики, показы)\n"
        report += "3. **Проверить**: Возможные причины - цены конкурентов, рекламные ставки, контент\n"
        report += "4. **Обратиться**: К алгоритму действий для конкретных рекомендаций\n\n"
        
        report += "---\n\n"
        report += f"*Отчет сгенерирован автоматически AI-агентом*\n"
        report += f"*Время анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return report
    
    def save_report(self, report: str) -> str:
        """Сохраняет отчет в файл"""
        today = datetime.now().strftime('%Y-%m-%d')
        filename = f"daily-report-{today}.md"
        filepath = Path("reports") / filename
        
        # Создаем папку если нет
        filepath.parent.mkdir(exist_ok=True)
        
        # Сохраняем отчет
        filepath.write_text(report, encoding='utf-8')
        print(f"INFO: Отчет сохранен в {filepath}")
        
        return str(filepath)

def main():
    """Основная функция"""
    print("=" * 60)
    print("АНАЛИЗ ЕЖЕДНЕВНЫХ ИЗМЕНЕНИЙ")
    print("=" * 60)
    
    analyzer = AugustDailyAnalyzer()
    
    # Анализируем
    result = analyzer.analyze_daily_changes()
    
    if not result['success']:
        print(f"ERROR: {result.get('error', 'Неизвестная ошибка')}")
        return
    
    # Подсвечиваем ячейки
    analyzer.highlight_cells()
    
    # Генерируем и сохраняем отчет
    report = analyzer.generate_markdown_report()
    report_path = analyzer.save_report(report)
    
    print("\n" + "=" * 60)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("=" * 60)
    print(f"Найдено отклонений: {len(analyzer.anomalies)}")
    print(f"Отчет сохранен: {report_path}")
    print("\nКритичные отклонения:")
    for anomaly in analyzer.anomalies:
        if anomaly['category'] == 'critical':
            print(f"  [CRITICAL] {anomaly['metric']}: {anomaly['change_pct']:+.1f}%")

if __name__ == "__main__":
    main()


