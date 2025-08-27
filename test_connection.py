import psycopg2
import sys

def test_local_connection():
    """Тестирует локальное подключение к PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="harvest_db",
            user="harvest_user",
            password="harvest123"
        )
        print("✅ Локальное подключение успешно")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка локального подключения: {e}")
        return False

def test_ngrok_connection(ngrok_url):
    """Тестирует подключение через ngrok"""
    try:
        # Парсим URL вида tcp://0.tcp.ngrok.io:12345
        if ngrok_url.startswith('tcp://'):
            url_part = ngrok_url.replace('tcp://', '')
            host, port = url_part.split(':')
        else:
            host, port = ngrok_url.split(':')
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database="harvest_db", 
            user="harvest_user",
            password="harvest123"
        )
        print("✅ Подключение через ngrok успешно")
        print(f"🔗 URL для Render: postgresql://harvest_user:harvest123@{host}:{port}/harvest_db")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения через ngrok: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Тестирование подключений к PostgreSQL\n")
    
    # Тест локального подключения
    print("1. Тестирование локального подключения...")
    test_local_connection()
    
    # Тест ngrok подключения
    print("\n2. Тестирование подключения через ngrok...")
    if len(sys.argv) > 1:
        ngrok_url = sys.argv[1]
        test_ngrok_connection(ngrok_url)
    else:
        print("💡 Для теста ngrok запустите: python test_connection.py tcp://0.tcp.ngrok.io:12345")
        print("   (замените на ваш реальный ngrok URL)")