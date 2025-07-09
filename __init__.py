from flask import Flask, send_from_directory
from flask_cors import CORS  # ✅ Tambahkan ini
import os


from .GET import (
    get_images_bp,
    get_motif_bp,
    get_product_bp,
    get_size_bp,
    get_admin_bp,
    get_orders_bp,
    get_order_detail_bp,
    get_print_bp
)

from .POST import (
    post_order_bp
)

from .DELETE import (
    delete_order_bp
)

def create_app():
    app = Flask(__name__)

    # ✅ Aktifin CORS biar frontend bisa akses API
    CORS(app)

    # Register all GET blueprints
    app.register_blueprint(get_images_bp)
    app.register_blueprint(get_motif_bp)
    app.register_blueprint(get_product_bp)
    app.register_blueprint(get_size_bp)
    # Tambahan baru
    app.register_blueprint(get_admin_bp)
    app.register_blueprint(get_orders_bp)
    app.register_blueprint(get_order_detail_bp)
    app.register_blueprint(get_print_bp)

    # ✅ Register POST blueprint
    app.register_blueprint(post_order_bp)


    # ✅ Register UPDATE blueprint

    # ✅ Register DELETE blueprint
    app.register_blueprint(delete_order_bp)

    # ✅ Static file serving untuk gambar
    @app.route('/static/images/<path:filename>')
    def serve_image(filename):
        try:
            # Path ke folder gambar
            image_directory = r'D:\assets\database_images'
            return send_from_directory(image_directory, filename)
        except Exception as e:
            print(f"Error serving image {filename}: {e}")
            # Return placeholder image jika file tidak ditemukan
            return '', 404

    return app
