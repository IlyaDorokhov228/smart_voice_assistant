#!/usr/bin/env python3
"""
Главный модуль голосового помощника
"""

import sys
import os
import logging
import traceback
import random

# ПРАВИЛЬНО ДОБАВЛЯЕМ ПУТИ
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ТЕПЕРЬ ИМПОРТИРУЕМ
try:
    from src.core.config import get_settings
    from src.core.listener import SpeechListener
    from src.core.speaker import VoiceAssistantSpeaker, say_text
    from src.brain.processor import CommandProcessor
    from src.brain.actions import CommandExecutor
    print("✅ Все модули успешно импортированы")
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Структура проекта:")
    print(f"Текущая директория: {current_dir}")
    print(f"Корень проекта: {project_root}")
    sys.exit(1)


class VoiceAssistant:
    """Основной класс голосового помощника"""

    def __init__(self):
        """Инициализация всех компонентов"""
        try:
            # Загружаем конфигурацию
            self.config = get_settings()

            # Инициализируем компоненты
            self.listener = SpeechListener(self.config)
            self.speaker = VoiceAssistantSpeaker(self.config)
            self.processor = CommandProcessor()
            self.executor = CommandExecutor(self.config)

            self.is_running = False

            logging.info(f"Инициализирован помощник '{self.config.get('NAME', 'Ассистент')}'")
            print(f"✅ Помощник '{self.config.get('NAME', 'Ассистент')}' инициализирован")

        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            raise

    def start(self):
        """Запуск основного цикла"""
        self.is_running = True
        
        print("\n" + "=" * 60)
        print(f"🚀 Запуск голосового помощника '{self.config.get('NAME', 'Ассистент')}'")
        print("=" * 60)
        print("\n📋 Доступные команды:")
        print("• Привет/Здравствуй")
        print("• Который час/Скажи время")
        print("• Какая сегодня дата")
        print("• Погода [в городе]")
        print("• Расскажи шутку")
        print("• Найди [запрос]")
        print("• Стоп/Выход")
        print("\n🎤 Говорите четко в микрофон после сигнала...")
        
        # Приветственное сообщение
        self.speaker.say(f"Привет! Я {self.config.get('NAME', 'Ассистент')}, ваш голосовой помощник. Чем могу помочь?")

        # Основной цикл
        while self.is_running:
            self._process_cycle()

        print("\n👋 Работа помощника завершена")

    def _process_cycle(self):
        """Один цикл обработки команды"""
        try:
            # 1. Слушаем команду
            command_text = self.listener.listen()

            if command_text is None:
                # Переспрашиваем, если не распознали
                if random.random() < 0.3:  # 30% chance
                    self.speaker.say("Повторите, пожалуйста")
                return

            # 2. Анализируем команду
            analysis = self.processor.parse_command(command_text)
            print(f"📝 Вы сказали: '{command_text}' -> Intent: {analysis['intent']}")

            # 3. Выполняем действие
            response = self.executor.execute(
                analysis['intent'],
                analysis['entities']
            )

            # 4. Озвучиваем ответ
            self.speaker.say(response)

            # 5. Проверяем, не команда ли выхода
            if analysis['intent'] == 'exit':
                self.is_running = False

        except KeyboardInterrupt:
            self.is_running = False
            print("\n\n👋 Прерывание пользователем")
        except Exception as e:
            print(f"⚠️  Ошибка: {e}")
            self.speaker.say("Произошла ошибка, попробуйте еще раз")

    def stop(self):
        """Остановка помощника"""
        self.is_running = False


def check_environment():
    """Проверка окружения перед запуском"""
    print("🔍 Проверка окружения...")

    # Проверяем наличие необходимых файлов
    required_files = [
        'config.ini',
        'data/responses.json'
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"⚠️  Отсутствуют файлы: {', '.join(missing_files)}")

        # Создаем config.ini если нет
        if 'config.ini' in missing_files:
            print("Создаю config.ini...")
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.write("""[ASSISTANT]
name = Ассистент
language = ru-RU
energy_threshold = 30000
pause_threshold = 0.8
timeout = 5
phrase_time_limit = 10

[VOICE]
rate = 200
volume = 0.9
voice_id = 1

[WEATHER]
default_city = Москва
units = metric
lang = ru
""")
            print("✅ Создан файл config.ini")
            missing_files.remove('config.ini')

        # Создаем responses.json если нет
        if 'data/responses.json' in missing_files:
            print("Создаю data/responses.json...")
            os.makedirs('data', exist_ok=True)
            import json
            with open('data/responses.json', 'w', encoding='utf-8') as f:
                json.dump({
                    "greeting": ["Привет!", "Здравствуйте!", "Приветствую!", "Рада вас слышать!"],
                    "time": ["Сейчас {time}", "Текущее время: {time}"],
                    "date": ["Сегодня {date}", "Текущая дата: {date}"],
                    "weather": ["В {city} сейчас {weather}", "Погода в {city}: {weather}"],
                    "wikipedia": ["Согласно информации: {info}", "Я нашла: {info}"],
                    "joke": ["{joke}", "Вот шутка: {joke}"],
                    "exit": ["До свидания!", "Рада была помочь!"],
                    "unknown": ["Извините, не поняла команду", "Повторите, пожалуйста"]
                }, f, ensure_ascii=False, indent=2)
            print("✅ Создан файл data/responses.json")
            missing_files.remove('data/responses.json')

        if missing_files:
            print(f"❌ Не удалось создать: {', '.join(missing_files)}")
            return False

    # Проверяем зависимости
    try:
        import speech_recognition
        import pyttsx3
        import pyaudio
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствует зависимость: {e}")
        print("Установите: pip install -r requirements.txt")
        return False

    print("✅ Окружение проверено")
    return True


def main():
    """Точка входа в программу"""
    try:
        print("=" * 60)
        print("🎤 Умный голосовой помощник")
        print("=" * 60)

        # Проверяем окружение
        if not check_environment():
            return 1

        # Создаем и запускаем помощника
        assistant = VoiceAssistant()
        assistant.start()

    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
        return 0
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())