import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',      # Cambia por tu usuario MySQL
        password='root',  # Cambia por tu contraseña MySQL
        database='tesis4_db'
    )