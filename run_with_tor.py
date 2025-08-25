#!/usr/bin/env python3
"""
Скрипт для запуска Flask приложения с Tor
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

def check_tor_running():
    """Проверяем, запущен ли Tor"""
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tor.exe'], 
                                  capture_output=True, text=True)
            return 'tor.exe' in result.stdout
        else:
            result = subprocess.run(['pgrep', 'tor'], capture_output=True)
            return result.returncode == 0
    except:
        return False

def start_tor():
    """Запускаем Tor если он не запущен"""
    if check_tor_running():
        print("✅ Tor уже запущен")
        return True
    
    print("🚀 Запускаем Tor...")
    
    try:
        if platform.system().lower() == "windows":
            if os.path.exists('tor.exe'):
                subprocess.Popen(['tor.exe', '-f', 'torrc'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                print("❌ Tor не найден. Запустите сначала tor_setup.py")
                return False
        else:
            if os.path.exists('./tor'):
                subprocess.Popen(['./tor', '-f', 'torrc'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:
                print("❌ Tor не найден. Запустите сначала tor_setup.py")
                return False
        
        # Ждем запуска Tor
        print("⏳ Ждем запуска Tor...")
        time.sleep(15)
        
        if check_tor_running():
            print("✅ Tor успешно запущен")
            return True
        else:
            print("❌ Не удалось запустить Tor")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запуска Tor: {e}")
        return False

def get_onion_address():
    """Получаем .onion адрес"""
    hostname_file = Path('tor_hidden_service/hostname')
    
    if hostname_file.exists():
        with open(hostname_file, 'r') as f:
            onion_address = f.read().strip()
        return onion_address
    else:
        return None

def start_flask_app():
    """Запускаем Flask приложение"""
    print("🌐 Запускаем Flask приложение...")
    
    # Устанавливаем переменные окружения для Tor
    os.environ['FLASK_ENV'] = 'production'
    os.environ['TOR_ENABLED'] = 'true'
    
    # Импортируем и запускаем Flask приложение
    try:
        from app import app, socketio
        
        # Получаем onion адрес
        onion_address = get_onion_address()
        if onion_address:
            print(f"🔗 Onion адрес: http://{onion_address}")
        
        print("🚀 Запускаем сервер на порту 10000...")
        print("📱 Android приложение будет подключаться через Tor")
        
        # Запускаем с SocketIO
        socketio.run(app, debug=False, host='127.0.0.1', port=10000)
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Ошибка запуска Flask: {e}")

def main():
    print("🌐 Запуск Harvestano с Tor")
    print("=" * 40)
    
    # Проверяем наличие конфигурации Tor
    if not os.path.exists('torrc'):
        print("❌ Конфигурация Tor не найдена")
        print("Запустите сначала: python tor_setup.py")
        return
    
    # Запускаем Tor
    if not start_tor():
        return
    
    # Получаем onion адрес
    onion_address = get_onion_address()
    if onion_address:
        print(f"🎯 Ваш сайт будет доступен по адресу: http://{onion_address}")
    else:
        print("⚠️ Onion адрес еще не сгенерирован. Подождите...")
    
    print("\n📋 Инструкции для Android приложения:")
    print("1. Установите Orbot (Tor для Android)")
    print("2. Запустите Orbot и включите VPN")
    print("3. В Android приложении сайт будет доступен через Tor")
    
    # Запускаем Flask
    start_flask_app()

if __name__ == "__main__":
    main() 