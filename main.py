# main.py
import sys
import os
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ozon Label Generator - Main Menu")
        self.setFixedSize(400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("Выберите режим работы")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        btn_manual = QPushButton("Ручной ввод (Single)")
        btn_manual.setMinimumHeight(50)
        btn_manual.clicked.connect(self.open_manual)
        layout.addWidget(btn_manual)
        
        btn_excel = QPushButton("Генерация из Excel (Batch)")
        btn_excel.setMinimumHeight(50)
        btn_excel.clicked.connect(self.open_excel)
        layout.addWidget(btn_excel)
        
    def open_manual(self):
        logger.info("Запуск режима ручного ввода")
        from gui_manual import ManualGeneratorWindow
        self.window = ManualGeneratorWindow()
        self.window.show()
        self.close()
        
    def open_excel(self):
        logger.info("Запуск режима генерации из Excel")
        from gui_excel import ExcelGeneratorWindow
        self.window = ExcelGeneratorWindow()
        self.window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainMenu()
    window.show()
    sys.exit(app.exec())