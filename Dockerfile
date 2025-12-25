# Базовый образ Python 3.9 slim (основан на Debian Bullseye)
FROM python:3.9-slim

# Устанавливаем системные зависимости для компиляции и работы pyaudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    portaudio19-dev \
    libportaudio2 \
    libportaudiocpp0 \
    libasound2-dev \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*
# Рабочая директория
WORKDIR /app

# Копируем requirements и устанавливаем Python-пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Не буферизуем вывод (логи видно сразу)
ENV PYTHONUNBUFFERED=1

# Запуск ассистента
CMD ["python", "run.py"]
