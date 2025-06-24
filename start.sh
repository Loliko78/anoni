#!/bin/bash

# Установка переменной PORT по умолчанию, если не задана
export PORT=${PORT:-5000}

# Запуск приложения с поддержкой Flask-SocketIO через eventlet
exec gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT 