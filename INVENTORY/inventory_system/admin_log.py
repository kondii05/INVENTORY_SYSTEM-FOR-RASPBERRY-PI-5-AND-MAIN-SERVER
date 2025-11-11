from db import get_connection
from datetime import datetime
import socket

def log_admin_action(admin_name, action, item_name=None, user_name=None):
    device = socket.gethostname()  # laptop or Pi name
    conn = get_connection()
    if not conn:
        print("⚠️  Could not connect to DB for logging.")
        return
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO admin_logs (admin_name, action, item_name, user_name, device_name, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (admin_name, action, item_name, user_name, device, datetime.now()))
        conn.commit()
    except Exception as e:
        print("❌  Failed to log admin action:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()
