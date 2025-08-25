#!/usr/bin/env python3
"""
Скрипт для обновления зависимостей для совместимости с Python 3.13
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return success status"""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🔄 Обновление зависимостей для Python 3.13...")
    
    # Update specific packages that have Python 3.13 compatibility issues
    packages = [
        "eventlet==0.35.2",
        "Flask-SocketIO==5.3.7", 
        "python-socketio==5.13.0",
        "python-engineio==4.12.2"
    ]
    
    for package in packages:
        print(f"📦 Установка {package}...")
        if not run_command(f"pip install --upgrade {package}"):
            print(f"❌ Ошибка установки {package}")
            return False
    
    print("✅ Зависимости обновлены!")
    return True

if __name__ == "__main__":
    if main():
        print("🎉 Готово! Теперь можно запускать app.py")
    else:
        print("❌ Ошибка обновления зависимостей")
        sys.exit(1) 