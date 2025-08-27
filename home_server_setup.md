# Настройка домашнего сервера базы данных

## Вариант 1: PostgreSQL + Cloudflare Tunnel

### 1. Установка PostgreSQL на домашнем ПК:
```bash
# Windows
choco install postgresql

# Создание базы
createdb harvest_db
```

### 2. Настройка Cloudflare Tunnel:
```bash
# Установка cloudflared
choco install cloudflared

# Авторизация
cloudflared tunnel login

# Создание туннеля
cloudflared tunnel create harvest-db

# Настройка config.yml
tunnel: harvest-db
credentials-file: C:\Users\%USERNAME%\.cloudflared\tunnel-id.json

ingress:
  - hostname: harvest-db.yourdomain.com
    service: tcp://localhost:5432
  - service: http_status:404
```

### 3. Запуск туннеля:
```bash
cloudflared tunnel run harvest-db
```

## Вариант 2: Tailscale (VPN)

### 1. Установка Tailscale:
- Скачать с tailscale.com
- Установить на домашний ПК и сервер Render

### 2. Подключение:
```bash
# На домашнем ПК
tailscale up

# Получить IP
tailscale ip -4
```

### 3. Строка подключения:
```
postgresql://user:pass@100.x.x.x:5432/harvest_db
```

## Вариант 3: Простой HTTP API

### Создать простой API для базы:
```python
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/query', methods=['POST'])
def execute_query():
    query = request.json.get('query')
    # Выполнить запрос к локальной базе
    # Вернуть результат
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```