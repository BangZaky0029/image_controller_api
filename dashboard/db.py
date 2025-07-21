import pymysql

def get_connection():
    # Daftar IP yang bisa digunakan
    hosts = ["100.124.58.32", "192.168.0.95"]
    
    # Coba koneksi ke semua host yang tersedia
    last_error = None
    for host in hosts:
        try:
            return pymysql.connect(
                host=host,
                user="root",
                password="",
                database="db_ai",
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            last_error = e
            continue
    
    # Jika semua remote gagal, coba local
    try:
        return pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="db_ai",
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        # Jika semua koneksi gagal, raise error terakhir
        raise last_error

# Hapus fungsi get_connection() kedua yang duplikat

# 2. Perbaikan Server Error 500 pada /api/order/create

# Perbaikan di db.py untuk menangani koneksi database

def get_all_order_ids():
    """
    Mengambil semua id_order dari database
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id_order FROM orders")
            results = cursor.fetchall()
            return [result['id_order'] for result in results]
    except Exception as e:
        print(f"Error getting order IDs: {e}")
        return []
    finally:
        conn.close()
