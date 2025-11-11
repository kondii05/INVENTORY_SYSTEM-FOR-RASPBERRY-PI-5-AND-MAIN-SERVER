import mysql.connector
from mysql.connector import Error
import threading
import os

def get_connection():
    try:
        conn = mysql.connector.connect(
    host="192.168.1.22",
    port=3306,
    user="admin",
    password="Inventory1234",   # or your root password
    database="inventory_db"
)

        if conn.is_connected():
            print("✅ Database connection successful.")
        return conn
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

