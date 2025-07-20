import os
from flask import Blueprint, request, jsonify
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

delete_preview_bp = Blueprint('delete_preview', __name__)

@delete_preview_bp.route('/api/preview/<int:id_preview>', methods=['DELETE'])
def delete_preview(id_preview):
    """Delete preview by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
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