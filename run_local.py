#!/usr/bin/env python3
"""
Скрипт для локального запуска Flask приложения
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

if __name__ == '__main__':
    print("🚀 Запуск Flask приложения локально...")
    print("📱 Локальный доступ: http://0.0.0.0:5000")
    print("💡 Нажмите Ctrl+C для остановки")
    
    # Check database first
    print("🔍 Проверка базы данных...")
    if not run_command("python check_db.py"):
        print("❌ Ошибка проверки базы данных")
        sys.exit(1)
    
    try:
        from app import app, socketio
        print("🔌 Запуск с SocketIO...")
        # Пробуем запустить с SocketIO
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"⚠️ SocketIO не запущен: {e}")
        print("🔄 Запуск в режиме Flask без WebSocket...")
        print("💡 Чат и звонки будут работать без реального времени")
        
        try:
            from app import app
            # Запускаем обычный Flask
            app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e2:
            print(f"❌ Ошибка запуска Flask: {e2}")
            sys.exit(1) 