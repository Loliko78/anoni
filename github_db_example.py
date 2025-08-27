import requests
import json
import base64
from datetime import datetime

class GitHubDB:
    def __init__(self, token, repo):
        self.token = token
        self.repo = repo  # "username/repo-name"
        self.headers = {'Authorization': f'token {token}'}
        self.base_url = f"https://api.github.com/repos/{repo}/contents"
    
    def save_users(self, users_data):
        """Сохранить пользователей в users.json"""
        return self._save_file('users.json', users_data)
    
    def load_users(self):
        """Загрузить пользователей из users.json"""
        return self._load_file('users.json')
    
    def save_messages(self, messages_data):
        """Сохранить сообщения в messages.json"""
        return self._save_file('messages.json', messages_data)
    
    def _save_file(self, filename, data):
        url = f"{self.base_url}/{filename}"
        
        # Получаем SHA существующего файла
        existing = requests.get(url, headers=self.headers)
        sha = existing.json().get('sha') if existing.status_code == 200 else None
        
        # Кодируем данные в base64
        content = base64.b64encode(
            json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        ).decode('utf-8')
        
        payload = {
            'message': f'Update {filename} - {datetime.now().isoformat()}',
            'content': content
        }
        
        if sha:
            payload['sha'] = sha
        
        response = requests.put(url, json=payload, headers=self.headers)
        return response.status_code in [200, 201]
    
    def _load_file(self, filename):
        url = f"{self.base_url}/{filename}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            content = response.json()['content']
            return json.loads(base64.b64decode(content).decode('utf-8'))
        return {}

# Пример использования:
# github_db = GitHubDB('your_token', 'username/harvest-data')
# 
# # Сохранение
# users = {'1': {'name': 'user1', 'messages': []}}
# github_db.save_users(users)
# 
# # Загрузка
# users = github_db.load_users()