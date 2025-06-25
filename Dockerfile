# Используем Python 3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для загрузок
RUN mkdir -p static/uploads

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "app:app", "--bind", "0.0.0.0:8080"] 