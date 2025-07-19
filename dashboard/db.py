import pymysql

# def get_connection():
#     return pymysql.connect(
#         host="127.0.0.1",
#         user="root",
#         password="",
#         database="db_ai",
#         cursorclass=pymysql.cursors.DictCursor
#     )

def get_connection():
    return pymysql.connect(
        host="100.124.58.32",  # IP tujuan
        user="root",
        password="",           # isi kalau ada password
        database="db_ai",
        cursorclass=pymysql.cursors.DictCursor
    )
