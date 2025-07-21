import os
import sys
import re
sys.path.append(os.path.abspath('D:/image_controller_api'))
from datetime import datetime
import logging
from dashboard.db import get_connection, get_all_order_ids

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_output_image_path(base_dir, id_input, id_print, image_path):
    """
    Membuat path output untuk file hasil model.
    Struktur: base_dir/JULY/21/Marsoto/{id_input}/{id_print}_{nama_image}.jpg
    """
    now = datetime.now()
    month = now.strftime('%B').upper()
    day = now.strftime('%d')
    # Ambil nama product dari path image
    path_parts = os.path.normpath(image_path).split(os.sep)
    product = path_parts[-3] if len(path_parts) >= 3 else "UnknownProduct"
    
    # Log nilai id_input yang diterima
    logger.debug(f"Received id_input: {id_input}, type: {type(id_input)}")
    
    # Pastikan id_input adalah string untuk perbandingan yang konsisten
    id_input_str = str(id_input) if id_input is not None else ''
    
    # Periksa apakah id_input memiliki format id_order yang valid (misalnya: MMYY-NNNNN)
    if id_input_str and re.match(r'^\d{4}-\d{5}$', id_input_str):
        logger.debug(f"Using id_input as folder name: {id_input_str}")
    else:
        # Jika id_input tidak memiliki format id_order yang valid, coba validasi dengan database
        try:
            valid_order_ids = get_all_order_ids()
            logger.debug(f"Valid order IDs from database: {valid_order_ids}")
            
            # Gunakan id_input jika ada di database, jika tidak gunakan 'UnknownID'
            if id_input_str and id_input_str in valid_order_ids:
                logger.debug(f"Using valid id_input from database: {id_input_str}")
            else:
                logger.debug(f"id_input '{id_input_str}' not found in valid_order_ids, using 'UnknownID'")
                id_input_str = 'UnknownID'
        except Exception as e:
            # Jika terjadi error saat mengambil data dari database, gunakan id_input langsung
            logger.error(f"Error validating id_input: {e}")
            id_input_str = str(id_input) if id_input and str(id_input) != 'None' and str(id_input) != '' else 'UnknownID'
    
    # Folder tujuan: .../JULY/21/Marsoto/{id_input}
    target_dir = os.path.join(base_dir, month, day, product, id_input_str)
    logger.debug(f"Creating directory: {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    # Nama file: {id_print}_{nama_image}.jpg
    image_filename = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{id_print}_{image_filename}.jpg"
    output_path = os.path.join(target_dir, output_filename)
    return output_path, output_filename