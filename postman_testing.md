# Pengujian API dengan Postman

Dokumen ini berisi panduan untuk menguji API image_controller_api menggunakan Postman.

## Persiapan

1. Download dan install [Postman](https://www.postman.com/downloads/)
2. Jalankan aplikasi API dengan menjalankan `python main.py`
3. Pastikan server berjalan di `http://localhost:5000`

## Endpoint yang Akan Diuji

### 1. Health Check

- **URL**: `GET http://localhost:5000/health`
- **Deskripsi**: Memeriksa status API
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/health`
  3. Klik tombol Send
  4. Verifikasi response status 200 dan pesan sukses

### 2. Mendapatkan Semua Gambar

- **URL**: `GET http://localhost:5000/api/images/path`
- **Deskripsi**: Mendapatkan semua gambar dari semua merek
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/images/path`
  3. Klik tombol Send
  4. Verifikasi response status 200 dan data gambar

### 3. Mendapatkan Gambar berdasarkan Merek

- **URL**: `GET http://localhost:5000/api/images/path/{brand}`
- **Deskripsi**: Mendapatkan semua gambar untuk merek tertentu
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/images/path/Marsoto` (atau `MNK`)
  3. Klik tombol Send
  4. Verifikasi response status 200 dan data gambar

### 4. Mendapatkan Gambar berdasarkan Merek dan Subdirektori

- **URL**: `GET http://localhost:5000/api/images/path/{brand}/{subdir}`
- **Deskripsi**: Mendapatkan semua gambar untuk merek dan subdirektori tertentu
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/images/path/Marsoto/BATIK` (atau subdirektori lain)
  3. Klik tombol Send
  4. Verifikasi response status 200 dan data gambar

### 5. Mendapatkan Gambar Spesifik

- **URL**: `GET http://localhost:5000/api/images/path/{brand}/{subdir}/{image_name}`
- **Deskripsi**: Mendapatkan gambar spesifik berdasarkan merek, subdirektori, dan nama
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/images/path/Marsoto/BATIK/HM0001` (sesuaikan dengan nama gambar yang ada)
  3. Klik tombol Send
  4. Verifikasi response status 200 dan data gambar

### 6. Mendapatkan Gambar dalam Format Raw

- **URL**: `GET http://localhost:5000/api/images/path/{brand}/{subdir}/{image_name}?format=raw`
- **Deskripsi**: Mendapatkan file gambar langsung
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/images/path/Marsoto/BATIK/HM0001?format=raw` (sesuaikan dengan nama gambar yang ada)
  3. Klik tombol Send
  4. Verifikasi response berupa file gambar

### 7. Mendapatkan Subdirektori untuk Merek

- **URL**: `GET http://localhost:5000/api/subdirectories/{brand}`
- **Deskripsi**: Mendapatkan semua subdirektori untuk merek tertentu
- **Langkah-langkah**:
  1. Buat request GET baru di Postman
  2. Masukkan URL `http://localhost:5000/api/subdirectories/Marsoto` (atau `MNK`)
  3. Klik tombol Send
  4. Verifikasi response status 200 dan daftar subdirektori

## Membuat Koleksi Postman

Untuk memudahkan pengujian, Anda dapat membuat koleksi Postman:

1. Klik tombol "New" di Postman
2. Pilih "Collection"
3. Beri nama koleksi "Image Controller API"
4. Tambahkan semua request di atas ke dalam koleksi
5. Simpan koleksi

## Pengujian Otomatis

Anda juga dapat membuat pengujian otomatis di Postman:

1. Pada setiap request, klik tab "Tests"
2. Tambahkan script pengujian, contoh:

```javascript
// Pengujian status response
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Pengujian format response
pm.test("Response is JSON", function () {
    pm.response.to.be.json;
});

// Pengujian isi response
pm.test("Response has status success", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.status).to.equal("success");
});
```

3. Jalankan koleksi dengan mengklik tombol "Run" pada koleksi

## Ekspor dan Impor Koleksi

Anda dapat mengekspor koleksi untuk dibagikan:

1. Klik elipsis (...) pada koleksi
2. Pilih "Export"
3. Pilih format (JSON disarankan)
4. Simpan file

Untuk mengimpor:

1. Klik tombol "Import" di Postman
2. Pilih file koleksi yang diekspor
3. Klik "Import"

## Troubleshooting

- **Error 404**: Pastikan URL dan parameter sudah benar
- **Error 500**: Periksa log server untuk detail kesalahan
- **Tidak ada gambar**: Pastikan path direktori gambar sudah benar dan file gambar ada