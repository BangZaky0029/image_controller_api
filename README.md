# Image Controller API

API untuk mengakses dan mengelola gambar dari direktori database_images.

## Struktur Direktori

```
D:\assets\database_images\
├── Marsoto\
│   ├── BATIK\
│   ├── DUBAI\
│   ├── EID\
│   └── NM\
└── MNK\
```

## Instalasi

1. Pastikan Python 3.7+ sudah terinstal
2. Install dependensi yang diperlukan:

```bash
pip install flask flask-cors
```

## Menjalankan API

```bash
python image_api.py
```

API akan berjalan di http://localhost:5001

## Endpoint API

### Health Check

```
GET /health
```

Memeriksa status API.

### Mendapatkan Semua Gambar

```
GET /api/images
```

Mendapatkan semua gambar dari semua brand.

### Mendapatkan Gambar Berdasarkan Brand

```
GET /api/images/<brand>
```

Mendapatkan semua gambar untuk brand tertentu (Marsoto atau MNK).

### Mendapatkan Gambar Berdasarkan Brand dan Subdirektori

```
GET /api/images/<brand>/<subdir>
```

Mendapatkan semua gambar untuk brand dan subdirektori tertentu.

### Mendapatkan Gambar Spesifik

```
GET /api/images/<brand>/<subdir>/<image_name>
```

Mendapatkan gambar spesifik berdasarkan brand, subdirektori, dan nama gambar.

Parameter query:
- `info=true`: Mengembalikan informasi gambar dalam format JSON alih-alih file gambar.

### Mendapatkan Subdirektori

```
GET /api/subdirectories/<brand>
```

Mendapatkan semua subdirektori untuk brand tertentu.

## Contoh Penggunaan

### Mendapatkan Semua Gambar Marsoto

```
GET http://localhost:5001/api/images/Marsoto
```

### Mendapatkan Gambar Batik Marsoto

```
GET http://localhost:5001/api/images/Marsoto/BATIK
```

### Mendapatkan Gambar Spesifik

```
GET http://localhost:5001/api/images/Marsoto/BATIK/HM0001
```

### Mendapatkan Informasi Gambar

```
GET http://localhost:5001/api/images/Marsoto/BATIK/HM0001?info=true
```