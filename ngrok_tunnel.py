#!/usr/bin/env python3
"""
ngrok Tunnel for Flask App
Fast and reliable tunneling
"""

import subprocess
import sys
import time
from threading import Thread

def run_flask():
    """Запускает Flask приложение"""
    print("🚀 Запускаю Flask приложение на порту 10000...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def run_ngrok():
    """Запускает ngrok туннель"""
    print("🌐 Запускаю ngrok туннель...")
    print("Ожидаемый URL: https://[random].ngrok.io")
    print("Порт: 10000")
    print()
    
    try:
        # ngrok команда
        subprocess.run(['ngrok', 'http', '10000'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 ngrok остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка ngrok: {e}")
        print("Установите ngrok:")
        print("1. Скачайте с https://ngrok.com/")
        print("2. Распакуйте в папку проекта")
        print("3. Запустите снова")

def main():
    """Основная функция"""
    print("=" * 50)
    print("🌐 ngrok Tunnel для Flask")
    print("=" * 50)
    print()
    
    print("🎯 Настройки:")
    print("- Flask порт: 10000")
    print("- ngrok домен: [random].ngrok.io")
    print("- URL: https://[random].ngrok.io")
    print()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем немного для запуска Flask
    print("⏳ Ждем запуска Flask на порту 10000...")
    time.sleep(5)
    
    print("✅ Flask запущен! Теперь запускаю ngrok...")
    print()
    
    # Запускаем ngrok
    run_ngrok()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 