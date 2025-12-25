import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Класс для работы с API погоды"""

    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    BASE_URL_FORECAST = "http://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str, default_city: str = "Москва", units: str = "metric", lang: str = "ru"):
        self.api_key = api_key
        self.default_city = default_city
        self.units = units
        self.lang = lang

        # Кэш для хранения результатов
        self.cache = {}
        self.cache_duration = 600  # 10 минут в секундах

    def get_weather(self, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Получает текущую погоду для города

        Args:
            city: название города (None для города по умолчанию)

        Returns:
            Dict с данными о погоде
        """
        city = city or self.default_city

        # Проверяем кэш
        cache_key = f"current_{city}"
        if self._is_cached_valid(cache_key):
            logger.info(f"Используем кэшированные данные для {city}")
            return self.cache[cache_key]['data']

        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Обрабатываем и форматируем данные
            processed_data = self._process_weather_data(data)

            # Сохраняем в кэш
            self.cache[cache_key] = {
                'timestamp': datetime.now().timestamp(),
                'data': processed_data
            }

            logger.info(f"Получены данные погоды для {city}")
            return processed_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса погоды: {e}")
            return {
                'error': True,
                'message': f"Ошибка получения данных: {str(e)}"
            }
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {
                'error': True,
                'message': "Ошибка обработки данных"
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return {
                'error': True,
                'message': "Неожиданная ошибка"
            }

    def get_forecast(self, city: Optional[str] = None, days: int = 1) -> Dict[str, Any]:
        """Получает прогноз погоды"""
        city = city or self.default_city

        cache_key = f"forecast_{city}_{days}"
        if self._is_cached_valid(cache_key):
            return self.cache[cache_key]['data']

        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': self.units,
                'lang': self.lang,
                'cnt': days * 8  # API возвращает данные каждые 3 часа
            }

            response = requests.get(self.BASE_URL_FORECAST, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            processed_data = self._process_forecast_data(data)

            self.cache[cache_key] = {
                'timestamp': datetime.now().timestamp(),
                'data': processed_data
            }

            return processed_data

        except Exception as e:
            logger.error(f"Ошибка получения прогноза: {e}")
            return {'error': True, 'message': str(e)}

    def _process_weather_data(self, data: Dict) -> Dict:
        """Обрабатывает сырые данные о погоде"""
        if data.get('cod') != 200:
            return {'error': True, 'message': data.get('message', 'Unknown error')}

        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        sys = data.get('sys', {})

        return {
            'error': False,
            'city': data.get('name', 'Unknown'),
            'country': sys.get('country', ''),
            'temperature': main.get('temp', 0),
            'feels_like': main.get('feels_like', 0),
            'humidity': main.get('humidity', 0),
            'pressure': main.get('pressure', 0),
            'description': weather.get('description', ''),
            'main': weather.get('main', ''),
            'wind_speed': wind.get('speed', 0),
            'wind_deg': wind.get('deg', 0),
            'sunrise': datetime.fromtimestamp(sys.get('sunrise', 0)).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(sys.get('sunset', 0)).strftime('%H:%M'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def _process_forecast_data(self, data: Dict) -> Dict:
        """Обрабатывает данные прогноза"""
        # Упрощенная обработка
        forecast_list = data.get('list', [])
        processed = []

        for item in forecast_list[:3]:  # Берем первые 3 прогноза
            processed.append({
                'time': item.get('dt_txt', ''),
                'temp': item['main']['temp'],
                'description': item['weather'][0]['description']
            })

        return {
            'city': data['city']['name'],
            'forecast': processed
        }

    def _is_cached_valid(self, key: str) -> bool:
        """Проверяет, действителен ли кэш"""
        if key not in self.cache:
            return False

        cache_time = self.cache[key]['timestamp']
        current_time = datetime.now().timestamp()

        return (current_time - cache_time) < self.cache_duration

    def format_weather_response(self, weather_data: Dict) -> str:
        """Форматирует данные о погоде в читаемую строку"""
        if weather_data.get('error'):
            return weather_data.get('message', 'Ошибка получения погоды')

        city = weather_data['city']
        temp = round(weather_data['temperature'])
        feels_like = round(weather_data['feels_like'])
        description = weather_data['description']
        humidity = weather_data['humidity']
        wind_speed = weather_data['wind_speed']

        # Формируем красивый ответ
        responses = [
            f"В городе {city} сейчас {description}. Температура {temp}°C, ощущается как {feels_like}°C. "
            f"Влажность {humidity}%, ветер {wind_speed} м/с.",

            f"Сейчас в {city}: {description}. {temp} градусов, по ощущениям {feels_like}. "
            f"Влажность {humidity} процентов.",

            f"Погода в {city}: {description}, {temp} градусов. "
            f"Ветер {wind_speed} метров в секунду."
        ]

        import random
        return random.choice(responses)


class WikipediaAPI:
    """Класс для работы с Wikipedia API"""

    BASE_URL = "https://ru.wikipedia.org/w/api.php"

    def __init__(self, lang: str = "ru"):
        self.lang = lang
        self.base_url = f"https://{lang}.wikipedia.org/w/api.php"

    def search(self, query: str, sentences: int = 3) -> Dict[str, Any]:
        """
        Ищет информацию в Википедии

        Args:
            query: поисковый запрос
            sentences: количество предложений в ответе

        Returns:
            Dict с результатами поиска
        """
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

            response = requests.get(self.base_url, params=params, timeout=10)
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

    def format_wikipedia_response(self, wiki_data: Dict) -> str:
        """Форматирует данные из Википедии в строку"""
        if wiki_data.get('error'):
            return wiki_data.get('message', 'Ошибка поиска')

        title = wiki_data['title']
        extract = wiki_data['extract']

        # Ограничиваем длину текста
        if len(extract) > 500:
            extract = extract[:497] + "..."

        return f"{title}. {extract}"


if __name__ == "__main__":
    # Тестирование API
    print("Тестирование API клиентов...")

    # Тест требует установленного API ключа
    # weather_api = WeatherAPI("your_api_key")
    # weather = weather_api.get_weather("Москва")
    # print(f"Погода: {weather}")

    wiki_api = WikipediaAPI()
    result = wiki_api.search("Пушкин")
    print(f"Википедия: {result}")