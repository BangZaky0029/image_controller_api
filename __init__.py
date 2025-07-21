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
    get_print_bp,
    get_images_path_bp
)

from .POST import (
    post_order_bp
)

from .DELETE import (
    delete_order_bp,
    delete_preview_bp
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
    app.register_blueprint(get_images_path_bp)

    # ✅ Register POST blueprint
    app.register_blueprint(post_order_bp)


    # ✅ Register UPDATE blueprint

    # ✅ Register DELETE blueprint
    app.register_blueprint(delete_order_bp)
    app.register_blueprint(delete_preview_bp)

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
    
    # ✅ Static file serving untuk CSS dan JS files
    @app.route('/style/<path:filename>')
    def serve_css(filename):
        try:
            # Path ke folder style di frontend
            style_directory = r'D:\image_interFace_db\style'
            response = send_from_directory(style_directory, filename)
            # Set proper MIME type untuk CSS files
            if filename.endswith('.css'):
                response.headers['Content-Type'] = 'text/css'
            return response
        except Exception as e:
            print(f"Error serving CSS file {filename}: {e}")
            return '', 404
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        try:
            # Path ke folder js di frontend
            js_directory = r'D:\image_interFace_db\js'
            response = send_from_directory(js_directory, filename)
            # Set proper MIME type untuk JS files
            if filename.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript'
            return response
        except Exception as e:
            print(f"Error serving JS file {filename}: {e}")
            return '', 404
    
    @app.route('/config/<path:filename>')
    def serve_config(filename):
        try:
            # Path ke folder config di frontend
            config_directory = r'D:\image_interFace_db\config'
            response = send_from_directory(config_directory, filename)
            # Set proper MIME type untuk JS files
            if filename.endswith('.js'):
                response.headers['Content-Type'] = 'application/javascript'
            return response
        except Exception as e:
            print(f"Error serving config file {filename}: {e}")
            return '', 404
    
    @app.route('/views/<path:filename>')
    def serve_views(filename):
        try:
            # Path ke folder views di frontend
            views_directory = r'D:\image_interFace_db\views'
            response = send_from_directory(views_directory, filename)
            # Set proper MIME type untuk HTML files
            if filename.endswith('.html'):
                response.headers['Content-Type'] = 'text/html'
            return response
        except Exception as e:
            print(f"Error serving view file {filename}: {e}")
            return '', 404

    return app
