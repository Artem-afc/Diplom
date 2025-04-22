# Используем официальный образ Python
FROM python:3.11-slim-bookworm

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости для PostgreSQL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем только requirements.txt сначала для лучшего кэширования
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Настройки окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=diplom.settings

# Открываем порт
EXPOSE 8000

# Команда запуска (будет переопределена в docker-compose для миграций)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]