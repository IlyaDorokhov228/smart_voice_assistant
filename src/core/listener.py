"""
Модуль распознавания речи
"""

import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)


class SpeechListener:
    def __init__(self, config=None):
        """Инициализация распознавателя речи"""
        if config is None:
            from .config import get_settings
            config = get_settings()

        self.config = config
        self.recognizer = sr.Recognizer()
        self.microphone = None  # Не инициализируем сразу
        
        # Настройка параметров
        self.recognizer.energy_threshold = self.config.get('ENERGY_THRESHOLD', 30000)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = self.config.get('PAUSE_THRESHOLD', 0.8)

        print("✅ Распознаватель речи инициализирован")

    def _get_microphone(self):
        """Получает микрофон (создает при первом вызове)"""
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone()
                print("✅ Микрофон инициализирован")
            except Exception as e:
                print(f"❌ Ошибка инициализации микрофона: {e}")
                self.microphone = None
        return self.microphone

    def _calibrate_microphone(self, source):
        """Калибровка микрофона под фоновый шум"""
        try:
            print("🔧 Калибровка микрофона... Пожалуйста, помолчите 2 секунды")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Калибровка завершена")
        except Exception as e:
            print(f"⚠️  Ошибка калибровки: {e}")

    def listen(self, timeout=None, phrase_time_limit=None):
        """
        Слушает микрофон и возвращает распознанный текст
        """
        if timeout is None:
            timeout = self.config.get('TIMEOUT', 5)
        if phrase_time_limit is None:
            phrase_time_limit = self.config.get('PHRASE_TIME_LIMIT', 10)

        # Получаем микрофон
        microphone = self._get_microphone()
        if microphone is None:
            print("❌ Микрофон не доступен")
            return None

        try:
            print("\n🎤 Слушаю... (говорите после сигнала)")

            # Используем микрофон в контекстном менеджере
            with microphone as source:
                # Калибруем при каждом запуске
                self._calibrate_microphone(source)
                
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                print("✅ Речь распознана, обрабатываю...")

                # Используем Google Web Speech API
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.config.get('LANGUAGE', 'ru-RU')
                ).lower()

                print(f"📝 Вы сказали: {text}")
                return text

        except sr.WaitTimeoutError:
            print("⏰ Время ожидания истекло")
            return None
        except sr.UnknownValueError:
            print("🤔 Речь не распознана")
            return None
        except sr.RequestError as e:
            print(f"🚫 Ошибка сервиса распознавания: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Ошибка при прослушивании: {e}")
            return None


def listen_command():
    """Простая функция для распознавания команды"""
    try:
        from .config import get_settings
        config = get_settings()
        listener = SpeechListener(config)
        return listener.listen()
    except Exception as e:
        print(f"❌ Ошибка при распознавании речи: {e}")
        return None


if __name__ == "__main__":
    # Тестирование модуля
    listener = SpeechListener()
    print("\nТест модуля распознавания речи...")
    command = listener.listen()
    if command:
        print(f"✅ Распознано: {command}")