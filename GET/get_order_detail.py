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
    
    # Join order_detail with orders table to get order information
    cursor.execute("""
        SELECT od.*, o.platform, o.deadline, o.nama_customer, o.timestamp, o.status_print 
        FROM order_detail od
        LEFT JOIN orders o ON od.id_order = o.id_order
    """)
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
