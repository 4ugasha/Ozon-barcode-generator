# gui.py
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                               QComboBox, QPushButton, QGroupBox, QFormLayout, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from generator import generate_ozon_label
from presets import LABEL_PRESETS

class OzonLabelGeneratorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ozon Barcode Generator")
        self.setMinimumSize(500, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Группа: Основные настройки ---
        settings_group = QGroupBox("Настройки этикетки")
        settings_layout = QFormLayout(settings_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(LABEL_PRESETS.keys())
        settings_layout.addRow("Пресет размера:", self.preset_combo)
        
        # Поля для ручной корректировки (опционально)
        self.font_desc_input = QLineEdit()
        self.font_desc_input.setPlaceholderText("Например: 4 (оставьте пустым для значения из пресета)")
        settings_layout.addRow("Размер шрифта описания:", self.font_desc_input)
        
        main_layout.addWidget(settings_group)
        
        # --- Группа: Данные товара ---
        data_group = QGroupBox("Данные для печати")
        data_layout = QVBoxLayout(data_group)
        
        data_layout.addWidget(QLabel("Артикул / Штрихкод (OZN...):"))
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Введите код, например: OZN1777835488")
        self.code_input.setFont(QFont("Consolas", 12))
        data_layout.addWidget(self.code_input)
        
        data_layout.addWidget(QLabel("Описание товара:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Введите название товара...")
        self.desc_input.setMaximumHeight(100)
        data_layout.addWidget(self.desc_input)
        
        main_layout.addWidget(data_group)
        
        # --- Кнопка генерации ---
        self.generate_btn = QPushButton("️ Сгенерировать этикетку")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #005bff;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0046cc;
            }
            QPushButton:pressed {
                background-color: #003399;
            }
        """)
        self.generate_btn.clicked.connect(self.on_generate)
        main_layout.addWidget(self.generate_btn)
        
        # Статус бар
        self.statusBar().showMessage("Готов к работе")

    def on_generate(self):
        code = self.code_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        preset = self.preset_combo.currentText()
        
        if not code:
            QMessageBox.warning(self, "Ошибка", "Введите артикул или штрихкод!")
            return
        if not desc:
            QMessageBox.warning(self, "Ошибка", "Введите описание товара!")
            return
            
        # Собираем переопределения
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
                preset_name=preset,
                **overrides
            )
            
            if result:
                self.statusBar().showMessage(f"Успешно создано: {os.path.basename(result)}", 5000)
                QMessageBox.information(self, "Успех", f"Этикетка сохранена в папку output!\n\n{os.path.basename(result)}")
            else:
                self.statusBar().showMessage("Ошибка генерации", 5000)
                
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Неизвестная ошибка", str(e))
            self.statusBar().showMessage("Произошла ошибка", 5000)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка современного стиля ( Fusion работает везде одинаково хорошо)
    app.setStyle("Fusion")
    
    window = OzonLabelGeneratorGUI()
    window.show()
    sys.exit(app.exec())