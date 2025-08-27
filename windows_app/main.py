import webview
import sys
import os

def main():
    # URL вашего сайта
    url = "https://anoni-1.onrender.com/"
    
    # Создаем окно приложения
    webview.create_window(
        title="Harvest Messenger",
        url=url,
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True,
        fullscreen=False,
        minimized=False,
        on_top=False,
        shadow=True,
        focus=True,
        text_select=False
    )
    
    # Запускаем приложение
    webview.start(debug=False)

if __name__ == "__main__":
    main()