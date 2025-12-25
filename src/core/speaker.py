"""
Модуль синтеза речи (исправленная версия)
"""

import sys
import logging

logger = logging.getLogger(__name__)


class VoiceAssistantSpeaker:
    def __init__(self, config=None):
        """Инициализация синтезатора речи"""
        self.config = config or {}
        self.engine = None
        
        # Пытаемся использовать pyttsx3
        self._try_init_pyttsx3()
        
        # Если не получилось, используем fallback
        if self.engine is None:
            print("⚠️  Pyttsx3 не работает. Использую текстовый режим.")
            self.use_tts = False
        else:
            self.use_tts = True

    def _try_init_pyttsx3(self):
        """Пробуем инициализировать pyttsx3"""
        try:
            import pyttsx3
            print("🔊 Инициализация pyttsx3...")
            self.engine = pyttsx3.init()
            
            # Настройки
            if self.engine:
                rate = self.config.get('VOICE_RATE', 170)
                volume = self.config.get('VOICE_VOLUME', 0.9)
                self.engine.setProperty('rate', rate)
                self.engine.setProperty('volume', volume)
                
                # Выбор голоса
                voices = self.engine.getProperty('voices')
                if voices:
                    voice_id = self.config.get('VOICE_ID', 0)
                    if 0 <= voice_id < len(voices):
                        self.engine.setProperty('voice', voices[voice_id].id)
                
                print("✅ Pyttsx3 инициализирован")
        except Exception as e:
            print(f"❌ Ошибка инициализации pyttsx3: {e}")
            self.engine = None

    def say(self, text, wait=True):
        """
        Произносит текст или выводит его
        """
        if not text:
            return
            
        print(f"\n{'='*50}")
        print(f"🤖: {text}")
        print(f"{'='*50}")
        
        if self.use_tts and self.engine:
            try:
                self.engine.say(text)
                if wait:
                    self.engine.runAndWait()
            except Exception as e:
                print(f"⚠️  Ошибка синтеза речи: {e}")
                print("Переключаюсь в текстовый режим...")
                self.use_tts = False

    def __del__(self):
        """Очистка при удалении"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


def say_text(text):
    """Простая функция для обратной совместимости"""
    speaker = VoiceAssistantSpeaker()
    speaker.say(text)


if __name__ == "__main__":
    print("Тест модуля синтеза речи...")
    speaker = VoiceAssistantSpeaker()
    speaker.say("Привет! Это тест синтеза речи. Если вы это слышите, всё работает!")