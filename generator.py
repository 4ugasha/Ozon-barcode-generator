# generator.py
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
import re
import logging
from presets import LABEL_PRESETS

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[^\w\s\-\.]', '', name, flags=re.UNICODE)
    name = name.replace(' ', '_')
    name = re.sub(r'_+', '_', name)
    return name[:50].strip('_') or "label"

def generate_ozon_label(code_data, product_name, preset_key, **overrides):
    logger.info(f"Начало генерации для {code_data} (пресет: {preset_key})")
    
    if preset_key not in LABEL_PRESETS:
        raise ValueError(f"Неизвестный пресет '{preset_key}'")
    
    config = LABEL_PRESETS[preset_key].copy()
    for key, value in overrides.items():
        if value is not None and key in config:
            config[key] = value
            
    w = config['label_width_mm']
    h = config['label_height_mm']
    mt = config['margin_top_mm']
    mb = config['margin_bottom_mm']
    ml = config['margin_left_mm']
    mr = config['margin_right_mm']
    bh = config['barcode_height_mm']
    fsc = config['font_size_code']
    fsd = config['font_size_desc']
    mw = config['module_width']

    clean_code = code_data.upper().strip()
    if not all(32 <= ord(c) <= 126 for c in clean_code):
        raise ValueError("Code 128 поддерживает только печатные ASCII символы")

    writer = ImageWriter()
    options = {
        'module_width': mw,      
        'module_height': bh, 
        'quiet_zone': 0,        
        'write_text': False
    }

    try:
        code_class = barcode.get_barcode_class('code128')
        ozon_code = code_class(clean_code, writer=writer)
        
        img_buffer = io.BytesIO()
        ozon_code.write(img_buffer, options=options)
        img_buffer.seek(0)
        barcode_img = Image.open(img_buffer)
        
        # Обрезка нижнего отступа (твоя фишка)
        w_px, h_px = barcode_img.size
        crop_pixels = int(h_px * 0.07)
        if crop_pixels > 0:
            barcode_img = barcode_img.crop((0, 0, w_px, h_px - crop_pixels))
            
    except Exception as e:
        logger.error(f"Ошибка генерации штрихкода: {e}")
        return None

    mm_to_pt = 2.83465
    page_width = w * mm_to_pt
    page_height = h * mm_to_pt
    
    safe_name = sanitize_filename(product_name)
    output_filename = os.path.join(OUTPUT_DIR, f"{clean_code}_{safe_name}.pdf")
    
    c = canvas.Canvas(output_filename, pagesize=(page_width, page_height))
    
    current_y_mm = h - mt
    left_x_mm = ml
    available_width_mm = w - ml - mr
    
    # Рисуем Штрихкод
    img_w_px, img_h_px = barcode_img.size
    aspect_ratio = img_w_px / img_h_px
    
    draw_height_mm = bh 
    draw_width_mm = draw_height_mm * aspect_ratio
    
    if draw_width_mm > available_width_mm:
        draw_width_mm = available_width_mm
        draw_height_mm = draw_width_mm / aspect_ratio
        
    draw_x_mm = left_x_mm + (available_width_mm - draw_width_mm) / 2
    
    draw_x_pt = draw_x_mm * mm_to_pt
    draw_y_pt = (current_y_mm - draw_height_mm) * mm_to_pt
    draw_w_pt = draw_width_mm * mm_to_pt
    draw_h_pt = draw_height_mm * mm_to_pt
    
    img_reader = ImageReader(img_buffer)
    c.drawImage(img_reader, draw_x_pt, draw_y_pt, width=draw_w_pt, height=draw_h_pt)
    
    # Отступ после штрихкода (твой параметр -1.2 для прижатия)
    gap_after_barcode = -1.2 if h <= 30 else 1.0
    current_y_mm = current_y_mm - draw_height_mm - gap_after_barcode
    
    # Текст кода
    c.setFont("Helvetica", fsc) 
    code_text_width_pt = c.stringWidth(clean_code, "Helvetica", fsc)
    code_x_pt = (page_width - code_text_width_pt) / 2
    
    text_y_pt = (current_y_mm - (fsc * 0.35)) * mm_to_pt
    c.drawString(code_x_pt, text_y_pt, clean_code)
    
    gap_after_code = 0.5 if h <= 30 else 1.5
    line_height_code_mm = (fsc * 0.35) + gap_after_code
    current_y_mm = current_y_mm - line_height_code_mm
    
    # Описание товара
    font_name = "Helvetica"
    local_arial = os.path.join(FONTS_DIR, "arial.ttf")
    sys_arial = r"C:\Windows\Fonts\arial.ttf"
    local_dejavu = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
    
    font_path_to_use = None
    registered_font_name = None
    
    if os.path.exists(local_arial):
        font_path_to_use = local_arial
        registered_font_name = 'Arial-Local'
    elif os.path.exists(sys_arial):
        font_path_to_use = sys_arial
        registered_font_name = 'Arial-Sys'
    elif os.path.exists(local_dejavu):
        font_path_to_use = local_dejavu
        registered_font_name = 'DejaVu-Local'
        
    if font_path_to_use and registered_font_name:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        if registered_font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(registered_font_name, font_path_to_use))
        font_name = registered_font_name

    c.setFont(font_name, fsd)
    
    words = product_name.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, font_name, fsd) < (available_width_mm * mm_to_pt):
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    line_height_desc_mm = fsd * (0.6 if h <= 30 else 0.45) 
    
    for line in lines:
        if current_y_mm < mb + (fsd * 0.35):
            break 
        desc_y_pt = (current_y_mm - (fsd * 0.35)) * mm_to_pt
        c.drawString(left_x_mm * mm_to_pt, desc_y_pt, line)
        current_y_mm = current_y_mm - line_height_desc_mm
        
    c.save()
    logger.info(f"Сохранено: {output_filename}")
    return output_filename