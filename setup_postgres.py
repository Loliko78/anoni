import psycopg2
import os

def setup_database():
    """Создает базу данных и таблицы для PostgreSQL"""
    
    # Подключение к PostgreSQL
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/harvest_db')
    
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Подключение к PostgreSQL успешно")
        
        # Проверяем таблицы
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cur.fetchall()
        
        print(f"📊 Найдено таблиц: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == '__main__':
    setup_database()