#!/usr/bin/env python3
"""
Основной скрипт запуска
"""

import sys
import os

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Главная функция запуска"""
    try:
        # Импортируем и запускаем главный модуль
        from src.main import main as assistant_main
        return assistant_main()
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\nВозможные решения:")
        print("1. Установите зависимости: pip install -r requirements.txt")
        print("2. Проверьте структуру проекта")
        print("3. Убедитесь, что все файлы на месте")
        return 1
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())