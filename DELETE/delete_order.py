import os
from flask import Blueprint, request, jsonify
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

delete_order_bp = Blueprint('delete_order', __name__)

@delete_order_bp.route('/api/order/delete/<string:id_order>', methods=['DELETE'])
def delete_order(id_order):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Ambil semua id_order_detail dari order_detail yg berelasi ke id_order
        cursor.execute("SELECT id_order_detail FROM order_detail WHERE id_order = %s", (id_order,))
        order_details = cursor.fetchall()

        # Step 2: Hapus print dan file gambarnya
        for detail in order_details:
            id_order_detail = detail['id_order_detail']

            # Ambil path gambar dari table print
            cursor.execute("SELECT print_image_path FROM print WHERE id_order_detail = %s", (id_order_detail,))
            paths = cursor.fetchall()

            for row in paths:
                image_path = row['print_image_path']
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"[✔] Gambar dihapus: {image_path}")
                    except Exception as file_err:
                        print(f"[!] Gagal hapus file: {image_path}, error: {file_err}")

            # Hapus data print
            cursor.execute("DELETE FROM print WHERE id_order_detail = %s", (id_order_detail,))

        # Step 3: Hapus data dari order_detail
        cursor.execute("DELETE FROM order_detail WHERE id_order = %s", (id_order,))

        # Step 4: Hapus data dari orders
        cursor.execute("DELETE FROM orders WHERE id_order = %s", (id_order,))

        conn.commit()
        return jsonify({"message": f"Order {id_order} dan semua file relasinya berhasil dihapus"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

