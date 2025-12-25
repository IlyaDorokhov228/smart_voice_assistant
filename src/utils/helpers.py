import os
import sys
import platform
import subprocess
from pathlib import Path


def play_sound(sound_type: str = "beep"):
    """
    Воспроизводит звуковой сигнал

    Args:
        sound_type: тип сигнала ('beep', 'start', 'end', 'error')
    """
    try:
        system = platform.system()

        if sound_type == "beep":
            # Системный beep
            print("\a", end='', flush=True)

            # Альтернатива для Windows
            if system == "Windows":
                import winsound
                winsound.Beep(1000, 200)
            elif system == "Darwin":  # macOS
                os.system('afplay /System/Library/Sounds/Ping.aiff &')
            elif system == "Linux":
                os.system('beep -f 1000 -l 200 2>/dev/null || echo -e "\a"')

    except Exception:
        pass  # Игнорируем ошибки воспроизведения звука


def clear_screen():
    """Очищает экран консоли"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def print_banner():
    """Выводит красивый баннер"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║            🎤 ГОЛОСОВОЙ ПОМОЩНИК v1.0 🎤                ║
    ║                                                          ║
    ║   Говорите четко в микрофон после звукового сигнала      ║
    ║   Для выхода скажите: "стоп" или "выход"                ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_dependencies():
    """Проверяет наличие всех зависимостей"""
    required = ['speech_recognition', 'pyttsx3', 'pyaudio', 'requests']
    missing = []

    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    return missing


def setup_environment():
    """Настройка окружения при первом запуске"""
    data_dir = Path("data")
    if not data_dir.exists():
        data_dir.mkdir()
        print("✅ Создана папка data/")

    env_file = Path(".env")
    if not env_file.exists():
        with open(".env.example", "r") as src, open(".env", "w") as dst:
            dst.write(src.read())
        print("✅ Создан файл .env (отредактируйте его)")

    responses_file = data_dir / "responses.json"
    if not responses_file.exists():
        from src.brain.processor import create_responses_template
        create_responses_template()

    return True