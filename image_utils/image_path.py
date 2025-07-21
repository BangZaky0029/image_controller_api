import os
import glob
from typing import List, Dict, Optional, Union
from urllib.parse import quote

# Base directories for image storage
# Contoh perbaikan dengan pathlib
from pathlib import Path

# Base directories for image storage
BASE_DIRS = {
    'Marsoto': Path('D:/assets/database_images/Marsoto'),
    'MNK': Path('D:/assets/database_images/MNK')
}

# Subdirectories in Marsoto
MARSOTO_SUBDIRS = ['BATIK', 'DUBAI', 'EID', 'NM']

# API Base URL for serving images
API_BASE_URL = 'http://100.124.58.32:5000/api/images'

def get_image_path(brand: str, subdir: Optional[str] = None, image_name: Optional[str] = None) -> str:
    """
    Get the full path to an image based on brand, subdirectory, and image name
    
    Args:
        brand: Brand name ('Marsoto' or 'MNK')
        subdir: Subdirectory name (e.g., 'BATIK', 'DUBAI', etc.)
        image_name: Image name without extension (e.g., 'HM0001')
        
    Returns:
        Full path to the image or directory
    """
    if brand not in BASE_DIRS:
        raise ValueError(f"Invalid brand: {brand}. Must be one of {list(BASE_DIRS.keys())}")
    
    base_path = BASE_DIRS[brand]
    
    if not subdir:
        return str(base_path).replace('\\', '/')
    
    subdir_path = os.path.join(base_path, subdir)
    
    if not image_name:
        return str(subdir_path).replace('\\', '/')
    
    # Assume .jpg extension if not specified
    if not image_name.lower().endswith('.jpg'):
        image_name = f"{image_name}.jpg"
    
    path = os.path.join(subdir_path, image_name)
    return str(path).replace('\\', '/')

def path_to_url(image_path: str) -> str:
    """
    Convert a file system path to a URL for API access
    
    Args:
        image_path: Full path to the image file
        
    Returns:
        URL for accessing the image via API
    """
    # Check if path exists in our base directories
    brand = get_brand_from_path(image_path)
    if not brand:
        return ""
    
    # Get relative path components
    base_dir = BASE_DIRS[brand]
    # Ensure both paths use forward slashes before computing relative path
    normalized_image_path = str(image_path).replace('\\', '/')
    normalized_base_dir = str(base_dir).replace('\\', '/')
    
    # Use os.path.relpath with normalized paths
    rel_path = os.path.relpath(normalized_image_path, normalized_base_dir)
    
    # Ensure forward slashes and split path components
    path_components = rel_path.replace('\\', '/').split('/')
    encoded_components = [quote(component) for component in path_components]
    encoded_path = '/'.join(encoded_components)
    
    # Construct the API URL
    return f"{API_BASE_URL}/{brand}/{encoded_path}"

def list_images(brand: str, subdir: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List all images in a specific brand and optional subdirectory
    
    Args:
        brand: Brand name ('Marsoto' or 'MNK')
        subdir: Optional subdirectory name
        
    Returns:
        List of dictionaries with image information
    """
    # Validasi brand
    if brand not in BASE_DIRS:
        raise ValueError(f"Invalid brand: {brand}. Must be one of {list(BASE_DIRS.keys())}")
    
    base_path = BASE_DIRS[brand]
    
    # Periksa keberadaan direktori
    if not os.path.exists(base_path):
        return []
    
    if subdir:
        subdir_path = os.path.join(base_path, subdir)
        if not os.path.exists(subdir_path):
            return []
        search_path = os.path.join(subdir_path, "*.jpg")
    else:
        search_path = os.path.join(base_path, "**", "*.jpg")
    
    # Gunakan try-except untuk menangani potensi error
    try:
        image_files = glob.glob(search_path, recursive=True if not subdir else False)
    except Exception as e:
        print(f"Error listing images: {e}")
        return []
    
    result = []
    for img_path in image_files:
        # Normalize path to use forward slashes
        normalized_path = str(img_path).replace('\\', '/')
        img_name = os.path.basename(normalized_path)
        img_subdir = os.path.basename(os.path.dirname(normalized_path))
        result.append({
            'name': img_name,
            'name_without_ext': os.path.splitext(img_name)[0],
            'path': normalized_path,
            'url': path_to_url(img_path),
            'subdirectory': img_subdir,
            'brand': brand
        })
    
    return result

def get_subdirectories(brand: str) -> List[str]:
    """
    Get all subdirectories for a specific brand
    
    Args:
        brand: Brand name ('Marsoto' or 'MNK')
        
    Returns:
        List of subdirectory names
    """
    if brand not in BASE_DIRS:
        raise ValueError(f"Invalid brand: {brand}. Must be one of {list(BASE_DIRS.keys())}")
    
    base_path = BASE_DIRS[brand]
    
    if not os.path.exists(base_path):
        return []
    
    # Return directory names only, no need to normalize paths here
    # as these are just directory names, not full paths
    return [d for d in os.listdir(base_path) 
            if os.path.isdir(os.path.join(base_path, d))]

def get_image_info(image_path: str) -> Dict[str, Union[str, bool, int]]:
    """
    Get information about an image file
    
    Args:
        image_path: Full path to the image file
        
    Returns:
        Dictionary with image information
    """
    # Normalize path to use forward slashes
    normalized_path = str(image_path).replace('\\', '/')
    
    if not os.path.exists(image_path):
        return {
            'exists': False,
            'path': normalized_path,
            'url': path_to_url(image_path),
            'name': os.path.basename(normalized_path),
            'name_without_ext': os.path.splitext(os.path.basename(normalized_path))[0],
            'size': 0,
            'subdirectory': os.path.basename(os.path.dirname(normalized_path)),
            'brand': get_brand_from_path(image_path)
        }
    
    return {
        'exists': True,
        'path': normalized_path,
        'url': path_to_url(image_path),
        'name': os.path.basename(normalized_path),
        'name_without_ext': os.path.splitext(os.path.basename(normalized_path))[0],
        'size': os.path.getsize(image_path),
        'subdirectory': os.path.basename(os.path.dirname(normalized_path)),
        'brand': get_brand_from_path(image_path)
    }

def get_brand_from_path(image_path: str) -> str:
    """
    Extract brand name from image path
    
    Args:
        image_path: Full path to the image file
        
    Returns:
        Brand name or empty string if not found
    """
    # Normalize path with forward slashes for consistent comparison
    norm_path = os.path.normpath(image_path).replace('\\', '/')
    for brand, base_dir in BASE_DIRS.items():
        norm_base = str(base_dir).replace('\\', '/')
        # Pastikan ini adalah subdirektori yang tepat, bukan substring biasa
        if norm_path.startswith(norm_base + '/') or norm_path == norm_base:
            return brand
    return ""

# API Functions for retrieving image data
def get_all_brand_images() -> Dict[str, List[Dict[str, Union[str, bool, int]]]]:
    """
    Get all images from all brands
    
    Returns:
        Dictionary with brand names as keys and lists of image info as values
    """
    result = {}
    for brand in BASE_DIRS.keys():
        result[brand] = list_images(brand)
    return result

def get_image_by_path(image_path: str) -> Dict[str, Union[str, bool, int]]:
    """
    Get image information by path
    
    Args:
        image_path: Full path to the image file
        
    Returns:
        Dictionary with image information
    """
    return get_image_info(image_path)

def get_images_by_brand_and_subdir(brand: str, subdir: str) -> List[Dict[str, Union[str, bool, int]]]:
    """
    Get images by brand and subdirectory
    
    Args:
        brand: Brand name ('Marsoto' or 'MNK')
        subdir: Subdirectory name
        
    Returns:
        List of dictionaries with image information
    """
    return list_images(brand, subdir)

def get_image_by_brand_subdir_name(brand: str, subdir: str, image_name: str) -> Dict[str, Union[str, bool, int]]:
    """
    Get a specific image by brand, subdirectory, and name
    
    Args:
        brand: Brand name ('Marsoto' or 'MNK')
        subdir: Subdirectory name
        image_name: Image name without extension
        
    Returns:
        Dictionary with image information
    """
    image_path = get_image_path(brand, subdir, image_name)
    return get_image_info(image_path)