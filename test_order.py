import requests
import json
import sys
import os
sys.path.append(os.path.abspath('D:/image_controller_api'))
from dashboard.db import get_connection

# URL endpoint
url = "http://localhost:5000/api/order/create"

# Gunakan id_image yang ditentukan
valid_image_id = 451
print(f"Menggunakan id_image: {valid_image_id}")

# Data order
data = {
    "id_admin": 1,
    "platform": "Instagram",
    "nama_customer": "Test Customer",
    "deadline": "2025-07-25",
    "status_print": "belum_diprint",
    "items": [
        {
            "nama": "Test Nama",
            "id_image": valid_image_id,  # Gunakan id_image yang valid
            "type_product": "Marsoto 2 SISI",
            "qty": 1,
            "product_note": "Test Note",
            "font_color": "#000000"
        }
    ]
}

# Kirim request
response = requests.post(url, json=data)

# Tampilkan hasil
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")