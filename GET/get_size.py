from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

get_size_bp = Blueprint('get_size_bp', __name__)

@get_size_bp.route('/sizes', methods=['GET'])
def get_size():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM size")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
