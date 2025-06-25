#!/usr/bin/env python3
"""
Скрипт для настройки Tor сервера с доменом .onion
"""

import os
import subprocess
import sys
import platform
import requests
from pathlib import Path
import time

def download_tor():
    """Скачиваем Tor для текущей платформы"""
    system = platform.system().lower()
    arch = platform.machine().lower()
    
    # Определяем URL для скачивания
    if system == "windows":
        if "64" in arch:
            urls = [
                "https://dist.torproject.org/tor-0.4.8.10-win64.zip",
                "https://archive.torproject.org/tor-package-archive/tor-0.4.8.10-win64.zip"
            ]
        else:
            urls = [
                "https://dist.torproject.org/tor-0.4.8.10-win32.zip",
                "https://archive.torproject.org/tor-package-archive/tor-0.4.8.10-win32.zip"
            ]
    elif system == "linux":
        if "x86_64" in arch:
            urls = [
                "https://dist.torproject.org/tor-0.4.8.10-linux-x86_64.tar.gz",
                "https://archive.torproject.org/tor-package-archive/tor-0.4.8.10-linux-x86_64.tar.gz"
            ]
        else:
            urls = [
                "https://dist.torproject.org/tor-0.4.8.10-linux-i686.tar.gz",
                "https://archive.torproject.org/tor-package-archive/tor-0.4.8.10-linux-i686.tar.gz"
            ]
    elif system == "darwin":
        urls = [
            "https://dist.torproject.org/tor-0.4.8.10-osx64.tar.gz",
            "https://archive.torproject.org/tor-package-archive/tor-0.4.8.10-osx64.tar.gz"
        ]
    else:
        print(f"Неподдерживаемая платформа: {system} {arch}")
        return False
    
    print(f"Скачиваем Tor для {system} {arch}...")
    
    # Пробуем разные URL с повторными попытками
    for url in urls:
        for attempt in range(3):  # 3 попытки для каждого URL
            try:
                print(f"Попытка {attempt + 1}/3: {url}")
                
                # Увеличиваем таймаут и добавляем заголовки
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, stream=True, timeout=60, headers=headers)
                response.raise_for_status()
                
                filename = url.split('/')[-1]
                print(f"Скачиваем {filename}...")
                
                # Скачиваем файл с прогрессом
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"\rПрогресс: {progress:.1f}%", end='', flush=True)
                
                print(f"\nTor скачан: {filename}")
                return filename
                
            except requests.exceptions.Timeout:
                print(f"Таймаут при попытке {attempt + 1}")
                if attempt < 2:
                    print("Повторяем через 5 секунд...")
                    time.sleep(5)
                continue
            except requests.exceptions.ConnectionError as e:
                print(f"Ошибка подключения: {e}")
                if attempt < 2:
                    print("Повторяем через 5 секунд...")
                    time.sleep(5)
                continue
            except Exception as e:
                print(f"Ошибка скачивания: {e}")
                if attempt < 2:
                    print("Повторяем через 5 секунд...")
                    time.sleep(5)
                continue
    
    print("Не удалось скачать Tor ни с одного источника")
    return False

def check_existing_tor():
    """Проверяем, установлен ли уже Tor"""
    tor_executable = 'tor.exe' if platform.system().lower() == "windows" else './tor'
    
    if os.path.exists(tor_executable):
        print(f"Tor уже найден: {tor_executable}")
        return True
    
    # Проверяем в PATH
    try:
        result = subprocess.run(['tor', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Tor найден в PATH")
            return True
    except:
        pass
    
    return False

def extract_tor(filename):
    """Распаковываем Tor"""
    import zipfile
    import tarfile
    
    print(f"Распаковываем {filename}...")
    
    try:
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall('.')
        elif filename.endswith('.tar.gz'):
            with tarfile.open(filename, 'r:gz') as tar_ref:
                tar_ref.extractall('.')
        
        print("Tor распакован")
        return True
    except Exception as e:
        print(f"Ошибка распаковки: {e}")
        return False

def create_tor_config():
    """Создаем конфигурацию Tor"""
    config = """# Tor конфигурация для Harvestano
SocksPort 9050
HiddenServiceDir ./tor_hidden_service
HiddenServicePort 80 127.0.0.1:10000
DataDirectory ./tor_data
Log notice file ./tor.log
"""
    
    with open('torrc', 'w') as f:
        f.write(config)
    
    print("Конфигурация Tor создана: torrc")

def create_tor_directories():
    """Создаем необходимые директории"""
    directories = ['tor_hidden_service', 'tor_data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("Директории Tor созданы")

def get_onion_address():
    """Получаем .onion адрес"""
    hostname_file = Path('tor_hidden_service/hostname')
    
    if hostname_file.exists():
        with open(hostname_file, 'r') as f:
            onion_address = f.read().strip()
        print(f"Onion адрес: {onion_address}")
        return onion_address
    else:
        print("Onion адрес еще не сгенерирован. Запустите Tor сервер.")
        return None

def start_tor_server():
    """Запускаем Tor сервер"""
    print("Запускаем Tor сервер...")
    
    try:
        # Запускаем Tor в фоновом режиме
        if platform.system().lower() == "windows":
            subprocess.Popen(['tor.exe', '-f', 'torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(['./tor', '-f', 'torrc'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        print("Tor сервер запущен в фоновом режиме")
        print("Подождите несколько секунд для генерации .onion адреса...")
        
        # Ждем генерации адреса
        import time
        time.sleep(10)
        
        onion_address = get_onion_address()
        if onion_address:
            print(f"🎉 Ваш сайт доступен по адресу: http://{onion_address}")
            return onion_address
        
    except Exception as e:
        print(f"Ошибка запуска Tor: {e}")
        return None

def main():
    print("🔧 Настройка Tor сервера для Harvestano")
    print("=" * 50)
    
    # Проверяем, установлен ли уже Tor
    if check_existing_tor():
        print("Используем существующий Tor")
    else:
        print("Tor не найден. Скачиваем...")
        filename = download_tor()
        if filename:
            if not extract_tor(filename):
                print("Не удалось распаковать Tor")
                return
        else:
            print("Не удалось скачать Tor")
            print("\nАльтернативные способы установки:")
            print("1. Скачайте Tor вручную с https://www.torproject.org/")
            print("2. Установите через пакетный менеджер вашей системы")
            print("3. Используйте Tor Browser")
            return
    
    # Создаем конфигурацию и директории
    create_tor_config()
    create_tor_directories()
    
    # Запускаем Tor сервер
    onion_address = start_tor_server()
    
    if onion_address:
        print("\n📋 Инструкции:")
        print("1. Убедитесь, что Flask приложение запущено на порту 10000")
        print("2. Tor сервер работает в фоновом режиме")
        print(f"3. Ваш сайт доступен по адресу: http://{onion_address}")
        print("4. Для остановки Tor используйте: pkill tor (Linux/Mac) или taskkill /f /im tor.exe (Windows)")
        
        # Сохраняем адрес в файл
        with open('onion_address.txt', 'w') as f:
            f.write(onion_address)
        
        print(f"\nOnion адрес сохранен в файл: onion_address.txt")

if __name__ == "__main__":
    main() 