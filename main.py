import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
import os

URL = "https://anoni-1.onrender.com/"
ICON_PATH = "harvest_darkweb.ico"

class WebViewApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Harvest')
        self.setGeometry(100, 100, 420, 800)
        self.setMinimumSize(320, 480)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.webview = QWebEngineView(self)
        self.webview.setUrl(QUrl(URL))
        self.setCentralWidget(self.webview)
        # Обработка ошибок загрузки
        self.webview.loadFinished.connect(self.handle_load_finished)

    def handle_load_finished(self, ok):
        if not ok:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить сайт: {URL}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebViewApp()
    window.show()
    sys.exit(app.exec())