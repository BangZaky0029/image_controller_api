from flask import Blueprint, jsonify
from ..dashboard.db import get_connection

get_product_bp = Blueprint('get_product_bp', __name__)

@get_product_bp.route('/products', methods=['GET'])
def get_product_list():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM product_list")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
