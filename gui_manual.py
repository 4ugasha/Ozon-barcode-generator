# gui_manual.py
import sys
import os
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                               QComboBox, QPushButton, QGroupBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from generator import generate_ozon_label
from presets import LABEL_PRESETS

logger = logging.getLogger(__name__)

class ManualGeneratorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ручная генерация этикеток")
        self.setMinimumSize(500, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        settings_group = QGroupBox("Настройки")
        settings_layout = QFormLayout(settings_group)
        
        self.preset_combo = QComboBox()
        # Заполняем комбобокс ключами из конфига, но отображаем human-readable name
        for key, val in LABEL_PRESETS.items():
            self.preset_combo.addItem(val['name'], key)
            
        settings_layout.addRow("Размер этикетки:", self.preset_combo)
        
        self.font_desc_input = QLineEdit()
        self.font_desc_input.setPlaceholderText("Оставьте пустым для значения по умолчанию")
        settings_layout.addRow("Размер шрифта описания:", self.font_desc_input)
        
        main_layout.addWidget(settings_group)
        
        data_group = QGroupBox("Данные товара")
        data_layout = QVBoxLayout(data_group)
        
        data_layout.addWidget(QLabel("Артикул / Штрихкод:"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Например: OZN1777835488")
        self.code_input.setFont(QFont("Consolas", 12))
        data_layout.addWidget(self.code_input)
        
        data_layout.addWidget(QLabel("Описание товара:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Введите название товара...")
        self.desc_input.setMaximumHeight(100)
        data_layout.addWidget(self.desc_input)
        
        main_layout.addWidget(data_group)
        
        self.generate_btn = QPushButton("Сгенерировать PDF")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #005bff;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #0046cc; }
        """)
        self.generate_btn.clicked.connect(self.on_generate)
        main_layout.addWidget(self.generate_btn)
        
        self.statusBar().showMessage("Готов к работе")

    def on_generate(self):
        code = self.code_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        
        # Получаем ключ пресета (второй аргумент itemData)
        preset_key = self.preset_combo.currentData()
        
        if not code or not desc:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
            
        overrides = {}
        font_desc_val = self.font_desc_input.text().strip()
        if font_desc_val:
            try:
                overrides['font_size_desc'] = int(font_desc_val)
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Размер шрифта должен быть числом!")
                return

        try:
            self.statusBar().showMessage("Генерация...")
            result = generate_ozon_label(
                code_data=code,
                product_name=desc,
                preset_key=preset_key,
                **overrides
            )
            
            if result:
                self.statusBar().showMessage(f"Успешно: {os.path.basename(result)}", 5000)
                QMessageBox.information(self, "Успех", f"Файл сохранен в output/\n\n{os.path.basename(result)}")
            else:
                self.statusBar().showMessage("Ошибка генерации", 5000)
                
        except Exception as e:
            logger.error(f"Ошибка в GUI: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))