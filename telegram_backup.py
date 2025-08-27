import requests
import sqlite3
import os
import zipfile
import shutil
from datetime import datetime

# Настройки Telegram бота (используем переменные окружения для Render)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7293066749:AAFg5fXAVZkPx6s7R3drwGEV5pjKZY1f-PM')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '564049757')

def send_telegram_file(file_path, caption=""):
    """Отправляет файл в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    with open(file_path, 'rb') as file:
        files = {'document': file}
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'caption': caption
        }
        
        response = requests.post(url, files=files, data=data)
        return response.json().get('ok', False)

def backup_database():
    """Создает бэкап базы данных"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Создаем папку для бэкапа
    backup_dir = f"backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    try:
        # Ищем базу данных в разных местах
        db_paths = ['harvest.db', '/tmp/harvest.db', 'instance/harvest.db']
        db_found = False
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                shutil.copy2(db_path, f"{backup_dir}/harvest.db")
                db_found = True
                break
        
        if not db_found:
            # Создаем пустую базу для структуры
            open(f"{backup_dir}/harvest_empty.db", 'w').close()
        
        # Копируем папку uploads если есть
        upload_paths = ['static/uploads', 'uploads']
        for upload_path in upload_paths:
            if os.path.exists(upload_path):
                shutil.copytree(upload_path, f"{backup_dir}/uploads", dirs_exist_ok=True)
                break
        
        # Создаем архив
        zip_name = f"harvest_backup_{timestamp}.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arcname)
        
        # Отправляем в Telegram
        db_status = "✅ База данных" if db_found else "⚠️ База не найдена"
        caption = f"🔄 Автобэкап Harvest Messenger\n📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n{db_status}"
        
        if send_telegram_file(zip_name, caption):
            print(f"✅ Бэкап отправлен: {zip_name}")
        else:
            print(f"❌ Ошибка отправки бэкапа")
        
        # Удаляем временные файлы
        os.remove(zip_name)
        shutil.rmtree(backup_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания бэкапа: {e}")
        return False

if __name__ == '__main__':
    backup_database()