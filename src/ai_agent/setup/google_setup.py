"""
Настройка Google Sheets через Python
"""

from ai_agent.config import config
from ai_agent.google.auth import google_auth
from ai_agent.google.sheets import sheets


def main():
    """Основная функция настройки"""
    print("INFO: Настройка AI Agent для Google Sheets...\n")
    
    # Проверяем конфигурацию
    if not config.validate():
        print("ERROR: Неверная конфигурация. Проверьте .env файл")
        return False
    
    # Аутентификация
    if not google_auth.authenticate():
        print("ERROR: Ошибка аутентификации в Google API")
        return False
    
    # Получаем информацию о таблице
    info = sheets.get_spreadsheet_info()
    if info:
        print(f"SUCCESS: Подключение к таблице: '{info['title']}'")
        print(f"INFO: Существующие листы: {', '.join(info['sheets'])}")
    
    # Создаем схему
    print("\nINFO: Создаем схему листов...")
    if not sheets.setup_schema():
        print("ERROR: Ошибка создания схемы")
        return False
    
    # Добавляем стартовые правила
    print("\nINFO: Добавляем стартовые правила...")
    if not sheets.add_starter_rules():
        print("ERROR: Ошибка добавления правил")
        return False
    
    print("\nSUCCESS: Настройка завершена успешно!")
    print(f"\nINFO: Следующие шаги:")
    print("1. Откройте Google Таблицу")
    print("2. Extensions -> Apps Script")
    print("3. Скопируйте код из src/apps-script/enhanced-agent.gs")
    print("4. Появится меню 'AI Agent'")
    
    print(f"\nINFO: Ссылка на таблицу:")
    print(f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEETS_ID}/edit")
    
    return True


if __name__ == "__main__":
    main()
