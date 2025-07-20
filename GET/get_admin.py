from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

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