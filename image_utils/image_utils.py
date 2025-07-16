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

# Modular imports

from font_controllers.font_color import COLOR_OPTIONS 
from font_controllers.font_style import get_font 
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


def process_image_file(image_path, id_print, product_note, type_product, qty, nama, font_color_name="black", is_preview=False):
    try:
        print(f"Proses image: {image_path}, nama: {nama}")

        font_color = COLOR_OPTIONS.get(font_color_name, (0, 0, 0))
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
        header_bbox = draw.textbbox((0, 0), header_text, font=header_font)
        header_x = (image_pil.width - (header_bbox[2] - header_bbox[0])) // 2
        draw.text((header_x, 10), header_text, font=header_font, fill=(255, 0, 0))

        # Detection
        detection_model = load_model()
        if detection_model:
            img_rgb = np.array(image_pil.convert("RGB"))
            results = detection_model(img_rgb)
            detections = results.pandas().xyxy[0]
            print(detections[['name', 'confidence']])  # tambahkan ini

            font_main = get_font(size=min(260, image_pil.width // 5))
            for _, row in detections.iterrows():
                if row['name'] == 'list_nama':
                    xmin, ymin, xmax, ymax = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
                    text_bbox = font_main.getbbox(nama)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    text_x, text_y = calculate_text_position((xmin, ymin, xmax, ymax), (text_width, text_height))
                    draw.text((text_x, text_y), nama, font=font_main, fill=font_color)
                    break
        else:
            font_main = get_font(size=100)
            text_bbox = font_main.getbbox(nama)
            text_x = (image_pil.width - (text_bbox[2] - text_bbox[0])) // 2
            text_y = (image_pil.height - (text_bbox[3] - text_bbox[1])) // 2
            draw.text((text_x, text_y), nama, font=font_main, fill=font_color)

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
        return None, None

