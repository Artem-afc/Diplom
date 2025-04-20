# Используем официальный образ Python в качестве базового
FROM python:3.11-slim-buster

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем весь код проекта в контейнер
COPY  . /app

# Устанавливаем переменные окружения (по необходимости)
ENV DJANGO_SETTINGS_MODULE=diplom.settings

# Собираем статические файлы Django
RUN python manage.py collectstatic --noinput

# Открываем порт, на котором будет работать Django (обычно 8000)
EXPOSE 8000

# Команда для запуска Django-сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]