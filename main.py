import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import io
import os
import re

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Создаем папку output, если её нет
os.makedirs(OUTPUT_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """
    Очищает строку для использования в имени файла.
    Убирает спецсимволы, заменяет пробелы на подчеркивания, ограничивает длину.
    """
    # Оставляем только буквы (любые), цифры, пробелы, дефисы и точки
    name = re.sub(r'[^\w\s\-\.]', '', name, flags=re.UNICODE)
    # Заменяем пробелы на подчеркивания
    name = name.replace(' ', '_')
    # Убираем множественные подчеркивания
    name = re.sub(r'_+', '_', name)
    # Ограничиваем длину до 50 символов, чтобы имя файла не было слишком длинным
    return name[:50].strip('_') or "label"

def generate_ozon_label(
    code_data: str,
    product_name: str,
    label_width_mm: float = 58.0,   
    label_height_mm: float = 40.0,  
    margin_top_mm: float = 2.0,     
    margin_bottom_mm: float = 2.0,  
    margin_left_mm: float = 2.0,    
    margin_right_mm: float = 2.0,   
    barcode_height_mm: float = 14.0,
    font_size_code: int = 11,       
    font_size_desc: int = 8         
):
    clean_code = code_data.upper().strip()
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-. $/+%")
    
    invalid_chars = [c for c in clean_code if c not in allowed_chars]
    if invalid_chars:
        raise ValueError(f"Недопустимые символы для Code 39: {set(invalid_chars)}")

    print(f"Генерация Code 39 для: {clean_code}")

    writer = ImageWriter()
    options = {
        'module_width': 0.3,      
        'module_height': barcode_height_mm, 
        'quiet_zone': 0,        
        'write_text': False
    }

    try:
        code_class = barcode.get_barcode_class('code39')
        ozon_code = code_class(clean_code, writer=writer, add_checksum=False)
        
        img_buffer = io.BytesIO()
        ozon_code.write(img_buffer, options=options)
        img_buffer.seek(0)
        barcode_img = Image.open(img_buffer)
        
    except Exception as e:
        print(f"Ошибка генерации штрихкода: {e}")
        return None

    mm_to_pt = 2.83465
    page_width = label_width_mm * mm_to_pt
    page_height = label_height_mm * mm_to_pt
    
    # --- ФОРМИРОВАНИЕ ИМЕНИ ФАЙЛА ---
    safe_name = sanitize_filename(product_name)
    # Добавляем код в начало имени для уникальности, если описания похожи
    output_filename = os.path.join(OUTPUT_DIR, f"{clean_code}_{safe_name}.pdf")
    
    c = canvas.Canvas(output_filename, pagesize=(page_width, page_height))
    
    current_y_mm = label_height_mm - margin_top_mm
    left_x_mm = margin_left_mm
    available_width_mm = label_width_mm - margin_left_mm - margin_right_mm
    
    # --- Рисуем Штрихкод ---
    img_w_px, img_h_px = barcode_img.size
    aspect_ratio = img_w_px / img_h_px
    
    draw_width_mm = available_width_mm
    draw_height_mm = draw_width_mm / aspect_ratio
    
    if draw_height_mm > barcode_height_mm:
        draw_height_mm = barcode_height_mm
        draw_width_mm = draw_height_mm * aspect_ratio
        
    draw_x_mm = left_x_mm + (available_width_mm - draw_width_mm) / 2
    
    draw_x_pt = draw_x_mm * mm_to_pt
    draw_y_pt = (current_y_mm - draw_height_mm) * mm_to_pt
    draw_w_pt = draw_width_mm * mm_to_pt
    draw_h_pt = draw_height_mm * mm_to_pt
    
    img_reader = ImageReader(img_buffer)
    c.drawImage(img_reader, draw_x_pt, draw_y_pt, width=draw_w_pt, height=draw_h_pt)
    
    current_y_mm = current_y_mm - draw_height_mm - 1.0
    
    # --- Рисуем Текст (Код OZN...) ПО ЦЕНТРУ ---
    c.setFont("Helvetica-Bold", font_size_code) 
    code_text_width_pt = c.stringWidth(clean_code, "Helvetica-Bold", font_size_code)
    code_x_pt = (page_width - code_text_width_pt) / 2
    
    text_y_pt = (current_y_mm - (font_size_code * 0.35)) * mm_to_pt
    c.drawString(code_x_pt, text_y_pt, clean_code)
    
    line_height_code_mm = (font_size_code * 0.35) + 1.5
    current_y_mm = current_y_mm - line_height_code_mm
    
    # --- Рисуем Описание товара (Кириллица) ---
    # Ищем шрифт сначала в папке fonts/, потом в системе
    font_name = "Helvetica"
    
    # Приоритет 1: Arial в папке fonts (универсально)
    local_arial = os.path.join(FONTS_DIR, "arial.ttf")
    # Приоритет 2: Arial в системе Windows
    sys_arial = r"C:\Windows\Fonts\arial.ttf"
    # Приоритет 3: DejaVu в папке fonts
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
        print(f"✅ Используется шрифт: {os.path.basename(font_path_to_use)}")
    else:
        print("⚠️ ВНИМАНИЕ: Шрифты с кириллицей не найдены ни в /fonts, ни в системе!")

    c.setFont(font_name, font_size_desc)
    
    words = product_name.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, font_name, font_size_desc) < (available_width_mm * mm_to_pt):
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    line_height_desc_mm = font_size_desc * 0.45 
    
    for line in lines:
        if current_y_mm < margin_bottom_mm:
            break 
        desc_y_pt = (current_y_mm - (font_size_desc * 0.35)) * mm_to_pt
        c.drawString(left_x_mm * mm_to_pt, desc_y_pt, line)
        current_y_mm = current_y_mm - line_height_desc_mm
        
    c.save()
    print(f" Этикетка сохранена: {output_filename}")
    return output_filename

if __name__ == "__main__":
    my_code = "OZN1777835488"
    # Специально добавил спецсимволы для проверки очистки имени файла
    my_description = "Ручка для бутылок 5 литров, бутылей 5л (3 шт.), под узкое горлышко 37 мм / NEW!"
    
    try:
        generate_ozon_label(
            code_data=my_code,
            product_name=my_description,
            label_width_mm=58.0,      
            label_height_mm=40.0,     
            margin_top_mm=2.0,
            margin_bottom_mm=2.0,
            margin_left_mm=2.0,
            margin_right_mm=2.0,
            barcode_height_mm=14.0,   
            font_size_code=11,        
            font_size_desc=8          
        )
    except ValueError as e:
        print(e)