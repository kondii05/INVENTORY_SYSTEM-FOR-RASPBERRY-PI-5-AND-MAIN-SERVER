import tkinter as tk
from tkinter import messagebox
from db import get_connection
from admin_dashboard import open_admin_dashboard

def admin_login_window(root):
    import admin_dashboard
    win = tk.Toplevel(root)
    win.title("Admin Login")
    win.geometry("400x200")
    win.configure(bg="#2c3e50")

    tk.Label(
        win, text="Scan RFID to Login (Admin)",
        font=("Arial", 18, "bold"),
        bg="#2c3e50", fg="white"
    ).pack(pady=20)

    frame = tk.Frame(win, bg="#2c3e50")
    frame.pack(pady=10)

    tk.Label(frame, text="RFID Code:", bg="#2c3e50", fg="white", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
    rfid_entry = tk.Entry(frame, font=("Arial", 14))
    rfid_entry.grid(row=0, column=1, padx=5, pady=5)

    def do_admin_login(event=None):
        rfid = rfid_entry.get().strip()
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE rfid_code=%s AND role='admin'", (rfid,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin:
            win.destroy()
            open_admin_dashboard(root, admin)
        else:
            messagebox.showerror("Login Failed", "Unknown RFID code or not an Admin.")

    tk.Button(
        win, text="Login", bg="#c0392b", fg="white",
        font=("Arial", 14, "bold"), width=15, command=do_admin_login
    ).pack(pady=15)

    rfid_entry.bind("<Return>", do_admin_login)
    rfid_entry.focus()
