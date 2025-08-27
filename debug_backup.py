import os
import sqlite3

def check_database_status():
    """Проверяет статус базы данных"""
    print("🔍 Проверка базы данных...")
    
    # Возможные пути к базе данных
    db_paths = [
        'harvest.db',
        '/tmp/harvest.db', 
        'instance/harvest.db',
        '../harvest.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ Найдена база: {db_path}")
            
            # Проверяем размер
            size = os.path.getsize(db_path)
            print(f"📊 Размер: {size} байт")
            
            # Проверяем таблицы
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"📋 Таблиц: {len(tables)}")
                
                # Проверяем количество пользователей
                cursor.execute("SELECT COUNT(*) FROM user;")
                users = cursor.fetchone()[0]
                print(f"👥 Пользователей: {users}")
                
                # Проверяем количество сообщений
                cursor.execute("SELECT COUNT(*) FROM message;")
                messages = cursor.fetchone()[0]
                print(f"💬 Сообщений: {messages}")
                
                conn.close()
                return True
                
            except Exception as e:
                print(f"❌ Ошибка чтения БД: {e}")
        else:
            print(f"❌ Не найдена: {db_path}")
    
    print("\n📁 Содержимое текущей папки:")
    for item in os.listdir('.'):
        if os.path.isfile(item):
            size = os.path.getsize(item)
            print(f"  📄 {item} ({size} байт)")
        else:
            print(f"  📁 {item}/")
    
    return False

if __name__ == '__main__':
    check_database_status()