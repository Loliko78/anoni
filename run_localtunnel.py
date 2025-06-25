#!/usr/bin/env python3
"""
LocalTunnel Runner for Flask App
Runs LocalTunnel with fixed subdomain on port 10000
"""

import subprocess
import sys
import time
import os
import signal
from threading import Thread

def check_nodejs():
    """Проверяет установлен ли Node.js"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Node.js найден: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js не найден!")
        print("Установите Node.js с https://nodejs.org/")
        return False

def check_localtunnel():
    """Проверяет установлен ли localtunnel"""
    try:
        result = subprocess.run(['lt', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ LocalTunnel найден: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ LocalTunnel не найден!")
        print("Устанавливаю LocalTunnel...")
        try:
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], 
                         check=True, capture_output=True)
            print("✅ LocalTunnel установлен!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки LocalTunnel!")
            return False

def run_flask():
    """Запускает Flask приложение"""
    print("🚀 Запускаю Flask приложение...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def run_localtunnel():
    """Запускает LocalTunnel"""
    print("🌐 Запускаю LocalTunnel...")
    print("Ожидаемый URL: https://harvestano.loca.lt")
    print("Порт: 10000")
    print()
    
    try:
        subprocess.run(['lt', '--port', '10000', '--subdomain', 'harvestano'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 LocalTunnel остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка LocalTunnel: {e}")
        print("Попробуйте альтернативные домены:")
        print("- harvestano-app")
        print("- harvestano-dev") 
        print("- harvestano-test")

def main():
    """Основная функция"""
    print("=" * 50)
    print("🌐 LocalTunnel Runner для Flask")
    print("=" * 50)
    print()
    
    # Проверяем зависимости
    if not check_nodejs():
        return
    
    if not check_localtunnel():
        return
    
    print()
    print("🎯 Настройки:")
    print("- Порт: 10000")
    print("- Домен: harvestano.loca.lt")
    print("- Flask: app.py")
    print()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем немного для запуска Flask
    print("⏳ Ждем запуска Flask...")
    time.sleep(3)
    
    # Запускаем LocalTunnel
    run_localtunnel()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 