"""
Модуль конфигурации (упрощенный)
"""

import configparser
from pathlib import Path


def load_config():
    """Загружает конфигурацию из файлов"""
    
    # Создаем конфиг по умолчанию
    config = {
        'NAME': 'Ассистент',
        'LANGUAGE': 'ru-RU',
        'ENERGY_THRESHOLD': 30000,
        'PAUSE_THRESHOLD': 0.8,
        'TIMEOUT': 5,
        'PHRASE_TIME_LIMIT': 10,
        'VOICE_RATE': 170,
        'VOICE_VOLUME': 0.9,
        'VOICE_ID': 0,
        'DEFAULT_CITY': 'Москва',
        'DATA_DIR': 'data',
        'RESPONSES_FILE': 'data/responses.json'
    }

    # Загружаем из config.ini если есть
    config_file = Path('config.ini')
    
    if config_file.exists():
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(config_file, encoding='utf-8')

            # Читаем настройки
            if config_parser.has_section('ASSISTANT'):
                section = config_parser['ASSISTANT']
                
                # Текстовые значения
                for key in ['name', 'language']:
                    if key in section:
                        config[key.upper()] = section[key]
                
                # Числовые значения
                for key in ['energy_threshold', 'timeout', 'phrase_time_limit']:
                    if key in section:
                        try:
                            config[key.upper()] = int(section[key])
                        except ValueError:
                            pass
                
                # Дробные значения
                if 'pause_threshold' in section:
                    try:
                        config['PAUSE_THRESHOLD'] = float(section['pause_threshold'])
                    except ValueError:
                        pass

            if config_parser.has_section('VOICE'):
                section = config_parser['VOICE']
                
                if 'rate' in section:
                    try:
                        config['VOICE_RATE'] = int(section['rate'])
                    except ValueError:
                        pass
                        
                if 'volume' in section:
                    try:
                        config['VOICE_VOLUME'] = float(section['volume'])
                    except ValueError:
                        pass
                        
                if 'voice_id' in section:
                    try:
                        config['VOICE_ID'] = int(section['voice_id'])
                    except ValueError:
                        pass

            if config_parser.has_section('WEATHER'):
                section = config_parser['WEATHER']
                if 'default_city' in section:
                    config['DEFAULT_CITY'] = section['default_city']

            print("✅ Конфигурация загружена из config.ini")
            
        except Exception as e:
            print(f"⚠️  Ошибка чтения config.ini: {e}")
            print("Использую настройки по умолчанию")

    return config


# Глобальная конфигурация
SETTINGS = load_config()


def get_settings():
    """Возвращает настройки"""
    return SETTINGS


if __name__ == "__main__":
    # Тестирование
    print("Текущая конфигурация:")
    settings = get_settings()
    
    for key, value in settings.items():
        print(f"{key}: {value}")