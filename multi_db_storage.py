import os
import hashlib

class MultiDBStorage:
    def __init__(self):
        # Несколько Supabase проектов
        self.databases = [
            os.environ.get('DATABASE_URL_1'),  # 500MB
            os.environ.get('DATABASE_URL_2'),  # 500MB  
            os.environ.get('DATABASE_URL_3'),  # 500MB
            # Итого: 1.5GB бесплатно
        ]
    
    def get_db_for_user(self, user_id):
        """Распределяем пользователей по базам"""
        db_index = int(hashlib.md5(str(user_id).encode()).hexdigest(), 16) % len(self.databases)
        return self.databases[db_index]
    
    def get_db_for_chat(self, chat_id):
        """Распределяем чаты по базам"""
        db_index = chat_id % len(self.databases)
        return self.databases[db_index]