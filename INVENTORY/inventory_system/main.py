import tkinter as tk
from tkinter import messagebox
from db import get_connection
import os
import time
import threading
import subprocess
import sys
from admin_dashboard import open_admin_dashboard
import mysql.connector
from PIL import Image, ImageTk

# ---------- CONFIGURATION ----------
SCHOOL_NAME = "Manuel S. Enverga University Foundation-Candelaria Inc."
BG_COLOR = "#ffffff"
ACCENT_COLOR = "#800000"
TEXT_COLOR = "#800000"
FONT_SCHOOL = ("Segoe UI", 45, "bold")
FONT_MAIN = ("Segoe UI", 32, "bold")
FONT_SUB = ("Segoe UI", 16)


def get_user_info(rfid_code):
    """Query the database for full user info by RFID tag."""
    conn = get_connection()
    if not conn:
        messagebox.showerror("Database Error", "Unable to connect to database.")
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, name, rfid_code, role, section 
        FROM users 
        WHERE rfid_code = %s
    """, (rfid_code,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def open_dashboard(role):
    """Open the appropriate dashboard safely using the same Python interpreter."""
    dashboards = {
        "admin": "admin_dashboard.py",
        "faculty": "faculty_dashboard.py",
        "user": "user_dashboard.py",
    }

    role = role.lower().strip()
    script = dashboards.get(role)
    if not script:
        messagebox.showerror("Access Denied", f"Unknown role: {role}")
        return

    script_path = os.path.join(os.path.dirname(__file__), script)
    if not os.path.exists(script_path):
        messagebox.showerror("File Not Found", f"Cannot find: {script_path}")
        return

    try:
        subprocess.Popen([sys.executable, script_path])
        print(f"✅ Successfully launched: {script_path}")
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to open {script}: {e}")
        print(f"❌ Launch failed: {e}")


def process_rfid(tag, root, label_status):
    """Check RFID tag in DB and redirect to dashboard."""
    import socket
    label_status.config(text=f"Checking tag: {tag}", fg=ACCENT_COLOR)
    time.sleep(0.3)
    user = get_user_info(tag)

    if user:
        role = user["role"].lower()
        label_status.config(text=f"Welcome, {user['name']} ({role.title()})!", fg=ACCENT_COLOR)

        # Device restrictions
        hostname = socket.gethostname()
        print("🔍 Detected hostname:", hostname)
        BLOCKED_ADMIN_HOSTS = ["inventoryxx", "inventoryx"]  # 🔒 Replace with your Raspberry Pi 5 hostnames
        ALLOWED_ADMIN_HOSTS = ["MALUPIT_NA_PC"]          # ✅ Replace with your laptop's hostname

        def open_next():
            root.after(200, lambda: root.withdraw())

        # 🔐 Role-based redirection with security restrictions
        if role == "admin":
            if hostname in BLOCKED_ADMIN_HOSTS:
                label_status.config(
                    text="🚫 Admin login is not allowed on this Raspberry Pi terminal.",
                    fg="#800000"
                )
                root.after(2500, lambda: label_status.config(
                    text="Please scan your RFID card again", fg=TEXT_COLOR
                ))
                return
            elif hostname not in ALLOWED_ADMIN_HOSTS:
                label_status.config(
                    text="🚫 This device is not authorized for admin access.",
                    fg="#800000"
                )
                root.after(2500, lambda: label_status.config(
                    text="Please scan your RFID card again", fg=TEXT_COLOR
                ))
                return
            else:
                from admin_dashboard import open_admin_dashboard
                root.after(0, lambda: open_admin_dashboard(root, user))

        elif role == "faculty":
            from faculty_dashboard import open_faculty_dashboard
            root.after(0, lambda: open_faculty_dashboard(root, user))

        elif role == "user":
            from user_dashboard import open_user_dashboard
            root.after(0, lambda: open_user_dashboard(root, user))

        root.after(100, open_next)

    else:
        label_status.config(text="Access Denied: Unknown RFID", fg="#800000")
        root.after(1500, lambda: label_status.config(
            text="Please scan your RFID card again", fg=TEXT_COLOR
        ))


def on_key(event, entry, label_status, root):
    """Triggered when RFID scanner (keyboard) sends Enter key."""
    if event.keysym == "Return":
        tag = entry.get().strip()
        entry.delete(0, tk.END)
        if tag:
            threading.Thread(target=process_rfid, args=(tag, root, label_status), daemon=True).start()


def exit_fullscreen(event, root):
    """Allow admin to exit fullscreen with ESC key."""
    root.attributes("-fullscreen", False)
    root.destroy()


def enforce_fullscreen(root):
    """Force fullscreen after window is rendered (fix for Raspberry Pi GUI)."""
    root.update_idletasks()
    root.after(300, lambda: root.attributes("-fullscreen", True))


def main():
    root = tk.Tk()
    root.title("Inventory System RFID Login")
    root.configure(bg=BG_COLOR)

    # ✅ Bind ESC to exit fullscreen
    root.bind("<Escape>", lambda e: exit_fullscreen(e, root))

    # ✅ Force fullscreen after UI is ready (this is the main fix)
    enforce_fullscreen(root)

    # ======= School Header with Logo =======
    header_frame = tk.Frame(root, bg=BG_COLOR)
    header_frame.pack(pady=(60, 10))

    # 🏫 Load and display the school logo beside the name
    logo_path = "images/enverga_logo.jpg"
    try:
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((140, 140))
        logo_photo = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(header_frame, image=logo_photo, bg=BG_COLOR)
        logo_label.image = logo_photo
        logo_label.pack(side="left", padx=(10, 15))
    except Exception as e:
        print(f"⚠️ Logo could not be loaded: {e}")

    school_label = tk.Label(
        header_frame,
        text=SCHOOL_NAME,
        font=FONT_SCHOOL,
        fg=TEXT_COLOR,
        bg=BG_COLOR
    )
    school_label.pack(side="left")

    tk.Label(
        root,
        text="E-Borrow: An RFID-BASED Inventory Management System",
        font=FONT_MAIN,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=50)

    # ======= RFID Entry Box =======
    rfid_entry = tk.Entry(
        root,
        font=FONT_SUB,
        justify="center",
        width=40,
        relief="solid",
        bd=2,
        highlightthickness=0,
        fg=TEXT_COLOR,
    )
    rfid_entry.pack(pady=(10, 10))
    rfid_entry.focus_set()

    # ======= Status Label =======
    label_status = tk.Label(
        root,
        text="Please scan your RFID card",
        font=FONT_SUB,
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    label_status.pack(pady=25)

    # ✅ Bind Enter key to RFID processing
    rfid_entry.bind("<Return>", lambda e: on_key(e, rfid_entry, label_status, root))

    root.mainloop()


if __name__ == "__main__":
    main()
