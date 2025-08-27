# 🐘 Настройка PostgreSQL + ngrok для Harvest Messenger

## 1. Установка PostgreSQL (Windows)

1. Скачайте PostgreSQL с https://www.postgresql.org/download/windows/
2. Установите с паролем для пользователя `postgres`
3. Запомните порт (по умолчанию 5432)

## 2. Создание базы данных

Откройте pgAdmin или командную строку PostgreSQL:

```sql
CREATE DATABASE harvest_db;
CREATE USER harvest_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE harvest_db TO harvest_user;
```

## 3. Настройка внешнего доступа

Отредактируйте файлы PostgreSQL:

**postgresql.conf:**
```
listen_addresses = '*'
port = 5432
```

**pg_hba.conf** (добавьте в конец):
```
host    all             all             0.0.0.0/0               md5
```

Перезапустите службу PostgreSQL.

## 4. Установка ngrok

1. Зарегистрируйтесь на https://ngrok.com
2. Скачайте ngrok для Windows
3. Получите токен авторизации
4. Выполните: `ngrok authtoken YOUR_TOKEN`

## 5. Запуск туннеля

```bash
ngrok tcp 5432
```

Скопируйте URL вида: `tcp://0.tcp.ngrok.io:12345`

## 6. Настройка переменных окружения

В Render добавьте переменную:
```
DATABASE_URL=postgresql://harvest_user:your_password@0.tcp.ngrok.io:12345/harvest_db
```

## 7. Проверка подключения

Запустите локально:
```bash
python setup_postgres.py
```

## 8. Деплой на Render

1. Загрузите код в GitHub
2. Подключите репозиторий к Render
3. Убедитесь что ngrok туннель запущен
4. Деплойте приложение

## ⚠️ Важно

- Компьютер с PostgreSQL должен быть всегда включен
- ngrok туннель должен работать постоянно
- Бесплатный ngrok меняет URL при перезапуске
- Для стабильной работы нужен платный ngrok ($5/месяц)