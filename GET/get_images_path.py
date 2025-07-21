from flask import Blueprint, jsonify, send_file, request, abort
from flask_cors import CORS
import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our image utilities
from image_utils.image_path import (
    get_all_brand_images,
    get_images_by_brand_and_subdir,
    get_image_by_brand_subdir_name,
    get_image_by_path,
    get_subdirectories,
    BASE_DIRS
)

get_images_path_bp = Blueprint('get_images_path', __name__)
CORS(get_images_path_bp)

@get_images_path_bp.route('/api/images/path', methods=['GET'])
def get_all_images_path():
    """
    Get all images from all brands using path-based API
    """
    try:
        images = get_all_brand_images()
        return jsonify({
            'status': 'success',
            'data': images
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/path/<brand>', methods=['GET'])
def get_brand_images_path(brand):
    """
    Get all images for a specific brand using path-based API
    """
    try:
        if brand not in BASE_DIRS:
            return jsonify({
                'status': 'error',
                'message': f'Invalid brand: {brand}. Must be one of {list(BASE_DIRS.keys())}'
            }), 400
            
        images = []
        for subdir in get_subdirectories(brand):
            images.extend(get_images_by_brand_and_subdir(brand, subdir))
            
        return jsonify({
            'status': 'success',
            'data': images
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/path/<brand>/<subdir>', methods=['GET'])
def get_subdir_images_path(brand, subdir):
    """
    Get all images for a specific brand and subdirectory using path-based API
    """
    try:
        images = get_images_by_brand_and_subdir(brand, subdir)
        return jsonify({
            'status': 'success',
            'data': images
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/path/<brand>/<subdir>/<image_name>', methods=['GET'])
def get_image_path(brand, subdir, image_name):
    """
    Get a specific image by brand, subdirectory, and name using path-based API
    """
    try:
        # Remove .jpg extension if present
        if image_name.lower().endswith('.jpg'):
            image_name = os.path.splitext(image_name)[0]
            
        image_info = get_image_by_brand_subdir_name(brand, subdir, image_name)
        
        # Check if the image exists
        if not image_info['exists']:
            return jsonify({
                'status': 'error',
                'message': f'Image not found: {image_name}'
            }), 404
            
        # Check if the request wants the raw image file
        if request.args.get('format') == 'raw':
            return send_file(image_info['path'], mimetype='image/jpeg')
        else:
            # Return the image info
            return jsonify({
                'status': 'success',
                'data': image_info
            })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images', methods=['GET'])
def get_all_images():
    """
    Get all images from all brands
    """
    try:
        images = get_all_brand_images()
        return jsonify({
            'status': 'success',
            'data': images
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/<brand>', methods=['GET'])
def get_brand_images(brand):
    """
    Get all images for a specific brand
    """
    try:
        if brand not in BASE_DIRS:
            return jsonify({
                'status': 'error',
                'message': f'Invalid brand: {brand}. Must be one of {list(BASE_DIRS.keys())}'
            }), 400
            
        # Get subdirectories for this brand
        subdirs = get_subdirectories(brand)
        
        # Get images for each subdirectory
        result = {}
        for subdir in subdirs:
            result[subdir] = get_images_by_brand_and_subdir(brand, subdir)
            
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/<brand>/<subdir>', methods=['GET'])
def get_subdir_images(brand, subdir):
    """
    Get all images for a specific brand and subdirectory
    """
    try:
        images = get_images_by_brand_and_subdir(brand, subdir)
        return jsonify({
            'status': 'success',
            'data': images
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/images/<brand>/<subdir>/<image_name>', methods=['GET'])
def get_image(brand, subdir, image_name):
    """
    Get a specific image by brand, subdirectory, and name
    """
    try:
        # Remove .jpg extension if present
        if image_name.lower().endswith('.jpg'):
            image_name = os.path.splitext(image_name)[0]
            
        image_info = get_image_by_brand_subdir_name(brand, subdir, image_name)
        
        # Check if the image exists
        if not image_info['exists']:
            return jsonify({
                'status': 'error',
                'message': f'Image not found: {image_name}'
            }), 404
            
        # Check if the request wants the image file or the image info
        if request.args.get('info') == 'true':
            return jsonify({
                'status': 'success',
                'data': image_info
            })
        else:
            # Return the actual image file
            return send_file(image_info['path'], mimetype='image/jpeg')
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/api/subdirectories/<brand>', methods=['GET'])
def get_brand_subdirectories(brand):
    """
    Get all subdirectories for a specific brand
    """
    try:
        subdirs = get_subdirectories(brand)
        return jsonify({
            'status': 'success',
            'data': subdirs
        })
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@get_images_path_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'success',
        'message': 'Image API is running'
    })

# Blueprint tidak dapat dijalankan langsung seperti aplikasi Flask
# Untuk menjalankan aplikasi, gunakan file utama yang mengimpor blueprint ini