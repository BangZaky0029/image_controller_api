from flask import Blueprint, jsonify
from ..dashboard.db import get_connection


get_images_bp = Blueprint('get_images_bp', __name__)

@get_images_bp.route('/images', methods=['GET'])
def get_images():
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            i.id_image,
            p.product_name,
            s.size,
            m.jenis_motif,
            i.image_name,
            i.image_path
        FROM images i
        LEFT JOIN product_list p ON i.id_product = p.id_product
        LEFT JOIN size s ON i.id_size = s.id_size
        LEFT JOIN motif m ON i.id_motif = m.id_motif
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
