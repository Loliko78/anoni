#!/usr/bin/env python3
"""
Скрипт для настройки домена harvestano.onion
"""

import os
import subprocess
import time
import platform
from pathlib import Path

def create_custom_onion_config():
    """Создаем конфигурацию для домена harvestano.onion"""
    
    # Создаем специальную конфигурацию для получения нужного домена
    config = """# Tor конфигурация для harvestano.onion
SocksPort 9050
HiddenServiceDir ./harvestano_onion_service
HiddenServicePort 80 127.0.0.1:10000
DataDirectory ./harvestano_tor_data
Log notice file ./harvestano_tor.log

# Настройки для получения нужного домена
HiddenServiceVersion 3
"""
    
    with open('harvestano_torrc', 'w') as f:
        f.write(config)
    
    print("Конфигурация для harvestano.onion создана: harvestano_torrc")

def create_onion_directories():
    """Создаем директории для harvestano.onion"""
    directories = ['harvestano_onion_service', 'harvestano_tor_data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("Директории для harvestano.onion созданы")

def generate_onion_address():
    """Генерируем .onion адрес (может потребоваться несколько попыток)"""
    print("🔧 Генерация .onion адреса...")
    print("Это может занять некоторое время...")
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"Попытка {attempt}/{max_attempts}...")
        
        # Останавливаем предыдущий Tor если запущен
        stop_tor()
        
        # Запускаем Tor с новой конфигурацией
        if platform.system().lower() == "windows":
            subprocess.Popen(['tor.exe', '-f', 'harvestano_torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['./tor', '-f', 'harvestano_torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        # Ждем генерации адреса
        time.sleep(30)
        
        # Проверяем сгенерированный адрес
        hostname_file = Path('harvestano_onion_service/hostname')
        if hostname_file.exists():
            with open(hostname_file, 'r') as f:
                onion_address = f.read().strip()
            
            print(f"Сгенерирован адрес: {onion_address}")
            
            # Проверяем, содержит ли адрес "harvestano" (маловероятно, но возможно)
            if 'harvestano' in onion_address.lower():
                print("🎉 Удалось получить адрес с 'harvestano'!")
                return onion_address
            else:
                print(f"Адрес не содержит 'harvestano': {onion_address}")
                print("Продолжаем попытки...")
        
        time.sleep(5)
    
    # Если не удалось получить нужный адрес, используем последний сгенерированный
    hostname_file = Path('harvestano_onion_service/hostname')
    if hostname_file.exists():
        with open(hostname_file, 'r') as f:
            onion_address = f.read().strip()
        print(f"Используем сгенерированный адрес: {onion_address}")
        return onion_address
    
    return None

def stop_tor():
    """Останавливаем Tor процесс"""
    try:
        if platform.system().lower() == "windows":
            subprocess.run(['taskkill', '/f', '/im', 'tor.exe'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['pkill', 'tor'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
        time.sleep(2)
    except:
        pass

def update_android_config(onion_address):
    """Обновляем конфигурацию Android приложения"""
    if not onion_address:
        return
    
    # Обновляем MainActivity.java
    main_activity_path = Path('HarvestanoApp/app/src/main/java/com/harvestano/app/MainActivity.java')
    
    if main_activity_path.exists():
        with open(main_activity_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем заглушку на реальный адрес
        content = content.replace(
            'return "harvestano.onion";',
            f'return "{onion_address}";'
        )
        
        with open(main_activity_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Android конфигурация обновлена с адресом: {onion_address}")

def create_startup_script(onion_address):
    """Создаем скрипт для запуска с harvestano.onion"""
    script_content = f"""@echo off
echo ========================================
echo    Запуск Harvestano с Tor
echo ========================================
echo.

REM Останавливаем предыдущий Tor
taskkill /f /im tor.exe 2>nul

REM Запускаем Tor с конфигурацией harvestano.onion
echo Запускаем Tor сервер...
start /b tor.exe -f harvestano_torrc

REM Ждем запуска Tor
timeout /t 15 /nobreak >nul

REM Запускаем Flask приложение
echo Запускаем Flask приложение...
python run_with_tor.py

pause
"""
    
    with open('start_harvestano_tor.bat', 'w') as f:
        f.write(script_content)
    
    print("Скрипт запуска создан: start_harvestano_tor.bat")

def main():
    print("🔧 Настройка harvestano.onion")
    print("=" * 50)
    
    # Проверяем наличие Tor
    tor_executable = 'tor.exe' if platform.system().lower() == "windows" else './tor'
    
    if not os.path.exists(tor_executable):
        print("❌ Tor не найден. Запустите сначала tor_setup.py")
        return
    
    # Создаем конфигурацию и директории
    create_custom_onion_config()
    create_onion_directories()
    
    # Генерируем .onion адрес
    onion_address = generate_onion_address()
    
    if onion_address:
        print(f"\n🎉 Настройка завершена!")
        print(f"Onion адрес: http://{onion_address}")
        
        # Обновляем Android конфигурацию
        update_android_config(onion_address)
        
        # Создаем скрипт запуска
        create_startup_script(onion_address)
        
        # Сохраняем адрес
        with open('harvestano_onion_address.txt', 'w') as f:
            f.write(onion_address)
        
        print("\n📋 Инструкции:")
        print("1. Запустите: start_harvestano_tor.bat")
        print("2. Соберите APK: build_tor_apk.bat")
        print("3. Установите APK на Android устройство")
        print("4. Установите Orbot и включите VPN")
        print("5. Запустите приложение")
        
    else:
        print("❌ Не удалось сгенерировать .onion адрес")

if __name__ == "__main__":
    main() 