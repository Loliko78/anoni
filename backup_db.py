import os
import shutil
import schedule
import time
from datetime import datetime

def backup_database():
    """Создает бэкап SQLite базы"""
    if os.path.exists('harvest.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_harvest_{timestamp}.db'
        shutil.copy2('harvest.db', backup_name)
        print(f"Backup created: {backup_name}")

def restore_database(backup_file):
    """Восстанавливает базу из бэкапа"""
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, 'harvest.db')
        print(f"Database restored from: {backup_file}")

# Автоматический бэкап каждые 6 часов
schedule.every(6).hours.do(backup_database)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Проверка каждый час