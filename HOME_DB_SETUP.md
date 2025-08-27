# Настройка домашней базы данных

## Быстрая установка

1. **Запустите скрипт:**
   ```cmd
   setup_home_database.bat
   ```

## Ручная настройка

### 1. Установка PostgreSQL
```cmd
winget install PostgreSQL.PostgreSQL
```

### 2. Создание базы данных
```cmd
# Откройте SQL Shell (psql)
createdb harvest_db
```

### 3. Настройка PostgreSQL для внешних подключений

**Файл: `C:\Program Files\PostgreSQL\15\data\postgresql.conf`**
```
listen_addresses = '*'
port = 5432
```

**Файл: `C:\Program Files\PostgreSQL\15\data\pg_hba.conf`**
```
# Добавьте в конец файла:
host    all             all             0.0.0.0/0               md5
```

### 4. Перезапуск PostgreSQL
```cmd
net stop postgresql-x64-15
net start postgresql-x64-15
```

### 5. Установка Cloudflare Tunnel
```cmd
winget install Cloudflare.cloudflared
```

### 6. Настройка туннеля
```cmd
# Авторизация
cloudflared tunnel login

# Создание туннеля
cloudflared tunnel create harvest-db

# Получите tunnel ID из вывода команды
```

### 7. Создание config.yml
**Файл: `C:\Users\%USERNAME%\.cloudflared\config.yml`**
```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: C:\Users\%USERNAME%\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: harvest-db.yourdomain.com
    service: tcp://localhost:5432
  - service: http_status:404
```

### 8. Запуск туннеля
```cmd
cloudflared tunnel run harvest-db
```

### 9. Настройка Render
В Environment Variables добавьте:
```
DATABASE_URL=postgresql://postgres:your_password@harvest-db.yourdomain.com:5432/harvest_db
```

## Альтернатива - ngrok (проще)

### 1. Установка ngrok
```cmd
winget install ngrok.ngrok
```

### 2. Авторизация
```cmd
ngrok authtoken YOUR_TOKEN
```

### 3. Запуск туннеля
```cmd
ngrok tcp 5432
```

### 4. Получение URL
Скопируйте URL из вывода ngrok (например: `tcp://0.tcp.ngrok.io:12345`)

### 5. Настройка Render
```
DATABASE_URL=postgresql://postgres:password@0.tcp.ngrok.io:12345/harvest_db
```

## Преимущества домашней БД:

✅ **Бесплатно** - неограниченный объем  
✅ **Быстро** - локальная сеть  
✅ **Контроль** - полный доступ к данным  
✅ **Безопасность** - данные у вас дома  

## Недостатки:

❌ **Доступность** - нужно держать компьютер включенным  
❌ **Интернет** - зависит от вашего подключения  
❌ **Обслуживание** - нужно следить за работой  

## Автозапуск (Windows)

Создайте bat-файл для автозапуска:
```cmd
@echo off
cd /d C:\Users\%USERNAME%\.cloudflared
cloudflared tunnel run harvest-db
```

Добавьте в автозагрузку Windows.