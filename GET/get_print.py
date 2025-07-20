from flask import Blueprint, jsonify, send_from_directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

get_print_bp = Blueprint('get_print_bp', __name__)

def convert_path_to_url(print_image_path, base_url="http://100.124.58.32:5000"):
    """
    Convert print image path to URL format
    """
    if not print_image_path:
        return None
    
    # Normalize path separators
    normalized_path = print_image_path.replace('\\', '/')
    
    # Extract relative path from PRINT folder
    if 'D:/assets/PRINT/' in normalized_path:
        # Remove the base path
        relative_path = normalized_path.replace('D:/assets/PRINT/', '')
        return f"{base_url}/print-image/{relative_path}"
    elif 'D:\\assets\\PRINT\\' in normalized_path:
        # Handle Windows backslash format
        relative_path = normalized_path.replace('D:\\assets\\PRINT\\', '')
        # Convert backslashes to forward slashes
        relative_path = relative_path.replace('\\', '/')
        return f"{base_url}/print-image/{relative_path}"
    
    # Fallback: just use the filename
    filename = os.path.basename(normalized_path)
    return f"{base_url}/print-image/{filename}"

@get_print_bp.route('/print', methods=['GET'])
def get_print():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM print")
    raw_data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convert paths to URLs
    result = []
    for row in raw_data:
        print_data = dict(row)
        # Convert print_image_path to URL if it exists
        if 'print_image_path' in print_data and print_data['print_image_path']:
            print_data['print_image_url'] = convert_path_to_url(print_data['print_image_path'])
        else:
            print_data['print_image_url'] = None
        result.append(print_data)
    
    return jsonify(result)

@get_print_bp.route('/print-image/<path:filepath>')
def serve_print_image(filepath):
    """
    Serve print images from D:/assets/PRINT directory
    """
    # Normalize the path for Windows
    filepath = filepath.replace('/', os.path.sep)
    
    # Construct the full path
    full_path = os.path.join('D:\\assets\\PRINT', filepath)
    
    # Check if the file exists
    if os.path.isfile(full_path):
        # Get the directory and filename
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)
    else:
        return '', 404
