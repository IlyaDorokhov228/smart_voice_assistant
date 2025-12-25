"""
Модуль исполнения команд (упрощенная версия)
"""

import datetime
import random
import requests
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class WikipediaAPI:
    """Класс для работы с Wikipedia"""

    BASE_URL = "https://ru.wikipedia.org/w/api.php"

    def __init__(self, lang: str = "ru"):
        self.lang = lang
        self.base_url = f"https://{lang}.wikipedia.org/w/api.php"

    def search(self, query: str, sentences: int = 2) -> dict:
        """Ищет информацию в Википедии"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
                'titles': query,
                'exsentences': sentences
            }
            headers = {
                'User-Agent': 'VoiceAssistant/1.0 (my-assistant-project)'
            }
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            pages = data.get('query', {}).get('pages', {})

            # Получаем первую страницу
            page_id = next(iter(pages))
            page_data = pages.get(page_id, {})

            if page_id == '-1':
                return {
                    'error': True,
                    'message': f"Ничего не найдено по запросу '{query}'"
                }

            return {
                'error': False,
                'title': page_data.get('title', ''),
                'extract': page_data.get('extract', ''),
                'pageid': page_id
            }

        except Exception as e:
            logger.error(f"Ошибка поиска в Википедии: {e}")
            return {
                'error': True,
                'message': f"Ошибка при поиске: {str(e)}"
            }


class SimpleWeatherProvider:
    """Упрощенный провайдер погоды"""

    def __init__(self):
        self.conditions_ru = [
            'ясно', 'малооблачно', 'облачно', 'пасмурно',
            'небольшой дождь', 'дождь', 'сильный дождь',
            'гроза', 'снег', 'туман'
        ]

        self.wind_directions = [
            'северный', 'северо-восточный', 'восточный',
            'юго-восточный', 'южный', 'юго-западный',
            'западный', 'северо-западный'
        ]

    def get_weather_by_city(self, city_name: str = "Москва") -> dict:
        """Генерирует данные о погоде"""
        # Определяем сезон
        month = datetime.datetime.now().month
        if month in [12, 1, 2]:
            temp_range = (-10, 5)
        elif month in [3, 4, 5]:
            temp_range = (5, 20)
        elif month in [6, 7, 8]:
            temp_range = (20, 35)
        else:
            temp_range = (5, 20)

        # Генерируем данные
        temperature = random.randint(*temp_range)
        feels_like = temperature + random.randint(-3, 1)
        condition = random.choice(self.conditions_ru)
        wind_speed = round(random.uniform(0, 10), 1)
        wind_dir = random.choice(self.wind_directions)

        return {
            'error': False,
            'city': city_name.capitalize(),
            'temperature': temperature,
            'feels_like': feels_like,
            'condition': condition,
            'wind_speed': wind_speed,
            'wind_dir': wind_dir
        }


class CommandExecutor:
    """Класс для выполнения команд"""

    def __init__(self, config):
        self.config = config

        # Инициализация API клиентов
        self.weather_api = SimpleWeatherProvider()
        self.wikipedia_api = WikipediaAPI(lang='ru')

        # Шутки
        self.jokes = [
            "Что сказал кот-математик собаке? 'Мяу-биус'!",
            "Почему птицы летают на юг? Потому что пешком идти далеко.",
            "Как называют ленивого кенгуру? Карманный лежебока.",
            "Сын спрашивает отца: 'Пап, а электрический ток сильный?' — 'Не знаю, сынок, я с ним не знаком.'",
            "Почему снеговик смотрит в морозилку? Он ищет морковку для своего младшего брата.",
            "Что такое философия в России? Пофиг и лишил.",
            "Почему грибы такие общительные? Потому что они всегда в компании (в компоте).",
            "Что сказал виноград, когда на него наступили? Ничего, он просто выдавил слезу.",
            "Почему книга похудела? Потому что она сидела на диете — на глаВной.",
            "Что сказал один огурец другому? 'Не лезь, я огурец!'",
            "Почему кофе никогда не выигрывает в гонках? Потому что он всегда в чашке.",
            "Как назвать медведя без ушей? Медведь без ушей. А без ушей и без глаз? Уже неважно.",
            "Почему нельзя шутить с бананом? Потому что он скользкий — можно пошутить, но он выскользнет.",
            "Что сказал сломанный лифт? 'Я просто не могу подняться над этим.'",
            "Почему математик не стал есть кекс? Потому что он уже π (пи)."
        ]

    def execute(self, intent: str, entities: Dict[str, Any] = None) -> str:
        """Выполняет действие на основе намерения"""
        if entities is None:
            entities = {}

        # Вызываем соответствующий метод
        if intent == 'greeting':
            return self._greet()
        elif intent == 'time':
            return self._get_time()
        elif intent == 'date':
            return self._get_date()
        elif intent == 'weather':
            return self._get_weather(**entities)
        elif intent == 'wikipedia':
            return self._search_wikipedia(**entities)
        elif intent == 'joke':
            return self._tell_joke()
        elif intent == 'exit':
            return self._exit()
        else:
            return self._unknown_command()

    def _greet(self) -> str:
        """Приветствие"""
        greetings = [
            f"Привет! Я {self.config.get('NAME', 'Ассистент')}, ваш голосовой помощник.",
            f"Здравствуйте! Я {self.config.get('NAME', 'Ассистент')}, к вашим услугам.",
            f"Приветствую! {self.config.get('NAME', 'Ассистент')} на связи.",
            f"Добрый день! Я {self.config.get('NAME', 'Ассистент')}, чем могу помочь?"
        ]
        return random.choice(greetings)

    def _get_time(self) -> str:
        """Получение текущего времени"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")

        responses = [
            f"Сейчас {time_str}",
            f"Текущее время: {time_str}",
            f"На часах {time_str}",
            f"Время: {time_str}"
        ]
        return random.choice(responses)

    def _get_date(self) -> str:
        """Получение текущей даты"""
        now = datetime.datetime.now()
        months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ]
        date_str = f"{now.day} {months[now.month - 1]} {now.year} года"

        return f"Сегодня {date_str}"

    def _get_weather(self, city: str = None, **kwargs) -> str:
        """Получение погоды"""
        city = city or self.config.get('DEFAULT_CITY', 'Москва')
        weather_data = self.weather_api.get_weather_by_city(city)

        if weather_data.get('error'):
            return weather_data.get('message', 'Ошибка получения погоды')

        city_name = weather_data['city']
        temp = weather_data['temperature']
        feels_like = weather_data['feels_like']
        condition = weather_data['condition']
        wind_speed = weather_data['wind_speed']
        wind_dir = weather_data['wind_dir']

        responses = [
            f"В {city_name} сейчас {condition}. Температура {temp}°C, ощущается как {feels_like}°C. "
            f"Ветер {wind_dir}, {wind_speed} м/с.",

            f"Сейчас в {city_name}: {condition}, {temp} градусов. "
            f"По ощущениям {feels_like}. Ветер {wind_dir}.",

            f"Погода в {city_name}: {condition}. Температура воздуха {temp} градусов. "
            f"Ветер {wind_dir} со скоростью {wind_speed} метров в секунду."
        ]

        return random.choice(responses)

    def _search_wikipedia(self, query: str = None, original_text: str = None, **kwargs) -> str:
        """Поиск в Википедии"""
        if not query:
            if original_text:
                query = original_text
            else:
                return "Что именно вас интересует?"

        # Очищаем запрос
        stop_words = ['найди', 'что', 'такое', 'кто', 'такой', 'расскажи', 'о', 'про', 'в', 'википедии', 'ищи', 'поищи']
        for word in stop_words:
            query = query.replace(word, '')

        query = query.strip()

        if not query or len(query) < 2:
            return "Пожалуйста, уточните запрос"

        wiki_data = self.wikipedia_api.search(query)

        if wiki_data.get('error'):
            return wiki_data.get('message', 'Ошибка поиска')

        title = wiki_data['title']
        extract = wiki_data['extract']

        # Ограничиваем длину
        if len(extract) > 300:
            extract = extract[:297] + "..."

        return f"{title}. {extract}"

    def _tell_joke(self) -> str:
        """Рассказывает шутку"""
        return random.choice(self.jokes)

    def _exit(self) -> str:
        """Завершение работы"""
        responses = [
            "До свидания! Рада была помочь!",
            "Пока! Обращайтесь, если что!",
            "До встречи!",
            "Всего доброго!"
        ]
        return random.choice(responses)

    def _unknown_command(self) -> str:
        """Ответ на неизвестную команду"""
        responses = [
            "Извините, я не поняла команду.",
            "Повторите, пожалуйста.",
            "Я пока не умею это делать.",
            "Можете сказать иначе?",
            "Не совсем понимаю, что вы хотите."
        ]
        return random.choice(responses)


if __name__ == "__main__":
    # Тестирование
    config = {
        'NAME': 'Ассистент',
        'DEFAULT_CITY': 'Москва'
    }

    executor = CommandExecutor(config)

    test_cases = [
        ('greeting', {}),
        ('time', {}),
        ('date', {}),
        ('weather', {'city': 'Москва'}),
        ('wikipedia', {'query': 'Пушкин'}),
        ('joke', {}),
        ('exit', {}),
        ('unknown', {})
    ]

    for intent, entities in test_cases:
        response = executor.execute(intent, entities)
        print(f"{intent}: {response}")