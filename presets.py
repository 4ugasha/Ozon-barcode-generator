# presets.py
import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")

def load_presets():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding='utf-8')
    
    presets = {}
    
    for section in config.sections():
        try:
            presets[section] = {
                'name': config.get(section, 'name'),
                'label_width_mm': config.getfloat(section, 'label_width_mm'),
                'label_height_mm': config.getfloat(section, 'label_height_mm'),
                'margin_top_mm': config.getfloat(section, 'margin_top_mm'),
                'margin_bottom_mm': config.getfloat(section, 'margin_bottom_mm'),
                'margin_left_mm': config.getfloat(section, 'margin_left_mm'),
                'margin_right_mm': config.getfloat(section, 'margin_right_mm'),
                'barcode_height_mm': config.getfloat(section, 'barcode_height_mm'),
                'font_size_code': config.getint(section, 'font_size_code'),
                'font_size_desc': config.getint(section, 'font_size_desc'),
                'module_width': config.getfloat(section, 'module_width'),
            }
        except Exception as e:
            print(f"Ошибка чтения пресета {section}: {e}")
            
    return presets

# Загружаем пресеты при импорте
LABEL_PRESETS = load_presets()