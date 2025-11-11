import os
import sys
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from db import get_connection
import serial
from admin_requests import open_admin_transactions
from archived import open_archived_users
from admin_log import log_admin_action
from archived_items import open_archived_items

def logout_and_return(win, root):
    win.destroy()       # close the dashboard window
    root.deiconify()    # ✅ show RFID window again

# ---------------- ADMIN DASHBOARD ---------------- #
def open_admin_dashboard(root, admin):
    win = tk.Toplevel(root) 
    win.title("Admin Dashboard")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    from archived import open_archived_users  # ✅ import the archive viewer

    tk.Label(win, text=f"Welcome, {admin['name']} (Admin)", font=("Arial", 28, "bold"), bg="#800000", fg="white", pady=20).pack(fill="x")

    frame = tk.Frame(win, bg="#ecf0f1")
    frame.pack(expand=True)

    btn_style = {"font": ("Arial", 22, "bold"), "width": 25, "height": 2, "relief": "flat", "bd": 0}

    # --- Buttons ---
    tk.Button(frame, text="👥 Manage Users", bg="#800000", fg="white", command=lambda: open_manage_users(win, admin), **btn_style).pack(pady=20)
    tk.Button(frame, text="📦 Manage Items", bg="#800000", fg="white", command=lambda: open_manage_items(win, admin), **btn_style).pack(pady=20)
    tk.Button(frame, text="📊 Transactions", bg="#800000", fg="white", command=lambda: open_admin_transactions(win, admin), **btn_style).pack(pady=20)
    # ✅ NEW: Archived Users Button
    tk.Button(frame, text="📁 Archives", bg="#800000",  fg="white", command=lambda: open_archived_users(win), **btn_style).pack(pady=20)

    tk.Button(frame, text="🚪 Logout", bg="#800000", fg="white", command=lambda: logout_and_return(win, root),  **btn_style).pack(pady=40)

    win.bind("<Escape>", lambda e: win.destroy())


# ---------------- MANAGE USERS ---------------- #
def open_manage_users(win, admin):
    users_win = tk.Toplevel(win)
    users_win.title("Manage Users")
    users_win.attributes("-fullscreen", True)
    users_win.configure(bg="#ecf0f1")

    tk.Label(users_win, text="User Management", font=("Arial", 20, "bold"),
             bg="#800000", fg="white").pack(fill="x", pady=0)
    search_frame = tk.Frame(users_win, bg="#ecf0f1"); search_frame.pack(pady=10)
    tk.Label(search_frame, text="Search:", font=("Arial", 14), bg="#ecf0f1").grid(row=0, column=0, padx=5)
    search_entry = tk.Entry(search_frame, font=("Arial", 14), width=40); search_entry.grid(row=0, column=1, padx=5)

    frame = tk.Frame(users_win, bg="#ecf0f1"); frame.pack(fill="both", expand=True, padx=20, pady=10)
    cols = ("id", "name", "rfid_code", "role", "section")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
    for col in cols:
        tree.heading(col, text=col.capitalize()); tree.column(col, width=200, anchor="center")
    tree.pack(fill="both", expand=True, side="left")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview); tree.configure(yscroll=scrollbar.set); scrollbar.pack(side="right", fill="y")

    def load_users(filter_text=None):
        for row in tree.get_children(): tree.delete(row)
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=users_win); return
        cursor = conn.cursor(dictionary=True)
        if filter_text:
            q = """SELECT id, name, rfid_code, role, section FROM users WHERE role IN ('user','faculty') AND (name LIKE %s OR rfid_code LIKE %s OR role LIKE %s OR section LIKE %s)"""
            like = f"%{filter_text}%"
            cursor.execute(q, (like, like, like, like))
        else:
            cursor.execute("SELECT id, name, rfid_code, role, section FROM users WHERE role IN ('user','faculty')")
        users = cursor.fetchall(); cursor.close(); conn.close()
        for u in users: tree.insert("", "end", values=(u["id"], u["name"], u["rfid_code"], u["role"], u["section"] if u["section"] else ""))

    load_users()
    def on_type(event): load_users(search_entry.get().strip() or None)
    search_entry.bind("<KeyRelease>", on_type)

    btn_frame = tk.Frame(users_win, bg="#ecf0f1"); btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="➕ Register User", bg="#800000", fg="white", font=("Arial", 14, "bold"), width=20, command=lambda: open_register_window(users_win, load_users)).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="✏️ Update User", bg="#800000", fg="white", font=("Arial", 14, "bold"), width=20, command=lambda: open_update_window(users_win, tree, load_users)).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="🗃 Add to Archive", bg="#800000", fg="white", font=("Arial", 14, "bold"), width=20, command=lambda: archive_user(tree, load_users, users_win)).grid(row=0, column=2, padx=10)
    tk.Button(btn_frame, text="🔄 Refresh", bg="#800000", fg="white", font=("Arial", 14, "bold"), width=20, command=lambda: load_users(search_entry.get().strip())).grid(row=0, column=3, padx=10)
    tk.Button(btn_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white", font=("Arial", 14, "bold"), width=20, command=users_win.destroy).grid(row=0, column=4, padx=10)
    users_win.bind("<Escape>", lambda e: users_win.destroy())


def open_register_window(parent, refresh_callback):
    reg_win = tk.Toplevel(parent); reg_win.title("Register New User"); reg_win.geometry("400x400"); reg_win.configure(bg="#800000")
    tk.Label(reg_win, text="Register New User", font=("Arial", 20, "bold"), bg="#800000", fg="white").pack(pady=15)
    frame = tk.Frame(reg_win, bg="#800000"); frame.pack(pady=10)
    tk.Label(frame, text="Name:", bg="#800000", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(frame, font=("Arial", 12)); name_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame, text="RFID Code:", bg="#800000", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    rfid_entry = tk.Entry(frame, font=("Arial", 12)); rfid_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(frame, text="Role:", bg="#800000", fg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    role_var = tk.StringVar(value="user"); tk.OptionMenu(frame, role_var, "user", "faculty").grid(row=2, column=1, padx=5, pady=5)
    tk.Label(frame, text="Section:", bg="#800000", fg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    section_entry = tk.Entry(frame, font=("Arial", 12)); section_entry.grid(row=3, column=1, padx=5, pady=5)

    def register_user():
        name = name_entry.get().strip(); rfid = rfid_entry.get().strip(); role = role_var.get(); section = section_entry.get().strip()
        
        if not name or not rfid:
            messagebox.showerror("Error", "Name and RFID Code are required.", parent=reg_win); return
        conn = get_connection()
        
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=reg_win); return
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (name, rfid_code, password, role, section) VALUES (%s, %s, '', %s, %s)", (name, rfid, role, section if section else None))
            conn.commit(); messagebox.showinfo("Success", f"User {name} ({role}) registered successfully.", parent=reg_win); refresh_callback(); reg_win.destroy()
            log_admin_action(
                admin_name="Admin",
                action=f"Registered new user '{name}' ({role})",
                item_name=None,             # Not an item — leave as None
                user_name=name              # The user being created
            )


        except Exception as e:
            messagebox.showerror("Error", f"Failed to register user: {e}", parent=reg_win)
        
        finally:
            cursor.close(); conn.close()
    tk.Button(reg_win, text="Register", bg="#510400", fg="white", font=("Arial", 14, "bold"), width=15, command=register_user).pack(pady=20)
    reg_win.bind("<Escape>", lambda e: reg_win.destroy())


def open_update_window(parent, tree, refresh_callback):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a user to update.", parent=parent); return
    values = tree.item(selected[0])["values"]; user_id, name, rfid_code, role, section = values
    upd_win = tk.Toplevel(parent); upd_win.title("Update User"); upd_win.geometry("400x400"); upd_win.configure(bg="#800000")
    tk.Label(upd_win, text="Update User", font=("Arial", 20, "bold"), bg="#800000", fg="white").pack(pady=15)
    frame = tk.Frame(upd_win, bg="#800000"); frame.pack(pady=10)
    tk.Label(frame, text="Name:", bg="#800000", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(frame, font=("Arial", 12)); name_entry.insert(0, name); name_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame, text="RFID Code:", bg="#800000", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    rfid_entry = tk.Entry(frame, font=("Arial", 12)); rfid_entry.insert(0, rfid_code); rfid_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(frame, text="Role:", bg="#800000", fg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    role_var = tk.StringVar(value=role); tk.OptionMenu(frame, role_var, "user", "faculty").grid(row=2, column=1, padx=5, pady=5)
    tk.Label(frame, text="Section:", bg="#800000", fg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    section_entry = tk.Entry(frame, font=("Arial", 12)); section_entry.insert(0, section if section else ""); section_entry.grid(row=3, column=1, padx=5, pady=5)

    def update_user():
        new_name = name_entry.get().strip(); new_rfid = rfid_entry.get().strip(); new_role = role_var.get(); new_section = section_entry.get().strip()
        
        if not new_name or not new_rfid:
            messagebox.showerror("Error", "Name and RFID Code are required.", parent=upd_win); return
        conn = get_connection()
       
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=upd_win); return
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE users SET name=%s, rfid_code=%s, role=%s, section=%s WHERE id=%s", (new_name, new_rfid, new_role, new_section if new_section else None, user_id))
            conn.commit(); messagebox.showinfo("Success", "User updated successfully.", parent=upd_win); refresh_callback(); upd_win.destroy()
            log_admin_action(
                admin_name="Admin",
                action=f"Updated user '{new_name}' ({new_role}) information",
                item_name=None,
                user_name=new_name
            )


        except Exception as e:
            messagebox.showerror("Error", f"Failed to update user: {e}", parent=upd_win)
       
        finally:
            cursor.close(); conn.close()
    tk.Button(upd_win, text="Update User", bg="#510400", fg="white", font=("Arial", 14, "bold"), width=15, command=update_user).pack(pady=20)
    upd_win.bind("<Escape>", lambda e: upd_win.destroy())


def archive_user(tree, refresh_callback, parent_win=None):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a user to archive.", parent=parent_win)
        return

    user_id, name, rfid_code, role, section = tree.item(selected[0])["values"]

    confirm = messagebox.askyesno("Confirm Archive",
                                  f"Are you sure you want to move '{name}' ({role}) to the archive?",
                                  parent=parent_win)
    if not confirm:
        return

    conn = get_connection()
    if not conn:
        messagebox.showerror("DB Error", "Cannot connect to database.", parent=parent_win)
        return

    cursor = conn.cursor()
    try:
        # Move user to archived_users table
        cursor.execute("""
            INSERT INTO archived_users (name, rfid_code, role, section, archived_at)
            SELECT name, rfid_code, role, section, NOW()
            FROM users WHERE id=%s
        """, (user_id,))
        # Remove from main table
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        messagebox.showinfo("Archived", f"'{name}' has been moved to archive successfully.", parent=parent_win)
        log_admin_action(
            admin_name="Admin",
            action=f"Archived user '{name}' ({role})",
            item_name=None,
            user_name=name
        )


        refresh_callback()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to archive user: {e}", parent=parent_win)
    finally:
        cursor.close()
        conn.close()



# ---------------- MANAGE ITEMS ---------------- #
def open_manage_items(root, admin=None):
    items_win = tk.Toplevel(root)
    items_win.title("Manage Items (Grouped View)")
    items_win.attributes("-fullscreen", True)
    items_win.configure(bg="#ecf0f1")

    # Header
    tk.Label(
        items_win,
        text="Item Management (Grouped View)",
        font=("Arial", 20, "bold"),
        bg="#800000",
        fg="white"
    ).pack(fill="x", pady=0)

    frame = tk.Frame(items_win, bg="#ecf0f1")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Treeview columns
    cols = ("item_name", "category", "stock", "reserved_count", "available", "status", "image")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
    # --- Right Click Menu ---
    menu = tk.Menu(tree, tearoff=0)
    menu.add_command(label="🗃 Archive Item", command=lambda: archive_selected_item(tree))

    def show_context_menu(event):
        try:
            tree.selection_set(tree.identify_row(event.y))
            menu.post(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    tree.bind("<Button-3>", show_context_menu)

    for col in cols:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=160, anchor="center")

    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # --- Function to load grouped items ---
    def load_items():
        for row in tree.get_children():
            tree.delete(row)

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=items_win)
            return

        cursor = conn.cursor(dictionary=True)

        # 🧾 GROUPED VIEW QUERY
        cursor.execute("""
            SELECT 
                name,
                category,
                COUNT(*) AS total_items,
                SUM(GREATEST(stock, 0)) AS stock,
                SUM(GREATEST(reserved_count, 0)) AS reserved_count,
                SUM(GREATEST(stock - reserved_count, 0)) AS available,
                MIN(image_path) AS image_path
            FROM items
            GROUP BY name, category
            ORDER BY name ASC;
        """)


        items = cursor.fetchall()
        cursor.close()
        conn.close()

        # Insert each grouped record
        for i in items:
            img_status = "🖼️ Yes" if i.get("image_path") else "❌ None"

            stock = i["stock"] or 0
            reserved = i["reserved_count"] or 0
            available = i["available"] or 0

            # ✅ Label logic for status
            if stock == 0:
                status = "unavailable"
            elif reserved >= stock:
                status = "reserved"
            elif 0 < reserved < stock:
                status = "partially_reserved"
            else:
                status = "available"

            # Insert row into tree
            tree.insert("", "end", values=(
                i["name"],
                i["category"],
                stock,
                reserved,
                available,
                status,
                img_status
            ))

    # --- Auto-refresh (every 2 seconds) ---
    def auto_refresh_items():
        load_items()
        items_win.after(5000, auto_refresh_items)

    # Initial load
    load_items()
    auto_refresh_items()


    # ----- BUTTONS -----
    btn_frame = tk.Frame(items_win, bg="#ecf0f1")
    btn_frame.pack(pady=15)

    tk.Button(btn_frame, text="➕ Add Item", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=lambda: open_add_item_window(items_win, load_items)).grid(row=0, column=0, padx=10, pady=10)

    tk.Button(btn_frame, text="✏️ Update Item", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=lambda: open_update_item_window(items_win, tree, load_items)).grid(row=0, column=1, padx=10, pady=10)

    tk.Button(btn_frame, text="❌ Delete Item", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=lambda: delete_item(tree, load_items, items_win)).grid(row=0, column=2, padx=10, pady=10)
    
    tk.Button(btn_frame, text="🔄 Refresh", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=load_items).grid(row=0, column=3, padx=10, pady=10)

    tk.Button(btn_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=items_win.destroy).grid(row=0, column=5, padx=10, pady=10)

    items_win.bind("<Escape>", lambda e: items_win.destroy())


# ---------------- ADD ITEM w/ RFID scanning on COM3 ---------------- #
def open_add_item_window(parent, refresh_callback):
    import time, threading, os, shutil
    from tkinter import ttk, filedialog, messagebox

    add_win = tk.Toplevel(parent)
    add_win.title("Add New Item (RFID Scan)")
    add_win.geometry("560x480")
    add_win.configure(bg="#800000")
    add_win.resizable(False, False)

    # ---- Title ----
    tk.Label(
        add_win, text="🧾 Add New Item", font=("Segoe UI", 22, "bold"),
        bg="#800000", fg="white"
    ).pack(pady=(20, 10))

    form_frame = tk.Frame(add_win, bg="#800000")
    form_frame.pack(padx=30, pady=10, fill="x")

    # ---- Item Name ----
    tk.Label(form_frame, text="Item Name:", font=("Segoe UI", 12), bg="#800000", fg="#dcdde1").grid(row=0, column=0, sticky="e", pady=8, padx=8)
    name_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, relief="solid", bd=1)
    name_entry.grid(row=0, column=1, sticky="w")

    # ---- Category ----
    tk.Label(form_frame, text="Category:", font=("Segoe UI", 12), bg="#800000", fg="#dcdde1").grid(row=1, column=0, sticky="e", pady=8, padx=8)
    category_box = ttk.Combobox(form_frame, values=["Electronics", "Networking", "Consumables"], width=29, font=("Segoe UI", 11))
    category_box.grid(row=1, column=1, sticky="w")

    # ---- Quantity ----
    tk.Label(form_frame, text="Quantity:", font=("Segoe UI", 12),
             bg="#800000", fg="#dcdde1").grid(row=2, column=0, sticky="e", pady=8, padx=8)
    quantity_entry = tk.Entry(form_frame, font=("Segoe UI", 12), width=28, relief="solid", bd=1)
    quantity_entry.grid(row=2, column=1, sticky="w")

    # ---- Image ----
    tk.Label(form_frame, text="Image:", font=("Segoe UI", 12),
             bg="#800000", fg="#dcdde1").grid(row=3, column=0, sticky="e", pady=8, padx=8)

    image_path_var = tk.StringVar()
    image_entry = tk.Entry(form_frame, textvariable=image_path_var,
                        font=("Segoe UI", 11), width=31, relief="solid", bd=1)
    image_entry.grid(row=3, column=1, sticky="w")



    def browse_image():
        path = filedialog.askopenfilename(
            title="Select Item Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if path:
            images_dir = "images"
            os.makedirs(images_dir, exist_ok=True)
            filename = os.path.basename(path)
            dest = os.path.join(images_dir, filename)
            try:
                shutil.copy(path, dest)
                image_path_var.set(filename)
                messagebox.showinfo("Image Added", f"'{filename}' uploaded successfully!", parent=add_win)
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy image:\n{e}", parent=add_win)

    browse_btn = tk.Button(form_frame, text="📁 Browse", font=("Segoe UI", 10, "bold"),
                           bg="#0abde3", fg="#080808", activebackground="#940b0b",
                           relief="flat", cursor="hand2", command=browse_image)
    browse_btn.grid(row=3, column=2, padx=(10, 0), pady=8)

    # ===========================
    # Start HID Scan Logic
    # ===========================
    def start_hid_scan():
        name = name_entry.get().strip()
        category = category_box.get().strip()
        qty = quantity_entry.get().strip()
        image_file = image_path_var.get().strip() or None

        if not name or not category or not qty.isdigit() or int(qty) <= 0:
            messagebox.showerror("Error", "Please provide valid Name, Category, and positive Quantity.", parent=add_win)
            return

        qty = int(qty)
        scanned = []

        # ✅ If category is consumable → only one RFID scan
        if category.lower() == "consumables":
            scan_popup = tk.Toplevel(add_win)
            scan_popup.title("Scan RFID tag (Consumable)")
            scan_popup.attributes("-topmost", True)
            scan_popup.geometry("500x300")
            scan_popup.configure(bg="#ecf0f1")

            tk.Label(scan_popup, text=f"Scanning 1 RFID for '{name}' (Consumable)", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)
            info_label = tk.Label(scan_popup, text="Focus here and scan one RFID tag...", font=("Arial", 14), bg="#ecf0f1", fg="#2c3e50")
            info_label.pack(pady=8)

            entry = tk.Entry(scan_popup, font=("Arial", 1))
            entry.pack()
            entry.focus_set()

            def on_key(event):
                if event.keysym == "Return":
                    tag = entry.get().strip()
                    entry.delete(0, tk.END)
                    if tag:
                        scanned.append(tag)
                        save_to_db()
                    else:
                        messagebox.showwarning("Warning", "No RFID detected!", parent=scan_popup)

            def save_to_db():
                conn = get_connection()
                if not conn:
                    messagebox.showerror("DB Error", "Cannot connect to database.", parent=scan_popup)
                    return
                cur = conn.cursor()
                try:
                    # ✅ Single record, stock = qty
                    cur.execute(
                        """INSERT INTO items (name, category, stock, status, image_path, rfid_code)
                           VALUES (%s, %s, %s, 'available', %s, %s)""",
                        (name, category, qty, image_file, scanned[0])
                    )
                    conn.commit()
                    # ✅ Log to admin logs
                    log_admin_action(
                        admin_name="Admin",
                        action=f"Added new consumable item '{name}' ({qty} pcs)",
                        item_name=name)
                    messagebox.showinfo("Success", f"Added consumable item '{name}' ({qty} pcs)", parent=scan_popup)

                    refresh_callback()
                    scan_popup.destroy()
                    add_win.destroy()
                except Exception as e:
                    messagebox.showerror("DB Error", str(e), parent=scan_popup)
                finally:
                    cur.close()
                    conn.close()

            entry.bind("<Return>", on_key)

        else:
            # 🧾 Non-consumable: Scan one RFID per item (with progress counter)
            scan_popup = tk.Toplevel(add_win)
            scan_popup.title("Scan RFID tags")
            scan_popup.attributes("-topmost", True)
            scan_popup.geometry("600x450")
            scan_popup.configure(bg="#ecf0f1")

            tk.Label(scan_popup, text=f"Scanning {qty} tag(s) for '{name}'", font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)
            info_label = tk.Label(scan_popup, text="Focus here and start scanning...", font=("Arial", 14), bg="#ecf0f1", fg="#2c3e50")
            info_label.pack(pady=8)

            # ✅ Progress counter label
            progress_label = tk.Label(scan_popup, text=f"Progress: 0 / {qty}", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#27ae60")
            progress_label.pack(pady=5)

            listbox = tk.Listbox(scan_popup, font=("Arial", 12), width=60, height=10)
            listbox.pack(pady=10, padx=10)

            entry = tk.Entry(scan_popup, font=("Arial", 1))
            entry.pack()
            entry.focus_set()

            def on_key(event):
                if event.keysym == "Return":
                    tag = entry.get().strip()
                    entry.delete(0, tk.END)

                    if not tag:
                        info_label.config(text="Empty scan ignored.")
                        return

                    if tag in scanned:
                        info_label.config(text=f"Duplicate tag ignored ({tag})")
                        return

                    # ✅ Valid new tag
                    scanned.append(tag)
                    listbox.insert("end", f"{len(scanned)}. {tag}")
                    progress_label.config(text=f"Progress: {len(scanned)} / {qty}")
                    info_label.config(text=f"Scanned {len(scanned)} of {qty} tags...")

                    # ✅ Stop scanning once we reach the required quantity
                    if len(scanned) >= qty:
                        entry.unbind("<Return>")           # Stop listening for more scans
                        entry.config(state="disabled")     # Disable entry field
                        info_label.config(text="Scan complete! Saving to database...")
                        progress_label.config(fg="#2980b9")
                        scan_popup.update()                # Refresh UI
                        save_to_db()                       # Save to DB
                        return  # Important: stop here

            def save_to_db():
                conn = get_connection()
                if not conn:
                    messagebox.showerror("DB Error", "Cannot connect to database.", parent=scan_popup)
                    return

                cur = conn.cursor()
                try:
                    for tag in scanned:
                        cur.execute(
                            """INSERT INTO items (name, category, stock, status, image_path, rfid_code)
                            VALUES (%s, %s, %s, 'available', %s, %s)""",
                            (name, category, 1, image_file, tag)
                        )
                    conn.commit()
                    # ✅ Log to admin logs
                    log_admin_action(
                        admin_name="Admin",
                        action=f"Added {qty} new '{name}' item(s) ({category})",
                        item_name=name
                    )
                    messagebox.showinfo("Success", f"{qty} item(s) added successfully!", parent=scan_popup)
                    
                    refresh_callback()

                    # ✅ Close windows after successful save
                    scan_popup.after(800, scan_popup.destroy)
                    add_win.after(800, add_win.destroy)

                except Exception as e:
                    messagebox.showerror("DB Error", str(e), parent=scan_popup)
                finally:
                    cur.close()
                    conn.close()

            entry.bind("<Return>", on_key)


    tk.Button(add_win, text="Start RFID Scan", bg="#ff0000", fg="white", font=("Arial", 14, "bold"), command=start_hid_scan).pack(pady=18)
    add_win.bind("<Escape>", lambda e: add_win.destroy())

def open_update_item_window(parent, tree, refresh_callback):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to update.", parent=parent); return
    values = tree.item(selected[0])["values"]; item_id = values[0]; name = values[1]; category = values[2]; quantity = values[3]; status = values[4]
    upd_win = tk.Toplevel(parent); upd_win.title("Update Item"); upd_win.geometry("500x500"); upd_win.configure(bg="#800000")
    tk.Label(upd_win, text="Update Item", font=("Arial", 20, "bold"), bg="#800000", fg="white").pack(pady=15)
    frame = tk.Frame(upd_win, bg="#800000"); frame.pack(pady=10)
    tk.Label(frame, text="Name:", bg="#800000", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    name_entry = tk.Entry(frame, font=("Arial", 12)); name_entry.insert(0, name); name_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame, text="Category:", bg="#800000", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    category_box = ttk.Combobox(frame, values=["Electronics", "Networking", "Consumables", "Tools"], width=27); category_box.set(category); category_box.grid(row=1, column=1, padx=5, pady=5)
    tk.Label(frame, text="Quantity:", bg="#800000", fg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    quantity_entry = tk.Entry(frame, font=("Arial", 12)); quantity_entry.insert(0, quantity); quantity_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Label(frame, text="Status:", bg="#800000", fg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
    status_var = tk.StringVar(value=status); status_menu = tk.OptionMenu(frame, status_var, "available", "unavailable", "reserved"); status_menu.grid(row=3, column=1, padx=5, pady=5)
    image_path_var = tk.StringVar(value=""); image_label = tk.Label(frame, textvariable=image_path_var, bg="#800000", fg="white", width=30, anchor="w"); image_label.grid(row=4, column=1, padx=5, pady=5)

    def browse_image():
        path = filedialog.askopenfilename(title="Select New Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if path:
            images_dir = "images"; os.makedirs(images_dir, exist_ok=True)
            filename = os.path.basename(path); dest = os.path.join(images_dir, filename); shutil.copy(path, dest)
            image_path_var.set(filename); messagebox.showinfo("Success", f"Image '{filename}' uploaded successfully!", parent=upd_win)
    tk.Button(frame, text="📁 Browse Image", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=browse_image).grid(row=4, column=2, padx=10)

    def update_item():
        new_name = name_entry.get().strip(); new_category = category_box.get().strip(); new_quantity = quantity_entry.get().strip(); new_status = status_var.get(); new_image = image_path_var.get().strip()
        if not new_name or not new_category or not new_quantity.isdigit():
            messagebox.showerror("Error", "Please fill out all fields correctly.", parent=upd_win); return
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=upd_win); return
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE items SET name=%s, category=%s, stock=%s, status=%s, image_path=%s WHERE id=%s", (new_name, new_category, int(new_quantity), new_status, new_image, item_id))
            log_admin_action(
            admin_name="Admin",  # or use admin["name"] if dynamic
            action=f"Updated item '{new_name}' ({new_category}) — set stock: {new_quantity}, status: {new_status}",
            item_name=new_name)
            conn.commit(); messagebox.showinfo("Success", "Item updated successfully!", parent=upd_win); refresh_callback(); upd_win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=upd_win)
        finally:
            cursor.close(); conn.close()
    tk.Button(upd_win, text="Update Item", bg="#ff0000", fg="white", font=("Arial", 14, "bold"), width=15, command=update_item).pack(pady=20)
    upd_win.bind("<Escape>", lambda e: upd_win.destroy())


def delete_item(tree, refresh_callback, items_win):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to delete.", parent=items_win)
        return

    # Get selected group name (e.g., Monitor, Router, etc.)
    values = tree.item(selected[0])["values"]
    group_name = values[0]

    # --- Create popup window ---
    popup = tk.Toplevel(items_win)
    popup.title(f"Select {group_name} to Delete")
    popup.geometry("520x420")
    popup.transient(items_win)
    popup.grab_set()
    popup.configure(bg="#f2f2f2")

    tk.Label(
        popup,
        text=f"Select specific {group_name} item to delete:",
        font=("Arial", 12, "bold"),
        bg="#f2f2f2"
    ).pack(pady=10)

    # --- Frame for treeview and scrollbar ---
    frame = tk.Frame(popup, bg="#f2f2f2")
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("id", "name", "rfid_code")
    sub_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
    for col in columns:
        sub_tree.heading(col, text=col.capitalize())
        sub_tree.column(col, width=150, anchor="center")

    # --- Vertical scrollbar ---
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=sub_tree.yview)
    sub_tree.configure(yscrollcommand=y_scroll.set)
    y_scroll.pack(side="right", fill="y")
    sub_tree.pack(fill="both", expand=True, side="left")

    # --- Load items under this group ---
    conn = get_connection()
    if not conn:
        messagebox.showerror("DB Error", "Cannot connect to database.", parent=popup)
        popup.destroy()
        return

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, rfid_code FROM items WHERE name=%s", (group_name,))
        rows = cursor.fetchall()
        for row in rows:
            sub_tree.insert("", "end", values=(row["id"], row["name"], row["rfid_code"]))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load items: {e}", parent=popup)
    finally:
        cursor.close()
        conn.close()

    # --- Delete selected item ---
    def confirm_delete_selected():
        sub_selected = sub_tree.selection()
        if not sub_selected:
            messagebox.showwarning("Warning", "Please select an item to delete.", parent=popup)
            return

        values = sub_tree.item(sub_selected[0])["values"]
        item_id = values[0]
        item_name = values[1]
        rfid_code = values[2]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{item_name}' (RFID {rfid_code})?",
            parent=popup
        )
        if not confirm:
            return

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=popup)
            return

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
            conn.commit()

            log_admin_action(
                admin_name="Admin",
                action=f"Deleted item '{item_name}' (RFID {rfid_code}, ID {item_id}) from inventory",
                item_name=item_name,
                user_name=None
            )

            messagebox.showinfo(
                "Deleted",
                f"Item '{item_name}' (RFID {rfid_code}) deleted successfully.",
                parent=popup
            )

            popup.destroy()
            refresh_callback()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {e}", parent=popup)
        finally:
            cursor.close()
            conn.close()

    # --- Buttons at bottom ---
    btn_frame = tk.Frame(popup, bg="#f2f2f2")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Delete Selected", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), width=15,
              command=confirm_delete_selected).pack(side="left", padx=10)

    tk.Button(btn_frame, text="Cancel", bg="gray", fg="white",
              font=("Arial", 12, "bold"), width=15,
              command=popup.destroy).pack(side="left", padx=10)


def archive_selected_item(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select an item to archive.")
        return

    values = tree.item(selected[0], "values")
    item_name = values[0]
    item_category = values[1]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, rfid_code, stock, status, category
        FROM items
        WHERE name = %s AND category = %s
    """, (item_name, item_category))
    items = cur.fetchall()
    cur.close()
    conn.close()

    if not items:
        messagebox.showerror("Error", f"No items found for '{item_name}'.")
        return

    popup = tk.Toplevel()
    popup.title(f"Archive {item_name}")
    popup.geometry("500x420")
    popup.configure(bg="#ecf0f1")
    popup.attributes("-topmost", True)

    tk.Label(popup, text=f"Archiving: {item_name}",
             font=("Arial", 16, "bold"), bg="#ecf0f1").pack(pady=10)

    tk.Label(popup, text="Add remarks (reason for archiving):",
             bg="#ecf0f1", font=("Arial", 12)).pack(pady=5)
    remarks_entry = tk.Text(popup, font=("Arial", 12), width=45, height=4)
    remarks_entry.pack(pady=5)

    # --- For Consumables ---
    if item_category.lower() == "consumables":
        item = items[0]
        tk.Label(popup, text=f"Current Stock: {item['stock']}",
                 bg="#ecf0f1", font=("Arial", 12)).pack()
        tk.Label(popup, text="Enter quantity to archive:",
                 bg="#ecf0f1", font=("Arial", 12)).pack(pady=5)
        qty_entry = tk.Entry(popup, font=("Arial", 12), width=10)
        qty_entry.pack(pady=5)

        def confirm_archive_consumable():
            try:
                qty = int(qty_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.", parent=popup)
                return

            if qty <= 0 or qty > item["stock"]:
                messagebox.showerror("Error", f"Quantity must be between 1 and {item['stock']}.", parent=popup)
                return

            remarks = remarks_entry.get("1.0", "end").strip()
            if not remarks:
                messagebox.showwarning("Missing Remarks", "Please provide a reason for archiving.", parent=popup)
                return

            conn = get_connection()
            cur = conn.cursor()
            try:
                # 🧾 Reduce stock
                cur.execute("UPDATE items SET stock = stock - %s WHERE id = %s", (qty, item["id"]))

                # 🗃 Insert archive record
                cur.execute("""
                    INSERT INTO archived_items (item_id, name, category, rfid_code, remarks, archived_by, archived_at)
                    VALUES (%s, %s, %s, %s, %s, 'Admin', NOW())
                """, (item["id"], item_name, item_category, item["rfid_code"], f"{remarks} (Archived {qty})"))

                conn.commit()
                messagebox.showinfo("Archived", f"Archived {qty} of '{item_name}' successfully!", parent=popup)

                from admin_log import log_admin_action
                log_admin_action(
                    admin_name="Admin",
                    action=f"Archived {qty} of '{item_name}' ({item_category})",
                    item_name=item_name
                )

                popup.destroy()
                tree.event_generate("<<RefreshRequested>>")  # 🔄 Trigger refresh

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Archiving failed: {e}", parent=popup)
            finally:
                cur.close()
                conn.close()

        tk.Button(popup, text="🗃 Archive", bg="#800000", fg="white",
                  font=("Arial", 12, "bold"), command=confirm_archive_consumable).pack(pady=10)
        tk.Button(popup, text="Cancel", bg="gray", fg="white",
                  font=("Arial", 12, "bold"), command=popup.destroy).pack()

    # --- For Non-Consumables ---
    else:
        tk.Label(popup, text="Select which item to archive:",
                 font=("Arial", 12, "bold"), bg="#ecf0f1").pack(pady=5)
        listbox = tk.Listbox(popup, font=("Arial", 12), width=50, height=10)
        listbox.pack(padx=10, pady=10)

        for i in items:
            listbox.insert("end", f"ID {i['id']} | RFID: {i['rfid_code']} | Status: {i['status']}")

        def confirm_archive_nonconsumable():
            selected_index = listbox.curselection()
            if not selected_index:
                messagebox.showwarning("No Selection", "Please select an item to archive.", parent=popup)
                return

            remarks = remarks_entry.get("1.0", "end").strip()
            if not remarks:
                messagebox.showwarning("Missing Remarks", "Please provide a reason for archiving.", parent=popup)
                return

            selected_item = items[selected_index[0]]
            item_id = selected_item["id"]
            rfid_code = selected_item["rfid_code"]

            conn = get_connection()
            cur = conn.cursor()
            try:
                # 🗃 Insert into archived_items first (safe copy)
                cur.execute("""
                    INSERT INTO archived_items (item_id, name, category, rfid_code, remarks, archived_by, archived_at)
                    SELECT id, name, category, rfid_code, %s, 'Admin', NOW()
                    FROM items WHERE id = %s
                """, (remarks, item_id))

                # 🧹 Then remove it from items table (moved to archive)
                cur.execute("DELETE FROM items WHERE id = %s", (item_id,))

                conn.commit()
                messagebox.showinfo("Archived", f"'{item_name}' ({rfid_code}) moved to archive successfully!", parent=popup)

                from admin_log import log_admin_action
                log_admin_action(
                    admin_name="Admin",
                    action=f"Archived '{item_name}' ({item_category}) — RFID {rfid_code}",
                    item_name=item_name
                )

                popup.destroy()
                tree.event_generate("<<RefreshRequested>>")  # 🔄 Trigger refresh

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Archiving failed: {e}", parent=popup)
            finally:
                cur.close()
                conn.close()

        tk.Button(popup, text="🗃 Archive", bg="#800000", fg="white",
                  font=("Arial", 12, "bold"), command=confirm_archive_nonconsumable).pack(pady=10)
        tk.Button(popup, text="Cancel", bg="gray", fg="white",
                  font=("Arial", 12, "bold"), command=popup.destroy).pack()
