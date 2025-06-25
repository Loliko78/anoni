#!/usr/bin/env python3
"""
Скрипт для проверки статуса Tor и .onion адреса
"""

import os
import subprocess
import platform
import requests
import time
from pathlib import Path

def check_tor_process():
    """Проверяем, запущен ли процесс Tor"""
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

def get_onion_address():
    """Получаем .onion адрес"""
    # Проверяем разные возможные места
    possible_files = [
        'harvestano_onion_service/hostname',
        'tor_hidden_service/hostname',
        'harvestano_onion_address.txt',
        'onion_address.txt'
    ]
    
    for file_path in possible_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                address = f.read().strip()
                if address and '.onion' in address:
                    return address
    
    return None

def test_onion_connectivity(address):
    """Тестируем доступность .onion адреса"""
    if not address:
        return False, "Адрес не найден"
    
    try:
        # Настраиваем прокси для Tor (если доступен)
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        
        # Пробуем подключиться
        response = requests.get(f'http://{address}', 
                              proxies=proxies, 
                              timeout=30)
        
        if response.status_code == 200:
            return True, "Сайт доступен"
        else:
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.ProxyError:
        return False, "Ошибка прокси (Tor не запущен?)"
    except requests.exceptions.ConnectionError:
        return False, "Ошибка подключения"
    except requests.exceptions.Timeout:
        return False, "Таймаут подключения"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def check_tor_config():
    """Проверяем конфигурацию Tor"""
    config_files = ['torrc', 'harvestano_torrc']
    config_status = {}
    
    for config_file in config_files:
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                content = f.read()
                config_status[config_file] = {
                    'exists': True,
                    'has_hidden_service': 'HiddenServiceDir' in content,
                    'has_port': 'HiddenServicePort' in content
                }
        else:
            config_status[config_file] = {
                'exists': False,
                'has_hidden_service': False,
                'has_port': False
            }
    
    return config_status

def main():
    print("Проверка статуса Tor и .onion адреса")
    print("=" * 50)
    
    # Проверяем процесс Tor
    print("1. Проверка процесса Tor...")
    tor_running = check_tor_process()
    if tor_running:
        print("   [OK] Tor процесс запущен")
    else:
        print("   [ОШИБКА] Tor процесс не запущен")
    
    # Проверяем конфигурацию
    print("\n2. Проверка конфигурации...")
    config_status = check_tor_config()
    for config_file, status in config_status.items():
        if status['exists']:
            print(f"   [OK] {config_file} найден")
            if status['has_hidden_service']:
                print("   [OK] HiddenService настроен")
            if status['has_port']:
                print("   [OK] HiddenServicePort настроен")
        else:
            print(f"   [ОШИБКА] {config_file} не найден")
    
    # Получаем .onion адрес
    print("\n3. Проверка .onion адреса...")
    onion_address = get_onion_address()
    if onion_address:
        print(f"   [OK] Onion адрес: {onion_address}")
        
        # Тестируем доступность
        print("\n4. Тестирование доступности...")
        accessible, message = test_onion_connectivity(onion_address)
        if accessible:
            print(f"   [OK] {message}")
        else:
            print(f"   [ОШИБКА] {message}")
    else:
        print("   [ОШИБКА] Onion адрес не найден")
    
    # Рекомендации
    print("\nРекомендации:")
    
    if not tor_running:
        print("   * Запустите Tor: python tor_setup.py")
    
    if not onion_address:
        print("   * Настройте .onion адрес: python setup_harvestano_onion.py")
    
    if onion_address and not check_tor_process():
        print("   * Tor не запущен, но адрес найден. Запустите Tor сервер.")
    
    print("\nДля доступа к сайту используйте:")
    if onion_address:
        print(f"   http://{onion_address}")
    else:
        print("   (адрес не настроен)")
    
    print("\nДля Android приложения:")
    print("   * Установите Orbot")
    print("   * Включите VPN в Orbot")
    print("   * Запустите приложение")

if __name__ == "__main__":
    main() 