import json
import os
from datetime import datetime

class JSONStorage:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.data = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'users': {},
            'chats': {},
            'messages': {},
            'groups': {},
            'channels': {}
        }
    
    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_data):
        user_id = len(self.data['users']) + 1
        self.data['users'][user_id] = user_data
        self.save_data()
        return user_id
    
    def get_user(self, user_id):
        return self.data['users'].get(str(user_id))
    
    def add_message(self, chat_id, sender_id, content):
        msg_id = len(self.data['messages']) + 1
        self.data['messages'][msg_id] = {
            'chat_id': chat_id,
            'sender_id': sender_id,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.save_data()
        return msg_id