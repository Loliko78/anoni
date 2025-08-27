import requests
import json
import base64
import os

class GitHubStorage:
    def __init__(self, token, repo, branch='main'):
        self.token = token
        self.repo = repo  # username/repo-name
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{repo}/contents"
    
    def get_file(self, filename):
        """Получить файл из GitHub"""
        url = f"{self.base_url}/{filename}"
        headers = {'Authorization': f'token {self.token}'}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()['content']
            return json.loads(base64.b64decode(content).decode('utf-8'))
        return {}
    
    def save_file(self, filename, data):
        """Сохранить файл в GitHub"""
        url = f"{self.base_url}/{filename}"
        headers = {'Authorization': f'token {self.token}'}
        
        # Получаем SHA существующего файла
        existing = requests.get(url, headers=headers)
        sha = existing.json().get('sha') if existing.status_code == 200 else None
        
        content = base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        
        payload = {
            'message': f'Update {filename}',
            'content': content,
            'branch': self.branch
        }
        
        if sha:
            payload['sha'] = sha
        
        response = requests.put(url, json=payload, headers=headers)
        return response.status_code in [200, 201]

# Использование:
# storage = GitHubStorage('your_token', 'username/data-repo')
# data = storage.get_file('users.json')
# storage.save_file('users.json', updated_data)