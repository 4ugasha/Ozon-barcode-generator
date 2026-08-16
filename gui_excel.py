# gui_excel.py
import sys
import os
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QPushButton, 
                               QGroupBox, QFileDialog, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt
from generator import generate_ozon_label
from presets import LABEL_PRESETS

# Проверка наличия openpyxl для работы с Excel
try:
    import openpyxl
except ImportError:
    logging.error("Библиотека openpyxl не найдена. Установите: pip install openpyxl")

logger = logging.getLogger(__name__)

class ExcelGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пакетная генерация из Excel")
        self.setMinimumSize(600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        settings_group = QGroupBox("Настройки")
        settings_layout = QVBoxLayout(settings_group)
        
        self.preset_combo = QComboBox()
        for key, val in LABEL_PRESETS.items():
            self.preset_combo.addItem(val['name'], key)
        settings_layout.addWidget(QLabel("Размер этикетки:"))
        settings_layout.addWidget(self.preset_combo)
        
        main_layout.addWidget(settings_group)
        
        file_group = QGroupBox("Файл Excel")
        file_layout = QVBoxLayout(file_group)
        
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("color: gray; font-style: italic;")
        file_layout.addWidget(self.file_label)
        
        select_btn = QPushButton("Выбрать файл Excel (.xlsx)")
        select_btn.clicked.connect(self.select_file)
        file_layout.addWidget(select_btn)
        
        main_layout.addWidget(file_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.generate_btn = QPushButton("Начать генерацию")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.generate_btn.clicked.connect(self.start_generation)
        main_layout.addWidget(self.generate_btn)
        
        self.selected_file = None

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите Excel файл", "", "Excel Files (*.xlsx)")
        if path:
            self.selected_file = path
            self.file_label.setText(os.path.basename(path))
            self.file_label.setStyleSheet("color: black; font-weight: bold;")
            self.generate_btn.setEnabled(True)

    def start_generation(self):
        if not self.selected_file:
            return
            
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            wb = openpyxl.load_workbook(self.selected_file)
            ws = wb.active
            
            # Пропускаем заголовок (1 строка), начинаем со 2-й
            rows = list(ws.iter_rows(min_row=2, values_only=True))
            total = len(rows)
            
            if total == 0:
                QMessageBox.warning(self, "Внимание", "Файл пуст или нет данных после заголовка!")
                self.reset_ui()
                return
                
            success_count = 0
            error_count = 0
            
            for i, row in enumerate(rows):
                # A = Артикул (индекс 0), B = Описание (индекс 1)
                code = row[0]
                desc = row[1]
                
                if code and desc:
                    try:
                        preset_key = self.preset_combo.currentData()
                        generate_ozon_label(
                            code_data=str(code),
                            product_name=str(desc),
                            preset_key=preset_key
                        )
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка в строке {i+2}: {e}")
                        error_count += 1
                
                self.progress_bar.setValue(int((i + 1) / total * 100))
                
            msg = f"Готово!\nУспешно: {success_count}\nОшибок: {error_count}"
            QMessageBox.information(self, "Результат", msg)
            
        except Exception as e:
            logger.error(f"Критическая ошибка Excel: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.reset_ui()

    def reset_ui(self):
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)