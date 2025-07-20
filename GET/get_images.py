from flask import Blueprint, jsonify, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection


get_images_bp = Blueprint('get_images_bp', __name__)

def convert_path_to_url(image_path, base_url="http://localhost:5000"):
    """
    Convert Windows absolute path to URL format
    """
    if not image_path:
        return None
    
    # Normalize path separators
    normalized_path = image_path.replace('\\', '/')
    
    # Extract relative path from database_images folder
    if 'database_images' in normalized_path:
        # Find the index of 'database_images' and get everything after it
        db_images_index = normalized_path.find('database_images')
        if db_images_index != -1:
            relative_path = normalized_path[db_images_index + len('database_images'):]
            # Remove leading slash if present
            relative_path = relative_path.lstrip('/')
            return f"{base_url}/static/images/{relative_path}"
    
    # Fallback: try to extract filename
    filename = os.path.basename(normalized_path)
    return f"{base_url}/static/images/{filename}"

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
    raw_result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert paths to URLs
    result = []
    for row in raw_result:
        image_data = dict(row)
        # Convert image_path to URL
        if 'image_path' in image_data:
            image_data['image_url'] = convert_path_to_url(image_data['image_path'])
        result.append(image_data)
    
    return jsonify(result)
