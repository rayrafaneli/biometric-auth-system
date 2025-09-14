import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QGuiApplication

from src.database.database_manager import DatabaseManager
from src.biometrics import matcher

from src.gui.login_window import LoginWindow 

DB_PATH = 'biometric_database.db'
db_manager = DatabaseManager(DB_PATH)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(BASE_DIR, 'src', 'images', 'icon.ico')
        app.setWindowIcon(QIcon(icon_path))

        window = LoginWindow(db_manager, matcher)
        window.setWindowIcon(QIcon(icon_path)) 
        window.resize(600, 400)
        window.show()

        qt_rectangle = window.frameGeometry()
        center_point = QGuiApplication.primaryScreen().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        window.move(qt_rectangle.topLeft())

        sys.exit(app.exec())
    finally:
        db_manager.close_connection()