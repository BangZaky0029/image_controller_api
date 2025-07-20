import sys
import os
sys.path.append(os.path.abspath('D:/image_processing_api/src'))
import io
import re
import torch
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from flask import Blueprint, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

# Modular imports

from font_controllers.font_color import COLOR_OPTIONS 
from font_controllers.font_style import get_font, get_emoji_font 
from font_controllers.font_position import calculate_text_position

# Load YOLOv5 model (once)
model = None
def load_model():
    global model
    if model is None:
        try:
            model = torch.hub.load("ultralytics/yolov5", "custom", path="D:/YOLO/yolov5/runs/train/training_06/weights/best.pt", force_reload=False)
            print("[MODEL] YOLOv5 berhasil dimuat.")
        except Exception as e:
            print(f"[ERROR] Gagal load model: {e}")
            model = None
    return model

# Penamaan file
prefix = "Sample_"
ext = ".jpg"


def get_text_size(text, main_font, fallback_font):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    total_width = 0
    max_height = 0
    for char in bidi_text:
        if main_font.getmask(char).getbbox() is not None:
            bbox = main_font.getbbox(char)
            font = main_font
        else:
            bbox = fallback_font.getbbox(char)
            font = fallback_font
        total_width += bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if height > max_height:
            max_height = height
    return total_width, max_height

def draw_text_with_fallback(draw, x, y, text, main_font, fallback_font, fill):
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    current_x = x
    for char in bidi_text:
        if main_font.getmask(char).getbbox() is not None:
            font = main_font
        else:
            font = fallback_font
        draw.text((current_x, y), char, font=font, fill=fill)
        current_x += font.getbbox(char)[2] - font.getbbox(char)[0]


def process_image_file(image_path, id_print, product_note, type_product, qty, nama, font_color="#000000", is_preview=False):
    try:
        print(f"Proses image: {image_path}, nama: {nama}")

        font_color_rgb = hex_to_rgb(font_color)
        image_pil = Image.open(image_path)
        icc_profile = image_pil.info.get('icc_profile')
        dpi = image_pil.info.get('dpi', (300, 300))
        draw = ImageDraw.Draw(image_pil)

        # ✂️ Ambil product & category dari path
        path_parts = os.path.normpath(image_path).split(os.sep)
        product = path_parts[-3] if len(path_parts) >= 3 else "UnknownProduct"
        category = path_parts[-2] if len(path_parts) >= 2 else "UnknownCategory"

        # 📝 Format header
        header_text = f"{id_print} ({product}-{category}, {type_product}), {qty} PCS, {product_note}"

        # Header
        header_font = get_font(size=60)
        header_emoji_font = get_emoji_font(size=60)
        header_width, header_height = get_text_size(header_text, header_font, header_emoji_font)
        header_x = (image_pil.width - header_width) // 2
        draw_text_with_fallback(draw, header_x, 10, header_text, header_font, header_emoji_font, (255, 0, 0))

        # Detection
        detection_model = load_model()
        if detection_model:
            img_rgb = np.array(image_pil.convert("RGB"))
            results = detection_model(img_rgb)
            detections = results.pandas().xyxy[0]
            print(detections[['name', 'confidence']])  # tambahkan ini

            font_main = get_font(size=min(260, image_pil.width // 5))
            emoji_font = get_emoji_font(size=min(260, image_pil.width // 5))
            text_width, text_height = get_text_size(nama, font_main, emoji_font)
            for _, row in detections.iterrows():
                if row['name'] == 'list_nama':
                    xmin, ymin, xmax, ymax = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
                    text_bbox = font_main.getbbox(nama)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_x, text_y = calculate_text_position((xmin, ymin, xmax, ymax), (text_width, text_height))
                    draw_text_with_fallback(draw, text_x, text_y, nama, font_main, emoji_font, font_color_rgb)
                    break
        else:
            font_main = get_font(size=100)
            emoji_font = get_emoji_font(size=100)
            text_width, text_height = get_text_size(nama, font_main, emoji_font)
            text_x = (image_pil.width - text_width) // 2
            text_y = (image_pil.height - text_height) // 2
            draw_text_with_fallback(draw, text_x, text_y, nama, font_main, emoji_font, font_color_rgb)

        # 🧾 Ambil nama file asli
        image_filename = os.path.splitext(os.path.basename(image_path))[0]  # HM0001
        output_filename = f"{id_print}_{image_filename}.jpg"

        if is_preview:
            return None, output_filename, image_pil, dpi, icc_profile
        else:
            # 📂 Direktori simpan
            now = datetime.now()
            month = now.strftime('%B').upper()
            day = now.strftime('%d')
            base_dir = r"D:/assets/PRINT"

            # ✂️ Ambil nama product dari path image
            path_parts = os.path.normpath(image_path).split(os.sep)
            product = path_parts[-3] if len(path_parts) >= 3 else "UnknownProduct"

            # 📁 Gabung jadi folder lengkap: /PRINT/JULY/08/MARSOTO
            target_dir = os.path.join(base_dir, month, day, product)
            os.makedirs(target_dir, exist_ok=True)

            output_path = os.path.join(target_dir, output_filename)

            # 💾 Simpan
            image_pil.save(output_path, format='JPEG', quality=95, dpi=dpi, icc_profile=icc_profile)
            print(f"[✅] Gambar disimpan ke: {output_path}")

            return output_path, output_filename, None, None, None


    except Exception as e:
        print(f"[ERROR] Gagal proses image: {str(e)}")
        return None, None, None, None, None


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

