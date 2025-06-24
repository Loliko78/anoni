#!/usr/bin/env python3
"""
Запуск Flask с Cloudflare Tunnel (cloudflared)
"""

import threading
import time
import subprocess
import re
import os
from app import app

def run_flask():
    """Запускает Flask приложение"""
    app.run(host='0.0.0.0', port=10000, debug=False)

def start_cloudflare_tunnel():
    """Запускает Cloudflare Tunnel"""
    cloudflared_path = "./cloudflared.exe"
    
    if not os.path.exists(cloudflared_path):
        print("❌ Cloudflared не найден. Запустите: python install_cloudflared.py")
        return None, None
    
    try:
        print("🌐 Запуск Cloudflare Tunnel...")
        process = subprocess.Popen(
            [cloudflared_path, 'tunnel', '--url', 'http://127.0.0.1:5000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Ловим ссылку из stdout
        url = None
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
            # Ищем ссылку вида https://random-name.trycloudflare.com
            match = re.search(r'https://[\w\-]+\.trycloudflare\.com', line)
            if match and not url:
                url = match.group(0)
                print(f"\n\033[92m🌍 Публичный доступ: {url}\033[0m\n")
                break
            # Также ищем ссылки вида https://random-name.tunnel.ngrok-free.app
            match = re.search(r'https://[\w\-]+\.tunnel\.ngrok-free\.app', line)
            if match and not url:
                url = match.group(0)
                print(f"\n\033[92m🌍 Публичный доступ: {url}\033[0m\n")
                break
        
        return url, process
        
    except Exception as e:
        print(f"❌ Ошибка запуска Cloudflare Tunnel: {e}")
        return None, None

if __name__ == '__main__':
    print("🚀 Запуск Flask с Cloudflare Tunnel...")
    print("=" * 50)
    
    # Запускаем Flask
    print("📱 Запуск Flask приложения...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Ждем запуска Flask
    time.sleep(3)
    
    # Запускаем Cloudflare Tunnel
    public_url, process = start_cloudflare_tunnel()
    
    if process:
        if public_url:
            print(f"\n✅ Cloudflare Tunnel: {public_url}")
            print(f"📱 Локальный доступ: http://127.0.0.1:5000")
            print("=" * 50)
            print("💡 Нажмите Ctrl+C для остановки")
            print("🔒 Без предупреждений и паролей!")
        else:
            print("⚠️ Туннель запущен, но ссылка не найдена")
            print("💡 Проверьте вывод выше для ссылки")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Остановка...")
            process.terminate()
            print("✅ Остановлено")
    else:
        print("❌ Не удалось запустить Cloudflare Tunnel")
        print("💡 Попробуйте локальный доступ: python run_local.py") 