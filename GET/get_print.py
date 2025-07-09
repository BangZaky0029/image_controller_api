from flask import Blueprint, jsonify
from ..dashboard.db import get_connection

get_print_bp = Blueprint('get_print_bp', __name__)

@get_print_bp.route('/print', methods=['GET'])
def get_print():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM print")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)
