#!/usr/bin/env python3
"""
Скрипт для тестирования подключения через Tor
"""

import requests
import time
from pathlib import Path

def test_tor_connection():
    """Тестируем подключение через Tor"""
    print("🔍 Тестирование подключения через Tor...")
    
    # Получаем .onion адрес
    onion_address = None
    possible_files = [
        'harvestano_onion_address.txt',
        'harvestano_onion_service/hostname',
        'onion_address.txt'
    ]
    
    for file_path in possible_files:
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                address = f.read().strip()
                if address and '.onion' in address:
                    onion_address = address
                    break
    
    if not onion_address:
        print("❌ .onion адрес не найден")
        print("Запустите: python setup_harvestano_onion.py")
        return False
    
    print(f"📍 Тестируем адрес: {onion_address}")
    
    # Настраиваем прокси для Tor
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    
    try:
        print("⏳ Подключаемся через Tor...")
        start_time = time.time()
        
        response = requests.get(f'http://{onion_address}', 
                              proxies=proxies, 
                              timeout=60)
        
        end_time = time.time()
        connection_time = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ Подключение успешно!")
            print(f"⏱️ Время ответа: {connection_time:.2f} секунд")
            print(f"📄 Размер ответа: {len(response.content)} байт")
            
            # Проверяем, что это наш сайт
            if 'harvestano' in response.text.lower() or 'login' in response.text.lower():
                print("✅ Сайт работает корректно")
                return True
            else:
                print("⚠️ Получен ответ, но возможно не наш сайт")
                return True
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except requests.exceptions.ProxyError:
        print("❌ Ошибка прокси - Tor не запущен или недоступен")
        print("Запустите: python tor_setup.py")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения - проверьте Tor и сеть")
        return False
    except requests.exceptions.Timeout:
        print("❌ Таймаут - Tor сеть может быть медленной")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        return False

def test_external_tor():
    """Тестируем подключение к внешним .onion сайтам"""
    print("\n🌐 Тестирование внешних .onion сайтов...")
    
    # Список известных .onion сайтов для тестирования
    test_sites = [
        'http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion',  # DuckDuckGo
        'http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion'   # The Hidden Wiki
    ]
    
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    
    for site in test_sites:
        try:
            print(f"⏳ Тестируем: {site}")
            response = requests.get(site, proxies=proxies, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {site} - доступен")
            else:
                print(f"⚠️ {site} - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {site} - ошибка: {str(e)}")

def main():
    print("🌐 Тестирование Tor подключения")
    print("=" * 40)
    
    # Тестируем наш сайт
    success = test_tor_connection()
    
    if success:
        print("\n🎉 Tor подключение работает!")
        print("📱 Android приложение должно работать корректно")
    else:
        print("\n❌ Проблемы с Tor подключением")
        print("📋 Проверьте:")
        print("1. Tor запущен: python check_tor_status.py")
        print("2. .onion адрес настроен: python setup_harvestano_onion.py")
        print("3. Flask приложение запущено на порту 10000")
    
    # Тестируем внешние сайты
    test_external_tor()
    
    print("\n📋 Рекомендации:")
    if success:
        print("✅ Ваш Tor хостинг работает корректно")
        print("📱 Можете устанавливать Android приложение")
    else:
        print("🔧 Исправьте проблемы перед использованием")
        print("📖 См. TOR_SETUP_INSTRUCTIONS.md для подробностей")

if __name__ == "__main__":
    main() 