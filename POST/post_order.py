# D:\image_controller_api\POST\post_order.py
# POST order
from flask import Blueprint, jsonify, request, send_from_directory
from datetime import datetime
import json
import sys
import os
import socket
import shutil
from dashboard.db import get_connection
from image_utils.image_utils import process_image_file

post_order_bp = Blueprint('post_order', __name__)

@post_order_bp.route('/api/order/create', methods=['POST'])
def create_order():
    data = request.json
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

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
                INSERT INTO order_detail (id_order_detail, id_order, nama, second_name, id_image, type_product, qty, product_note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_order_detail,
                id_order,
                item['nama'],
                item['second_name'],
                item['id_image'],
                item['type_product'],
                item['qty'],
                item['product_note']
            ))

            cursor.execute("SELECT image_path FROM images WHERE id_image = %s", (item['id_image'],))
            image = cursor.fetchone()
            image_path = image['image_path'] if image else None

            is_two_sided = "2 SISI" in item['type_product'].upper()
            has_second_name = item.get('second_name') and item['second_name'].strip() != ''
            
            for j in range(1, item['qty'] + 1):
                # Sisi pertama - selalu menggunakan nama
                id_print_side1 = f"{id_order_detail}-({j})-[1]"
                
                processed_path, output_filename, _, _, _ = process_image_file(
                    image_path=image_path,
                    id_print=id_print_side1,
                    product_note=item['product_note'],
                    type_product=item['type_product'],
                    qty=item['qty'],
                    nama=item['nama'],
                    id_input=id_order,
                    font_color=item.get('font_color', '#000000'),
                    is_preview=False,
                    is_side_one=True
                )
                
                # Insert record untuk sisi pertama
                cursor.execute("""
                    INSERT INTO print (id_print, id_order_detail, print_image_path, status)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_print_side1,
                    id_order_detail,
                    processed_path,
                    'belum_diprint'
                ))
                
                # Sisi kedua - jika 2 sisi, gunakan second_name jika ada, jika tidak gunakan nama
                if is_two_sided:
                    id_print_side2 = f"{id_order_detail}-({j})-[2]"
                    
                    # Jika ada second_name, gunakan itu untuk sisi kedua
                    # Jika tidak, gunakan nama yang sama dengan sisi pertama
                    display_name = item['second_name'] if has_second_name else item['nama']
                    
                    processed_path, output_filename, _, _, _ = process_image_file(
                        image_path=image_path,
                        id_print=id_print_side2,
                        product_note=item['product_note'],
                        type_product=item['type_product'],
                        qty=item['qty'],
                        nama=display_name,
                        id_input=id_order,
                        font_color=item.get('font_color', '#000000'),
                        is_preview=False,
                        is_side_one=False
                    )
                    
                    # Insert record untuk sisi kedua
                    cursor.execute("""
                        INSERT INTO print (id_print, id_order_detail, print_image_path, status)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        id_print_side2,
                        id_order_detail,
                        processed_path,
                        'belum_diprint'
                    ))

        conn.commit()
        return jsonify({"message": "Order berhasil dibuat", "id_order": id_order}), 201

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in create_order: {str(e)}\n{error_details}")
        if conn:
            conn.rollback()
        return jsonify({"error": str(e), "details": error_details}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@post_order_bp.route('/api/order/preview', methods=['POST'])
def preview_order():
    data = request.json
    id_image = data.get('id_image')
    nama = data.get('nama')
    second_name = data.get('second_name')
    qty = data.get('qty', 1)
    type_product = data.get('type_product')
    product_note = data.get('product_note', '')
    side = data.get('side', 1)  # Default ke sisi 1

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Ambil image path dari database
        cursor.execute("SELECT image_path FROM images WHERE id_image = %s", (id_image,))
        image = cursor.fetchone()
        image_path = image['image_path'] if image else None
        
        if not image_path:
            return jsonify({"error": "Image not found"}), 404

        # Setup preview directory
        now = datetime.now()
        ymd = now.strftime('%Y%m%d')
        preview_dir = os.path.join('D:/assets/PREVIEW', ymd)
        os.makedirs(preview_dir, exist_ok=True)
        
        # Generate unique preview ID dengan tambahan side jika ada
        timestamp = now.strftime('%H%M%S')
        id_print = f"PREVIEW-{id_image}-{timestamp}-S{side}"
        
        # Tentukan apakah ini sisi pertama atau kedua
        is_side_one = side == 1
        is_two_sided = "2 SISI" in type_product.upper()
        has_second_name = second_name and second_name.strip() != ''
        
        # Jika sisi kedua dan ada second_name, gunakan second_name sebagai nama
        # Jika sisi kedua tapi tidak ada second_name, tetap gunakan nama
        display_name = nama
        if not is_side_one and is_two_sided and has_second_name:
            display_name = second_name
        
        # Process image
        processed_path, output_filename, image_pil, dpi, icc_profile = process_image_file(
            image_path=image_path,
            id_print=id_print,
            product_note=product_note,
            type_product=type_product,
            qty=qty,
            nama=display_name,
            font_color=data.get('font_color', '#000000'),
            is_preview=True,
            is_side_one=is_side_one
        )
        
        if not output_filename:
            return jsonify({"error": "Failed to process image"}), 500

        # Save processed image to preview directory
        preview_path = os.path.join(preview_dir, output_filename)
        if image_pil:
            image_pil.save(preview_path, format='JPEG', quality=95, dpi=dpi, icc_profile=icc_profile)
        else:
            if processed_path and processed_path != preview_path:
                shutil.copy2(processed_path, preview_path)

        # Gunakan URL relatif dan host dari request untuk mendukung semua IP
        host = request.host
        preview_url = f"http://{host}/preview/{ymd}/{output_filename}"
        
        # Untuk kompatibilitas dengan kode lama, simpan juga URL alternatif
        preview_urls = [preview_url]
        
        # Save to preview table
        cursor.execute("""
            INSERT INTO preview (id_image, id_print, preview_path, preview_url, product_note, type_product, qty, nama, second_name, side)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_image,
            id_print,
            preview_path,
            preview_url,
            product_note,
            type_product,
            qty,
            nama,
            second_name,
            side
        ))
        
        # Tambahkan URL alternatif jika ada lebih dari satu IP
        for i in range(1, len(preview_urls)):
            alt_url = preview_urls[i]
            cursor.execute("""
                INSERT INTO preview_alt_urls (id_print, preview_url)
                VALUES (%s, %s)
            """, (id_print, alt_url))
        
        conn.commit()
        
        return jsonify({
            "preview_url": preview_url,
            "id_print": id_print,
            "message": "Preview berhasil dibuat",
            "side": side
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@post_order_bp.route('/preview/<path:filename>')
def serve_preview(filename):
    """Serve preview images from D:/assets/PREVIEW directory"""
    preview_root = 'D:/assets/PREVIEW'
    return send_from_directory(preview_root, filename)


@post_order_bp.route('/api/preview/list', methods=['GET'])
def list_previews():
    """Get list of all previews"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.*, i.image_name 
            FROM preview p 
            LEFT JOIN images i ON p.id_image = i.id_image 
            ORDER BY p.timestamp DESC
        """)
        
        previews = cursor.fetchall()
        
        return jsonify({
            "previews": previews,
            "total": len(previews)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@post_order_bp.route('/api/preview/<int:id_preview>', methods=['GET', 'DELETE'])
def handle_preview(id_preview):
    conn = get_connection()
    cursor = conn.cursor()
    
    if request.method == 'GET':
        try:
            cursor.execute("""
                SELECT p.*, i.image_name 
                FROM preview p 
                LEFT JOIN images i ON p.id_image = i.id_image 
                WHERE p.id_preview = %s
            """, (id_preview,))
            
            preview = cursor.fetchone()
            
            if not preview:
                return jsonify({"error": "Preview not found"}), 404
                
            return jsonify(preview)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()
    
    elif request.method == 'DELETE':
        try:
            # Get preview info first
            cursor.execute("SELECT preview_path FROM preview WHERE id_preview = %s", (id_preview,))
            preview = cursor.fetchone()
            
            if not preview:
                return jsonify({"error": "Preview not found"}), 404
            
            # Delete file if exists
            preview_path = preview['preview_path']
            if os.path.exists(preview_path):
                os.remove(preview_path)
            
            # Delete from database
            cursor.execute("DELETE FROM preview WHERE id_preview = %s", (id_preview,))
            conn.commit()
            
            return jsonify({"message": "Preview berhasil dihapus"})
            
        except Exception as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()