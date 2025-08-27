# Полная настройка домашней БД через ngrok

## 🚀 Быстрая установка (5 минут)

### 1. Установка PostgreSQL
```cmd
# Запустите от имени администратора
install_postgresql.bat
```

### 2. Настройка PostgreSQL
```cmd
# Запустите от имени администратора
setup_postgresql.bat
```

### 3. Регистрация на ngrok
1. Откройте https://ngrok.com/signup
2. Зарегистрируйтесь (бесплатно)
3. Скопируйте ваш **authtoken** из Dashboard

### 4. Настройка ngrok
```cmd
setup_ngrok.bat
# Введите ваш authtoken когда попросит
```

### 5. Запуск туннеля
```cmd
start_tunnel.bat
```

### 6. Получение URL базы данных
После запуска `start_tunnel.bat` вы увидите:
```
Forwarding    tcp://0.tcp.ngrok.io:12345 -> localhost:5432
```

**Скопируйте этот URL!** (например: `0.tcp.ngrok.io:12345`)

### 7. Настройка Render
1. Откройте ваш веб-сервис на Render
2. Перейдите в **Environment**
3. Добавьте переменную:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://harvest:harvest123@0.tcp.ngrok.io:12345/harvest_db`
   
   ⚠️ **Замените** `0.tcp.ngrok.io:12345` на ваш URL из ngrok!

### 8. Деплой изменений
```bash
git add .
git commit -m "Add home database support"
git push origin main
```

## ✅ Проверка работы

### Тест подключения к БД:
```cmd
psql -h 0.tcp.ngrok.io -p 12345 -U harvest -d harvest_db
# Замените на ваш URL и порт
```

### Проверка сайта:
1. Откройте https://anoni-1.onrender.com/
2. Зарегистрируйте нового пользователя
3. Если регистрация прошла - БД работает!

## 🔧 Автозапуск при включении компьютера

### Создайте ярлык:
1. Правый клик на `start_tunnel.bat` → Создать ярлык
2. Скопируйте ярлык в папку автозагрузки:
   ```
   Win+R → shell:startup → Вставить ярлык
   ```

## 📊 Мониторинг

### Веб-интерфейс ngrok:
Откройте http://localhost:4040 для просмотра статистики туннеля

### Логи PostgreSQL:
```
C:\Program Files\PostgreSQL\15\data\log\
```

## ⚠️ Важные моменты

### Безопасность:
- Используйте сильный пароль для PostgreSQL
- Регулярно обновляйте ngrok authtoken
- Не публикуйте URL туннеля

### Стабильность:
- Держите компьютер включенным 24/7
- Стабильное интернет-соединение
- Не закрывайте окно `start_tunnel.bat`

### Лимиты ngrok (бесплатный план):
- 1 туннель одновременно
- 40 подключений в минуту
- Туннель перезапускается каждые 8 часов

## 🆘 Решение проблем

### Ошибка "connection refused":
```cmd
# Проверьте статус PostgreSQL
net start postgresql-x64-15
```

### Ошибка "authentication failed":
```cmd
# Пересоздайте пользователя
psql -U postgres -c "DROP USER IF EXISTS harvest;"
psql -U postgres -c "CREATE USER harvest WITH PASSWORD 'harvest123';"
```

### ngrok не запускается:
```cmd
# Переустановите authtoken
ngrok authtoken YOUR_TOKEN_HERE
```

## 💰 Стоимость

- **PostgreSQL**: Бесплатно
- **ngrok**: Бесплатно (с лимитами)
- **Электричество**: ~50₽/месяц за работающий ПК

## 🎯 Результат

✅ **Неограниченный объем БД**  
✅ **Полный контроль над данными**  
✅ **Бесплатное решение**  
✅ **Высокая скорость**  

❌ **Нужно держать ПК включенным**  
❌ **Зависит от интернета**  
❌ **Лимиты ngrok**