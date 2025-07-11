# D:\image_controller_api\POST\post_order.py

from flask import Blueprint, jsonify, request
from datetime import datetime
import json
import sys
import os
from dashboard.db import get_connection
from image_utils.image_utils import process_image_file

post_order_bp = Blueprint('post_order', __name__)

@post_order_bp.route('/api/order/create', methods=['POST'])
def create_order():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now()
        prefix = now.strftime("%m") + now.strftime("%y")  # e.g. 0725

        cursor.execute("SELECT COUNT(*) AS count FROM orders WHERE id_order LIKE %s", (f"{prefix}-%",))
        order_count = cursor.fetchone()['count'] + 1
        id_order = f"{prefix}-{str(order_count).zfill(5)}"

        cursor.execute("""
            INSERT INTO orders (id_order, id_admin, platform, nama_customer, deadline, status_print)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_order,
            data['id_admin'],
            data['platform'],
            data['nama_customer'],
            data['deadline'],
            data['status_print']
        ))

        for i, item in enumerate(data['items'], start=1):
            id_order_detail = f"{id_order}-{i}"

            cursor.execute("""
                INSERT INTO order_detail (id_order_detail, id_order, nama, id_image, type_product, qty, product_note)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                id_order_detail,
                id_order,
                item['nama'],
                item['id_image'],
                item['type_product'],
                item['qty'],
                item['product_note']
            ))

            cursor.execute("SELECT image_path FROM images WHERE id_image = %s", (item['id_image'],))
            image = cursor.fetchone()
            image_path = image['image_path'] if image else None

            sisi = 2 if "2 SISI" in item['type_product'].upper() else 1

            for j in range(1, item['qty'] + 1):
                for k in range(1, sisi + 1):
                    id_print = f"{id_order_detail}-({j})-[{k}]"

                    processed_path, output_filename = process_image_file(
                        image_path=image_path,
                        id_print=id_print,
                        product_note=item['product_note'],
                        type_product=item['type_product'],
                        qty=item['qty'],
                        nama=item['nama'],
                        font_color_name="black"
                    )

                    cursor.execute("""
                        INSERT INTO print (id_print, id_order_detail, print_image_path, status)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        id_print,
                        id_order_detail,
                        processed_path,
                        'belum_diprint'
                    ))

        conn.commit()
        return jsonify({"message": "Order berhasil dibuat", "id_order": id_order}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@post_order_bp.route('/api/order/preview', methods=['POST'])
def preview_order():
    data = request.json
    id_image = data.get('id_image')
    nama = data.get('nama')
    qty = data.get('qty', 1)
    type_product = data.get('type_product')
    product_note = data.get('product_note', '')

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT image_path FROM images WHERE id_image = %s", (id_image,))
        image = cursor.fetchone()
        image_path = image['image_path'] if image else None
        if not image_path:
            return jsonify({"error": "Image not found"}), 404

        now = datetime.now()
        ymd = now.strftime('%Y%m%d')
        preview_dir = os.path.join('D:/assets/PREVIEW', ymd)
        os.makedirs(preview_dir, exist_ok=True)
        id_print = f"PREVIEW-{id_image}-{now.strftime('%H%M%S')}"
        processed_path, output_filename = process_image_file(
            image_path=image_path,
            id_print=id_print,
            product_note=product_note,
            type_product=type_product,
            qty=qty,
            nama=nama,
            font_color_name="black"
        )
        if not processed_path:
            return jsonify({"error": "Failed to process image"}), 500
        # Move/copy to preview_dir if needed
        preview_path = os.path.join(preview_dir, output_filename)
        if processed_path != preview_path:
            import shutil
            shutil.copy2(processed_path, preview_path)
        preview_url = f"http://localhost:5000/preview/{ymd}/{output_filename}"
        return jsonify({"preview_url": preview_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

from flask import send_from_directory
@post_order_bp.route('/preview/<path:filename>')
def serve_preview(filename):
    preview_root = os.path.join('D:/assets/PREVIEW')
    return send_from_directory(preview_root, filename)