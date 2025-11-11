import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection
from archived_items import open_archived_items


def open_archived_users(root):
    win = tk.Toplevel(root)
    win.title("Archived Users")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    tk.Label(
        win, text="📁 Archived Users & Faculty",
        font=("Arial", 28, "bold"), bg="#800000", fg="white", pady=20
    ).pack(fill="x")

    # --- Search bar ---
    search_frame = tk.Frame(win, bg="#ecf0f1")
    search_frame.pack(pady=10)

    tk.Label(search_frame, text="Search:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=5)
    search_var = tk.StringVar()
    tk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔍 Search", bg="#800000", fg="white",
              font=("Arial", 12, "bold"),
              command=lambda: load_archived(search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔄 Reset", bg="#800000", fg="white",
              font=("Arial", 12, "bold"),
              command=lambda: load_archived()).pack(side="left", padx=5)
    tk.Button(search_frame, text="📦 Archived Items", bg="#800000", fg="white",
          font=("Arial", 12, "bold"),
          command=lambda: open_archived_items(win)).pack(side="left", padx=5)
    tk.Button(search_frame, text="⬅ Back", bg="#800000", fg="white",
              font=("Arial", 12, "bold"),
              command=win.destroy).pack(side="right", padx=15)

    # --- Table ---
    frame = tk.Frame(win, bg="#ecf0f1")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = ("id", "name", "rfid_code", "role", "section", "archived_at")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
    for col in cols:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=200, anchor="center")
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # --- Context Menu (Right-click) ---
    menu = tk.Menu(tree, tearoff=0)
    menu.add_command(label="🕓 View History", command=lambda: open_selected_user_history(tree, win))
    menu.add_command(label="♻️ Restore", command=lambda: restore_selected(tree, load_archived, win))
    menu.add_command(label="❌ Delete Permanently", command=lambda: delete_archived_user(tree, load_archived, win))

    def show_menu(event):
        if tree.selection():
            menu.tk_popup(event.x_root, event.y_root)
    tree.bind("<Button-3>", show_menu)

    # --- Load Data ---
    def load_archived(search_text=""):
        for row in tree.get_children():
            tree.delete(row)
        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=win)
            return
        cur = conn.cursor(dictionary=True)
        query = "SELECT * FROM archived_users ORDER BY archived_at DESC"
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for r in rows:
            if (search_text.lower() in r["name"].lower()
                or search_text.lower() in r["role"].lower()
                or search_text.lower() in (r["section"] or "").lower()
                or search_text.lower() in r["rfid_code"].lower()
                or not search_text):
                tree.insert("", "end", values=(
                    r["id"], r["name"], r["rfid_code"], r["role"],
                    r["section"] or "", r["archived_at"]
                ))

    load_archived()
    win.bind("<Escape>", lambda e: win.destroy())


# --- Helper: open selected user's history ---
def open_selected_user_history(tree, parent_win):
    selected = tree.selection()
    if not selected:
        return
    values = tree.item(selected[0])["values"]
    _, name, rfid_code, _, _, _ = values
    open_user_history(parent_win, name, rfid_code)


# --- Helper: Restore User ---
def restore_selected(tree, refresh_func, parent_win):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a user to restore.", parent=parent_win)
        return
    values = tree.item(selected[0])["values"]
    user_id, name, rfid_code, role, section, archived_at = values

    confirm = messagebox.askyesno("Confirm Restore",
                                  f"Restore '{name}' ({role}) back to active users?",
                                  parent=parent_win)
    if not confirm:
        return

    conn = get_connection()
    if not conn:
        messagebox.showerror("DB Error", "Cannot connect to database.", parent=parent_win)
        return

    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (name, rfid_code, password, role, section)
            SELECT name, rfid_code, '', role, section
            FROM archived_users WHERE id=%s
        """, (user_id,))
        cur.execute("DELETE FROM archived_users WHERE id=%s", (user_id,))
        conn.commit()
        messagebox.showinfo("Restored", f"User '{name}' restored successfully.", parent=parent_win)
        refresh_func()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restore user: {e}", parent=parent_win)
    finally:
        cur.close()
        conn.close()


# --- Helper: Delete Permanently ---
def delete_archived_user(tree, refresh_func, parent_win):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a user to delete.", parent=parent_win)
        return
    values = tree.item(selected[0])["values"]
    user_id, name, *_ = values

    confirm = messagebox.askyesno("Confirm Delete",
                                  f"Permanently delete archived user '{name}'?",
                                  parent=parent_win)
    if not confirm:
        return

    conn = get_connection()
    if not conn:
        messagebox.showerror("DB Error", "Cannot connect to database.", parent=parent_win)
        return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM archived_users WHERE id=%s", (user_id,))
        conn.commit()
        messagebox.showinfo("Deleted", f"User '{name}' permanently deleted.", parent=parent_win)
        refresh_func()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete: {e}", parent=parent_win)
    finally:
        cur.close()
        conn.close()


# --- Helper: Show user’s transaction history ---
def open_user_history(parent_win, user_name, rfid_code):
    hist_win = tk.Toplevel(parent_win)
    hist_win.title(f"History of {user_name}")
    hist_win.geometry("1100x600")
    hist_win.configure(bg="#ecf0f1")

    tk.Label(
        hist_win,
        text=f"📜 History of {user_name}",
        font=("Arial", 20, "bold"),
        bg="#2c3e50",
        fg="white",
        pady=10
    ).pack(fill="x")

    cols = ("id", "item_name", "status", "quantity", "created_at")
    tree = ttk.Treeview(hist_win, columns=cols, show="headings", height=20)
    for col in cols:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=200, anchor="center")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    scrollbar = ttk.Scrollbar(hist_win, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    conn = get_connection()
    if not conn:
        messagebox.showerror("DB Error", "Cannot connect to database.", parent=hist_win)
        return

    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT t.id, i.name AS item_name, t.status, t.quantity, t.created_at
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            JOIN archived_users u ON t.user_id = u.id
            WHERE u.rfid_code = %s
            ORDER BY t.created_at DESC
        """, (rfid_code,))

        rows = cur.fetchall()
        for r in rows:
            tree.insert("", "end", values=(
                r["id"],
                r["item_name"],
                r["status"],
                r["quantity"],
                r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            ))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load history: {e}", parent=hist_win)
    finally:
        cur.close()
        conn.close()

    tk.Button(
        hist_win,
        text="⬅ Close",
        bg="#800000",
        fg="white",
        font=("Arial", 12, "bold"),
        command=hist_win.destroy
    ).pack(pady=10)
