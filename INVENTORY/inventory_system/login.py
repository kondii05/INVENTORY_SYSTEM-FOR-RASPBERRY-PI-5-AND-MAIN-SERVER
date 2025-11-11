import tkinter as tk
from tkinter import messagebox
from db import get_connection
from user_dashboard import open_user_dashboard
from faculty_dashboard import open_faculty_dashboard

# ---------------- LOGIN WINDOW ---------------- #

def login_window(root):
    win = tk.Toplevel(root)
    win.title("Login")
    win.geometry("400x200")
    win.configure(bg="#2c3e50")

    tk.Label(
        win, text="Scan RFID to Login (User / Faculty)",
        font=("Arial", 18, "bold"),
        bg="#2c3e50", fg="white"
    ).pack(pady=20)

    frame = tk.Frame(win, bg="#2c3e50")
    frame.pack(pady=10)

    tk.Label(frame, text="RFID Code:", bg="#2c3e50", fg="white", font=("Arial", 14)).grid(row=0, column=0, padx=5, pady=5)
    rfid_entry = tk.Entry(frame, font=("Arial", 14))
    rfid_entry.grid(row=0, column=1, padx=5, pady=5)

    def do_login(event=None):
        rfid = rfid_entry.get().strip()
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.")
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE rfid_code=%s", (rfid,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            win.destroy()
            if user["role"] == "user":
                open_user_dashboard(root, user)
            elif user["role"] == "faculty":
                open_faculty_dashboard(root, user)
            else:
                messagebox.showwarning("Access Denied", "Admins must use the Admin Login.")
        else:
            messagebox.showerror("Login Failed", "Unknown RFID code.")

    tk.Button(
        win, text="Login", bg="#27ae60", fg="white",
        font=("Arial", 14, "bold"), width=15, command=do_login
    ).pack(pady=15)

    rfid_entry.bind("<Return>", do_login)
    rfid_entry.focus()
