"""
Модуль обработки команд (упрощенная версия)
"""

import re
import json
import random
from typing import Optional, Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CommandProcessor:
    """Класс для обработки и анализа команд"""

    def __init__(self, responses_file: str = "data/responses.json"):
        self.intents = self._load_intent_patterns()
        self.responses = self._load_responses(responses_file)

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Загружает паттерны для определения намерений"""
        return {
            'greeting': ['привет', 'здравствуй', 'здравствуйте', 'добрый день', 'доброе утро', 'добрый вечер'],
            'time': ['время', 'который час', 'текущее время', 'сколько времени', 'скажи время'],
            'date': ['дата', 'какое число', 'сегодняшняя дата', 'какой сегодня день', 'какая сегодня дата'],
            'weather': ['погода', 'погоду', 'температура', 'на улице', 'какая погода'],
            'wikipedia': ['найди', 'найти', 'что такое', 'кто такой', 'расскажи о', 'информация о', 'ищи'],
            'joke': ['шутка', 'пошути', 'рассмеши', 'анекдот', 'расскажи шутку', 'расскажи анекдот'],
            'exit': ['стоп', 'выход', 'заверши', 'пока', 'до свидания', 'закончить', 'хватит']
        }

    def _load_responses(self, file_path: str) -> Dict[str, List[str]]:
        """Загружает шаблоны ответов из JSON файла"""
        # Дефолтные ответы
        default_responses = {
            'greeting': ['Привет!', 'Здравствуйте!', 'Приветствую!', 'Рада вас слышать!'],
            'time': ['Сейчас {time}', 'Текущее время: {time}', 'На часах {time}'],
            'date': ['Сегодня {date}', 'Текущая дата: {date}', 'Сегодняшнее число: {date}'],
            'weather': ['В {city} сейчас {weather}', 'Погода в {city}: {weather}'],
            'wikipedia': ['Согласно информации: {info}', 'Я нашла: {info}', '{info}'],
            'joke': ['{joke}', 'Вот шутка: {joke}', 'Слушайте: {joke}'],
            'exit': ['До свидания!', 'Рада была помочь!', 'До встречи!', 'Пока!'],
            'unknown': [
                'Извините, не поняла команду',
                'Повторите, пожалуйста',
                'Можете сказать иначе?',
                'Я пока не умею это делать'
            ]
        }

        file_path = Path(file_path)

        # Если файл не существует, создаем его
        if not file_path.exists():
            self._create_default_responses_file(file_path)
            return default_responses

        # Если файл существует, пытаемся загрузить
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_responses = json.loads(f.read())

                # Объединяем с дефолтными
                result = default_responses.copy()
                for key in custom_responses:
                    if key in result:
                        result[key] = custom_responses[key]
                    else:
                        result[key] = custom_responses[key]

                logger.info(f"✅ Загружены ответы из {file_path}")
                return result

        except Exception as e:
            logger.error(f"❌ Ошибка загрузки файла {file_path}: {e}")
            print(f"⚠️  Ошибка загрузки responses.json. Использую значения по умолчанию.")
            return default_responses

    def _create_default_responses_file(self, file_path: Path):
        """Создает файл с шаблонами ответов по умолчанию"""
        default_responses = {
            "greeting": ["Привет!", "Здравствуйте!", "Приветствую!", "Рада вас слышать!"],
            "time": ["Сейчас {time}", "Текущее время: {time}", "На часах {time}"],
            "date": ["Сегодня {date}", "Текущая дата: {date}", "Сегодняшнее число: {date}"],
            "weather": ["В {city} сейчас {weather}", "Погода в {city}: {weather}"],
            "wikipedia": ["Согласно информации: {info}", "Я нашла: {info}", "{info}"],
            "joke": ["{joke}", "Вот шутка: {joke}", "Слушайте: {joke}"],
            "exit": ["До свидания!", "Рада была помочь!", "До встречи!", "Пока!"],
            "unknown": [
                "Извините, не поняла команду",
                "Повторите, пожалуйста",
                "Можете сказать иначе?",
                "Я пока не умею это делать"
            ]
        }

        # Создаем папку, если её нет
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_responses, f, ensure_ascii=False, indent=2)

        print(f"✅ Создан файл {file_path}")

    def get_random_response(self, intent: str) -> str:
        """Возвращает случайный ответ для заданного намерения"""
        return random.choice(self.responses.get(intent, self.responses['unknown']))

    def parse_command(self, command_text: str) -> Dict[str, any]:
        """
        Анализирует текст команды и определяет намерение
        """
        if not command_text:
            return {
                'intent': 'unknown',
                'entities': {},
                'confidence': 0.0,
                'original_text': ''
            }

        command_lower = command_text.lower()
        entities = {}

        # Определяем намерение
        best_intent = 'unknown'
        best_score = 0

        for intent, patterns in self.intents.items():
            score = 0
            for pattern in patterns:
                if pattern in command_lower:
                    score += 1

            if score > best_score:
                best_score = score
                best_intent = intent

        # Извлекаем сущности
        if best_intent == 'weather':
            # Город для погоды
            weather_patterns = [
                r'погод[ауе] в ([\w\s-]+)',
                r'погод[ауе] ([\w\s-]+)',
                r'какая погода в ([\w\s-]+)'
            ]

            for pattern in weather_patterns:
                city_match = re.search(pattern, command_lower)
                if city_match:
                    entities['city'] = city_match.group(1).strip()
                    break

        elif best_intent == 'wikipedia':
            # Запрос для Википедии
            query = command_lower
            stop_words = ['найди', 'найти', 'что', 'такое', 'кто', 'такой', 'расскажи', 'о', 'про', 'информация',
                          'википедии', 'про', 'ищи', 'поищи']
            for word in stop_words:
                query = query.replace(word, '')
            entities['query'] = query.strip()
            entities['original_text'] = command_text

        confidence = min(best_score / max(len(command_lower.split()), 1), 1.0)

        return {
            'intent': best_intent,
            'entities': entities,
            'confidence': confidence,
            'original_text': command_text
        }


if __name__ == "__main__":
    # Тестирование процессора
    processor = CommandProcessor()

    test_commands = [
        "привет",
        "сколько времени",
        "какая сегодня дата",
        "погода в москве",
        "найди информацию о пушкине",
        "расскажи шутку",
        "стоп",
        "что-то непонятное"
    ]

    for cmd in test_commands:
        result = processor.parse_command(cmd)
        print(f"\nКоманда: '{cmd}'")
        print(f"Намерение: {result['intent']}")
        print(f"Сущности: {result['entities']}")
        print(f"Уверенность: {result['confidence']:.2f}")