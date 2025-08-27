import PyInstaller.__main__
import os

# Создаем исполняемый файл
PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name=HarvestMessenger',
    '--icon=icon.ico',
    '--add-data=icon.ico;.',
    '--hidden-import=webview',
    '--hidden-import=pythonnet',
    '--clean'
])