#!/usr/bin/env python3
"""
Fixed LocalTunnel for Flask App
Handles IP endpoint issues
"""

import subprocess
import sys
import time
import socket
from threading import Thread

def get_local_ip():
    """Получает локальный IP адрес"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

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

def install_localtunnel():
    """Устанавливает localtunnel"""
    print("📦 Устанавливаю localtunnel...")
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
    print("🚀 Запускаю Flask приложение на порту 10000...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def run_localtunnel_fixed():
    """Запускает LocalTunnel с исправленными настройками"""
    print("🌐 Запускаю LocalTunnel (исправленная версия)...")
    print("Ожидаемый URL: https://harvestano.loca.lt")
    print("Порт: 10000")
    print()
    
    local_ip = get_local_ip()
    print(f"📍 Ваш IP: {local_ip}")
    print()
    
    try:
        # Пробуем разные варианты команды
        commands = [
            ['lt', '--port', '10000', '--subdomain', 'harvestano'],
            ['lt', '--port', '10000', '--host', 'http://localhost:10000', '--subdomain', 'harvestano'],
            ['lt', '--port', '10000', '--local-host', local_ip, '--subdomain', 'harvestano'],
            ['lt', '--port', '10000', '--subdomain', 'harvestano', '--local-host', '0.0.0.0']
        ]
        
        for i, cmd in enumerate(commands, 1):
            print(f"Попытка {i}: {' '.join(cmd)}")
            try:
                subprocess.run(cmd, check=True)
                break
            except subprocess.CalledProcessError as e:
                print(f"❌ Попытка {i} не удалась: {e}")
                if i < len(commands):
                    print("Пробую следующий вариант...")
                    time.sleep(2)
                else:
                    print("❌ Все варианты не сработали")
                    print("Попробуйте альтернативные домены:")
                    print("- harvestano-app")
                    print("- harvestano-dev")
                    print("- harvestano-test")
                    
    except KeyboardInterrupt:
        print("\n🛑 LocalTunnel остановлен")

def main():
    """Основная функция"""
    print("=" * 50)
    print("🌐 Исправленный LocalTunnel для Flask")
    print("=" * 50)
    print()
    
    # Проверяем зависимости
    if not check_nodejs():
        return
    
    # Устанавливаем localtunnel если нужно
    try:
        subprocess.run(['lt', '--version'], capture_output=True, check=True)
        print("✅ LocalTunnel найден!")
    except:
        if not install_localtunnel():
            return
    
    print()
    print("🎯 Настройки:")
    print("- Flask порт: 10000")
    print("- LocalTunnel домен: harvestano.loca.lt")
    print("- URL: https://harvestano.loca.lt")
    print()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем немного для запуска Flask
    print("⏳ Ждем запуска Flask на порту 10000...")
    time.sleep(5)
    
    print("✅ Flask запущен! Теперь запускаю LocalTunnel...")
    print()
    
    # Запускаем LocalTunnel с исправлениями
    run_localtunnel_fixed()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 