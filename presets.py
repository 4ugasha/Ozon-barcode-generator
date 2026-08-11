# presets.py

LABEL_PRESETS = {
    "Компактная 43x25": {
        "label_width_mm": 43.0,
        "label_height_mm": 23.0,
        "margin_top_mm": 0.5,
        "margin_bottom_mm": 0.5,
        "margin_left_mm": 1.0,
        "margin_right_mm": 1.0,
        "barcode_height_mm": 15.0, 
        "font_size_code": 7,
        "font_size_desc": 3,
        "module_width": 0.3 
    },
    
    # Пример будущего пресета (раскомментируй и настрой когда понадобится):
    # "Стандартная 58x40": {
    #     "label_width_mm": 58.0,
    #     "label_height_mm": 40.0,
    #     "margin_top_mm": 2.0,
    #     "margin_bottom_mm": 2.0,
    #     "margin_left_mm": 2.0,
    #     "margin_right_mm": 2.0,
    #     "barcode_height_mm": 16.0, 
    #     "font_size_code": 11,
    #     "font_size_desc": 8,
    #     "module_width": 0.3
    # }
}