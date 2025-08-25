#!/usr/bin/env python3
"""
Cloudflare Tunnel for Flask App
Free and reliable tunneling
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_flask():
    """Запускает Flask приложение"""
    print("🚀 Запускаю Flask приложение на порту 10000...")
    try:
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Flask остановлен")

def check_cloudflared():
    """Проверяет установлен ли cloudflared"""
    try:
        result = subprocess.run(['cloudflared', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Cloudflared найден: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Cloudflared не найден!")
        print("Установите cloudflared:")
        print("1. Скачайте с https://github.com/cloudflare/cloudflared/releases")
        print("2. Распакуйте cloudflared.exe в папку проекта")
        print("3. Запустите снова")
        return False

def run_cloudflare():
    """Запускает Cloudflare Tunnel"""
    print("🌐 Запускаю Cloudflare Tunnel...")
    print("Ожидаемый URL: https://[random].trycloudflare.com")
    print("Порт: 10000")
    print()
    
    try:
        # Cloudflare Tunnel команда
        subprocess.run(['cloudflared', 'tunnel', '--url', 'http://localhost:10000'], 
                      check=True)
    except KeyboardInterrupt:
        print("\n🛑 Cloudflare Tunnel остановлен")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Cloudflare Tunnel: {e}")
        print("Проверьте установку cloudflared")

def download_cloudflared():
    """Скачивает cloudflared"""
    print("📥 Скачиваю cloudflared...")
    try:
        # Скачиваем cloudflared для Windows
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        subprocess.run(['powershell', '-Command', f'Invoke-WebRequest -Uri "{url}" -OutFile "cloudflared.exe"'], 
                      check=True)
        print("✅ Cloudflared скачан!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка скачивания cloudflared")
        return False

def main():
    """Основная функция"""
    print("=" * 50)
    print("🌐 Cloudflare Tunnel для Flask")
    print("=" * 50)
    print()
    
    # Проверяем cloudflared
    if not check_cloudflared():
        print("Хотите скачать cloudflared автоматически? (y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            if download_cloudflared():
                print("✅ Cloudflared готов к использованию!")
            else:
                print("❌ Не удалось скачать cloudflared")
                return
        else:
            print("Установите cloudflared вручную и запустите снова")
            return
    
    print()
    print("🎯 Настройки:")
    print("- Flask порт: 10000")
    print("- Cloudflare домен: [random].trycloudflare.com")
    print("- URL: https://[random].trycloudflare.com")
    print()
    
    # Запускаем Flask в отдельном потоке
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Ждем немного для запуска Flask
    print("⏳ Ждем запуска Flask на порту 10000...")
    time.sleep(5)
    
    print("✅ Flask запущен! Теперь запускаю Cloudflare Tunnel...")
    print()
    
    # Запускаем Cloudflare Tunnel
    run_cloudflare()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
        sys.exit(0) 