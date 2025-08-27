import requests

def setup_telegram_bot():
    """Помогает настроить Telegram бота для бэкапов"""
    
    print("🤖 Настройка Telegram бота для автобэкапов")
    print("=" * 50)
    
    print("\n1️⃣ Создание бота:")
    print("   • Напишите @BotFather в Telegram")
    print("   • Отправьте команду: /newbot")
    print("   • Придумайте имя бота (например: Harvest Backup Bot)")
    print("   • Придумайте username (например: harvest_backup_bot)")
    print("   • Скопируйте токен бота")
    
    bot_token = input("\n🔑 Введите токен бота: ").strip()
    
    print("\n2️⃣ Получение Chat ID:")
    print("   • Напишите вашему боту любое сообщение")
    print("   • Нажмите Enter для получения Chat ID...")
    input()
    
    # Получаем обновления от бота
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data['ok'] and data['result']:
            chat_id = data['result'][-1]['message']['chat']['id']
            print(f"✅ Ваш Chat ID: {chat_id}")
            
            # Обновляем файл telegram_backup.py
            with open('telegram_backup.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            content = content.replace('YOUR_BOT_TOKEN', bot_token)
            content = content.replace('YOUR_CHAT_ID', str(chat_id))
            
            with open('telegram_backup.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Настройки сохранены в telegram_backup.py")
            
            # Тестовая отправка
            print("\n3️⃣ Тестирование...")
            from telegram_backup import backup_database
            if backup_database():
                print("🎉 Бэкап система настроена успешно!")
            else:
                print("❌ Ошибка при тестировании")
                
        else:
            print("❌ Не найдены сообщения. Напишите боту и попробуйте снова.")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    setup_telegram_bot()