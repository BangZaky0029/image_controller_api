from flask import Blueprint, jsonify
from ..dashboard.db import get_connection

get_admin_bp = Blueprint('get_admin_bp', __name__)

@get_admin_bp.route('/admin', methods=['GET'])
def get_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
