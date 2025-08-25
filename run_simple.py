#!/usr/bin/env python3
"""
Простой скрипт для запуска Flask приложения без SocketIO
"""

from app import app, socketio
import threading
import time

def run_socketio():
    """Запуск SocketIO в отдельном потоке"""
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"⚠️ SocketIO не запущен: {e}")
        print("💡 Приложение будет работать без WebSocket функций")

if __name__ == '__main__':
    print("🚀 Запуск Flask приложения...")
    print("📱 Локальный доступ: http://0.0.0.0:5000")
    print("💡 Нажмите Ctrl+C для остановки")
    
    try:
        # Пробуем запустить с SocketIO
        run_socketio()
    except Exception as e:
        print(f"❌ Ошибка SocketIO: {e}")
        print("🔄 Запуск в режиме Flask без WebSocket...")
        
        # Запускаем обычный Flask
        app.run(host='0.0.0.0', port=5000, debug=False) 