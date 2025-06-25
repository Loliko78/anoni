#!/usr/bin/env python3
"""
Скрипт для исправления проблем с Tor
"""

import os
import platform
import subprocess
import sys
import time
from pathlib import Path

def check_tor_installation():
    """Проверяем установку Tor"""
    print("Проверка установки Tor...")
    
    # Проверяем в PATH
    try:
        result = subprocess.run(['tor', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Tor найден в PATH")
            return True
    except:
        pass
    
    # Проверяем локальные файлы
    tor_executable = 'tor.exe' if platform.system().lower() == "windows" else './tor'
    if os.path.exists(tor_executable):
        print(f"Tor найден локально: {tor_executable}")
        return True
    
    print("Tor не найден")
    return False

def check_tor_config():
    """Проверяем конфигурацию Tor"""
    print("Проверка конфигурации Tor...")
    
    if not os.path.exists('torrc'):
        print("Файл конфигурации torrc не найден")
        return False
    
    print("Файл конфигурации torrc найден")
    return True

def check_tor_directories():
    """Проверяем директории Tor"""
    print("Проверка директорий Tor...")
    
    directories = ['tor_hidden_service', 'tor_data']
    missing = []
    
    for directory in directories:
        if not os.path.exists(directory):
            missing.append(directory)
        else:
            print(f"Директория {directory} существует")
    
    if missing:
        print(f"Отсутствуют директории: {', '.join(missing)}")
        return False
    
    return True

def check_tor_process():
    """Проверяем, запущен ли процесс Tor"""
    print("Проверка процесса Tor...")
    
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq tor.exe'], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(['pgrep', 'tor'], capture_output=True, text=True)
        
        if 'tor' in result.stdout.lower():
            print("Процесс Tor запущен")
            return True
        else:
            print("Процесс Tor не запущен")
            return False
    except:
        print("Не удалось проверить процесс Tor")
        return False

def check_port_9050():
    """Проверяем, занят ли порт 9050"""
    print("Проверка порта 9050...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        
        if result == 0:
            print("Порт 9050 доступен")
            return True
        else:
            print("Порт 9050 занят или недоступен")
            return False
    except:
        print("Не удалось проверить порт 9050")
        return False

def create_tor_config():
    """Создаем конфигурацию Tor"""
    print("Создание конфигурации Tor...")
    
    config = """# Tor конфигурация для Harvestano
SocksPort 9050
HiddenServiceDir ./tor_hidden_service
HiddenServicePort 80 127.0.0.1:10000
DataDirectory ./tor_data
Log notice file ./tor.log
"""
    
    with open('torrc', 'w') as f:
        f.write(config)
    
    print("Конфигурация Tor создана")

def create_tor_directories():
    """Создаем директории Tor"""
    print("Создание директорий Tor...")
    
    directories = ['tor_hidden_service', 'tor_data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Директория {directory} создана")

def kill_tor_process():
    """Останавливаем процесс Tor"""
    print("Остановка процесса Tor...")
    
    try:
        if platform.system().lower() == "windows":
            subprocess.run(['taskkill', '/F', '/IM', 'tor.exe'], 
                         capture_output=True)
        else:
            subprocess.run(['pkill', 'tor'], capture_output=True)
        
        print("Процесс Tor остановлен")
        time.sleep(2)  # Ждем завершения
        return True
    except:
        print("Не удалось остановить процесс Tor")
        return False

def start_tor():
    """Запускаем Tor"""
    print("Запуск Tor...")
    
    try:
        if platform.system().lower() == "windows":
            subprocess.Popen(['tor.exe', '-f', 'torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['./tor', '-f', 'torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        print("Tor запущен")
        time.sleep(5)  # Ждем инициализации
        return True
    except Exception as e:
        print(f"Ошибка запуска Tor: {e}")
        return False

def get_onion_address():
    """Получаем .onion адрес"""
    hostname_file = Path('tor_hidden_service/hostname')
    
    if hostname_file.exists():
        with open(hostname_file, 'r') as f:
            onion_address = f.read().strip()
        print(f"Onion адрес: {onion_address}")
        return onion_address
    else:
        print("Onion адрес еще не сгенерирован")
        return None

def main():
    print("Исправление проблем с Tor")
    print("=" * 40)
    
    issues_found = []
    fixes_applied = []
    
    # Проверяем установку
    if not check_tor_installation():
        issues_found.append("Tor не установлен")
        print("\nРешение: Установите Tor Browser или используйте:")
        print("   python manual_tor_setup.py")
        print("   install_tor_browser.bat")
        return
    
    # Проверяем конфигурацию
    if not check_tor_config():
        issues_found.append("Отсутствует конфигурация")
        create_tor_config()
        fixes_applied.append("Создана конфигурация")
    
    # Проверяем директории
    if not check_tor_directories():
        issues_found.append("Отсутствуют директории")
        create_tor_directories()
        fixes_applied.append("Созданы директории")
    
    # Проверяем процесс
    if check_tor_process():
        print("\nTor уже запущен. Останавливаем...")
        kill_tor_process()
        fixes_applied.append("Остановлен старый процесс")
    
    # Проверяем порт
    if not check_port_9050():
        issues_found.append("Порт 9050 недоступен")
        print("\nРешение: Проверьте файрвол или измените порт в torrc")
    
    # Запускаем Tor
    if start_tor():
        fixes_applied.append("Tor запущен")
        
        # Ждем генерации адреса
        print("\nОжидание генерации .onion адреса...")
        time.sleep(10)
        
        onion_address = get_onion_address()
        if onion_address:
            print(f"\nВаш сайт доступен: http://{onion_address}")
        else:
            print("\nOnion адрес еще не готов. Подождите еще несколько минут.")
    
    # Выводим результаты
    print("\n" + "=" * 40)
    print("Результаты проверки:")
    
    if issues_found:
        print(f"Проблемы: {len(issues_found)}")
        for issue in issues_found:
            print(f"   - {issue}")
    else:
        print("Проблем не найдено")
    
    if fixes_applied:
        print(f"Исправления: {len(fixes_applied)}")
        for fix in fixes_applied:
            print(f"   - {fix}")
    
    print("\nРекомендации:")
    print("1. Проверьте статус: python check_tor_status.py")
    print("2. Запустите сервер: python run_with_tor.py")
    print("3. Если проблемы остались, используйте: install_tor_browser.bat")

if __name__ == "__main__":
    main() 