# 🔧 Исправление ошибок Render

## ✅ Исправлено:

1. **Конфликт версий** - обновлен `requirements.txt`
2. **Переменные окружения** - добавлен `render.yaml`

## 🚀 Новый деплой:

1. **Загрузите исправления:**
   ```bash
   git add .
   git commit -m "Fixed Werkzeug version conflict and added render.yaml"
   git push
   ```

2. **На Render:**
   - Нажмите "Manual Deploy" 
   - Или создайте новый сервис с этими настройками:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn -c gunicorn_config.py app:app`

## 📍 Где найти переменные окружения в Render:

1. Откройте ваш сервис в Dashboard
2. Перейдите на вкладку **"Environment"** (слева в меню)
3. Нажмите **"Add Environment Variable"**
4. Добавьте:
   - Key: `TELEGRAM_BOT_TOKEN`, Value: `7293066749:AAFg5fXAVZkPx6s7R3drwGEV5pjKZY1f-PM`
   - Key: `TELEGRAM_CHAT_ID`, Value: `564049757`

## 🎯 Альтернатива:

Если не можете найти Environment - используйте `render.yaml` (уже создан).
Render автоматически подхватит переменные из этого файла.

Теперь должно работать без ошибок!