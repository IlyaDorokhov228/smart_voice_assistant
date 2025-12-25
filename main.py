"""
Главный модуль голосового помощника
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.listener import listen_command
from src.core.speaker import say_text
from src.core.config import settings


def main():
    """Основной цикл работы помощника"""
    print("=" * 50)
    print(f"🚀 Запуск голосового помощника '{settings.NAME}'")
    print("=" * 50)
    print("\nДоступные команды:")
    print("• Привет/Здравствуй")
    print("• Который час/Скажи время")
    print("• Погода")
    print("• Стоп/Выход")
    print("\nГоворите четко в микрофон после сигнала...")

    say_text(f"Привет! Я {settings.NAME}, ваш голосовой помощник. Чем могу помочь?")

    running = True
    while running:
        # Слушаем команду
        command = listen_command()

        if command is None:
            continue

        # Простейшая обработка
        if any(word in command for word in ['привет', 'здравствуй', 'здравствуйте']):
            response = "Привет! Рада вас слышать!"
        elif any(word in command for word in ['стоп', 'выход', 'пока', 'заверши']):
            response = "До свидания! Рада была помочь!"
            running = False
        else:
            response = f"Вы сказали: {command}"

        # Озвучиваем ответ
        say_text(response)

    print("\n👋 Работа помощника завершена")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"\n⚠️  Критическая ошибка: {e}")
        import traceback

        traceback.print_exc()