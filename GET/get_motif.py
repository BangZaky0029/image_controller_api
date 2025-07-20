from flask import Blueprint, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dashboard.db import get_connection

get_motif_bp = Blueprint('get_motif_bp', __name__)

@get_motif_bp.route('/motif', methods=['GET'])
def get_motif():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM motif")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(result)
