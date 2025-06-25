#!/usr/bin/env python3
"""
Simple Web Server for Flask App
Runs on local network without tunnels
"""

import subprocess
import sys
import time
import socket
import requests
from threading import Thread

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        # Подключаемся к внешнему серверу чтобы узнать наш IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_port(port):
    """Проверяет доступность порта"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def run_flask():
    """Запускает Flask приложение"""
    print("🚀 Запускаю Flask приложение...")
    try:
        # Запускаем Flask на всех интерфейсах
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def show_network_info():
    """Показывает информацию о сети"""
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🌐 Веб-сервер запущен в локальной сети")
    print("=" * 60)
    print()
    print("📱 Доступные URL:")
    print(f"   Локально:     http://localhost:10000")
    print(f"   В сети:       http://{local_ip}:10000")
    print()
    print("📋 Инструкция:")
    print("1. Убедитесь что устройства в одной сети")
    print("2. Откройте браузер на телефоне/планшете")
    print("3. Введите URL: http://" + local_ip + ":10000")
    print()
    print("⚠️  Важно:")
    print("- Брандмауэр Windows может блокировать подключения")
    print("- Разрешите доступ для Python в брандмауэре")
    print("- Устройства должны быть в одной Wi-Fi сети")
    print()
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 60)

def main():
    """Основная функция"""
    print("🌐 Простой веб-сервер для Flask")
    print()
    
    # Проверяем порт
    if check_port(10000):
        print("⚠️  Порт 10000 уже занят!")
        print("Остановите другие приложения на этом порту")
        return
    
    print("🎯 Настройки:")
    print("- Порт: 10000")
    print("- Доступ: Локальная сеть")
    print("- Туннели: Не используются")
    print()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем запуска Flask
    print("⏳ Запускаю Flask...")
    time.sleep(3)
    
    # Показываем информацию о сети
    show_network_info()
    
    # Ждем завершения
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 