#!/usr/bin/env python3
"""
Alternative Tunneling Solutions for Flask App
Replaces LocalTunnel with other options
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

def run_flask():
    """Запускает Flask приложение"""
    print("🚀 Запускаю Flask приложение на порту 10000...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def run_serveo():
    """Запускает Serveo"""
    print("🌐 Запускаю Serveo...")
    print("Ожидаемый URL: https://harvestano.serveo.net")
    print()
    
    try:
        subprocess.run(['ssh', '-R', '80:localhost:10000', 'serveo.net'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 Serveo остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Serveo: {e}")
        print("Попробуйте другой домен:")
        print("- harvestano-dev.serveo.net")
        print("- harvestano-test.serveo.net")

def run_ngrok():
    """Запускает ngrok"""
    print("🌐 Запускаю ngrok...")
    print("Ожидаемый URL: https://[random].ngrok.io")
    print()
    
    try:
        subprocess.run(['ngrok', 'http', '10000'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 ngrok остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка ngrok: {e}")
        print("Установите ngrok с https://ngrok.com/")

def run_cloudflared():
    """Запускает Cloudflare Tunnel"""
    print("🌐 Запускаю Cloudflare Tunnel...")
    print("Ожидаемый URL: https://[random].trycloudflare.com")
    print()
    
    try:
        subprocess.run(['cloudflared', 'tunnel', '--url', 'http://localhost:10000'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 Cloudflare Tunnel остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Cloudflare Tunnel: {e}")
        print("Установите cloudflared с https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")

def run_pagekite():
    """Запускает PageKite"""
    print("🌐 Запускаю PageKite...")
    print("Ожидаемый URL: https://harvestano.pagekite.me")
    print()
    
    try:
        subprocess.run(['pagekite', '10000', 'harvestano.pagekite.me'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 PageKite остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка PageKite: {e}")
        print("Установите PageKite с https://pagekite.net/")

def run_telebit():
    """Запускает Telebit"""
    print("🌐 Запускаю Telebit...")
    print("Ожидаемый URL: https://harvestano.telebit.io")
    print()
    
    try:
        subprocess.run(['telebit', '--port', '10000', '--subdomain', 'harvestano'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 Telebit остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Telebit: {e}")
        print("Установите Telebit: npm install -g telebit")

def show_menu():
    """Показывает меню выбора"""
    print("=" * 50)
    print("🌐 Альтернативные туннели для Flask")
    print("=" * 50)
    print()
    print("Выберите туннель:")
    print("1. Serveo (ssh) - https://harvestano.serveo.net")
    print("2. ngrok - https://[random].ngrok.io")
    print("3. Cloudflare Tunnel - https://[random].trycloudflare.com")
    print("4. PageKite - https://harvestano.pagekite.me")
    print("5. Telebit - https://harvestano.telebit.io")
    print("6. Выход")
    print()

def main():
    """Основная функция"""
    while True:
        show_menu()
        
        choice = input("Введите номер (1-6): ").strip()
        
        if choice == "1":
            print("\n🚀 Запуск Serveo...")
            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()
            time.sleep(3)
            run_serveo()
            break
            
        elif choice == "2":
            print("\n🚀 Запуск ngrok...")
            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()
            time.sleep(3)
            run_ngrok()
            break
            
        elif choice == "3":
            print("\n🚀 Запуск Cloudflare Tunnel...")
            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()
            time.sleep(3)
            run_cloudflared()
            break
            
        elif choice == "4":
            print("\n🚀 Запуск PageKite...")
            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()
            time.sleep(3)
            run_pagekite()
            break
            
        elif choice == "5":
            print("\n🚀 Запуск Telebit...")
            flask_thread = Thread(target=run_flask, daemon=True)
            flask_thread.start()
            time.sleep(3)
            run_telebit()
            break
            
        elif choice == "6":
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 