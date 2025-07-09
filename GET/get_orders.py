from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

get_orders_bp = Blueprint('get_orders_bp', __name__)

@get_orders_bp.route('/orders', methods=['GET'])
def get_orders():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
