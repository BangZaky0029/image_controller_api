from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

get_order_detail_bp = Blueprint('get_order_detail_bp', __name__)

@get_order_detail_bp.route('/order_detail', methods=['GET'])
def get_order_detail():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM order_detail")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
