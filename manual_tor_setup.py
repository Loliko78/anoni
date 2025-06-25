#!/usr/bin/env python3
"""
Альтернативный скрипт для установки Tor
"""

import os
import platform
import subprocess
import sys

def check_tor_installed():
    """Проверяем, установлен ли Tor"""
    print("Проверяем установленный Tor...")
    
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
    
    return False

def install_via_package_manager():
    """Устанавливаем Tor через пакетный менеджер"""
    system = platform.system().lower()
    
    print(f"Попытка установки через пакетный менеджер для {system}...")
    
    if system == "windows":
        print("Для Windows рекомендуется:")
        print("1. Скачать Tor Browser с https://www.torproject.org/")
        print("2. Или использовать Chocolatey: choco install tor")
        print("3. Или использовать Scoop: scoop install tor")
        return False
    
    elif system == "linux":
        # Определяем дистрибутив
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    print("Устанавливаем Tor для Ubuntu/Debian...")
                    subprocess.run(['sudo', 'apt', 'update'])
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'tor'])
                    return True
                elif 'fedora' in content or 'rhel' in content or 'centos' in content:
                    print("Устанавливаем Tor для Fedora/RHEL/CentOS...")
                    subprocess.run(['sudo', 'dnf', 'install', '-y', 'tor'])
                    return True
                elif 'arch' in content:
                    print("Устанавливаем Tor для Arch Linux...")
                    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'tor'])
                    return True
        except:
            pass
        
        print("Не удалось определить дистрибутив Linux")
        print("Попробуйте установить Tor вручную:")
        print("Ubuntu/Debian: sudo apt install tor")
        print("Fedora/RHEL: sudo dnf install tor")
        print("Arch: sudo pacman -S tor")
        return False
    
    elif system == "darwin":
        print("Устанавливаем Tor для macOS...")
        try:
            # Проверяем Homebrew
            result = subprocess.run(['brew', '--version'], capture_output=True)
            if result.returncode == 0:
                subprocess.run(['brew', 'install', 'tor'])
                return True
            else:
                print("Homebrew не найден. Установите Homebrew или скачайте Tor Browser")
                return False
        except:
            print("Ошибка установки через Homebrew")
            return False
    
    return False

def download_tor_browser():
    """Скачиваем Tor Browser"""
    system = platform.system().lower()
    
    print("Скачиваем Tor Browser...")
    
    if system == "windows":
        url = "https://www.torproject.org/dist/torbrowser/12.5.4/torbrowser-install-12.5.4_en-US.exe"
    elif system == "linux":
        url = "https://www.torproject.org/dist/torbrowser/12.5.4/tor-browser-linux64-12.5.4_en-US.tar.xz"
    elif system == "darwin":
        url = "https://www.torproject.org/dist/torbrowser/12.5.4/TorBrowser-12.5.4-osx64_en-US.dmg"
    else:
        print("Неподдерживаемая платформа")
        return False
    
    print(f"Скачайте Tor Browser с: {url}")
    print("После установки Tor Browser, запустите этот скрипт снова")
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
    from pathlib import Path
    
    directories = ['tor_hidden_service', 'tor_data']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("Директории Tor созданы")

def main():
    print("Альтернативная установка Tor")
    print("=" * 40)
    
    # Проверяем, установлен ли уже Tor
    if check_tor_installed():
        print("Tor уже установлен!")
        create_tor_config()
        create_tor_directories()
        print("\nНастройка завершена. Запустите: python run_with_tor.py")
        return
    
    print("Tor не найден. Выберите способ установки:")
    print("1. Автоматическая установка через пакетный менеджер")
    print("2. Скачать Tor Browser")
    print("3. Ручная установка")
    print("4. Выход")
    
    choice = input("\nВведите номер (1-4): ").strip()
    
    if choice == "1":
        if install_via_package_manager():
            print("Tor установлен успешно!")
            create_tor_config()
            create_tor_directories()
        else:
            print("Не удалось установить автоматически")
    
    elif choice == "2":
        download_tor_browser()
    
    elif choice == "3":
        print("\nРучная установка:")
        print("1. Скачайте Tor с https://www.torproject.org/")
        print("2. Распакуйте в текущую директорию")
        print("3. Убедитесь, что файл tor.exe (Windows) или ./tor (Linux/Mac) существует")
        print("4. Запустите этот скрипт снова")
    
    elif choice == "4":
        print("Выход...")
        return
    
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main() 