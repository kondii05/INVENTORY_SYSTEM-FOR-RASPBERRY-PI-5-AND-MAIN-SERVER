import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_connection
from admin_log import log_admin_action  # make sure this is imported
import datetime


def open_archived_items(root):
    """Open the Archived Items window (fullscreen)."""
    win = tk.Toplevel(root)
    win.title("📦 Archived Items")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    # Header bar
    header = tk.Frame(win, bg="#800000")
    header.pack(fill="x")
    tk.Label(header, text="📦 Archived Items",
             font=("Arial", 26, "bold"),
             bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
    tk.Button(header, text="⬅ Back", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), command=win.destroy).pack(side="right", padx=15)

    # Search bar
    search_frame = tk.Frame(win, bg="#ecf0f1")
    search_frame.pack(fill="x", pady=10)
    tk.Label(search_frame, text="Search:", bg="#ecf0f1", font=("Arial", 14, "bold")).pack(side="left", padx=10)
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=40)
    search_entry.pack(side="left", padx=5)
    tk.Button(search_frame, text="🔍 Search", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=lambda: load_archived(search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔄 Reset", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=lambda: load_archived("")).pack(side="left", padx=5)

    # Table setup
    cols = ("id", "item_name", "category", "rfid_code", "remarks", "archived_by", "archived_at")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=25)
    for col in cols:
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col, width=180, anchor="center")
    tree.pack(fill="both", expand=True, padx=20, pady=10)
        # --- Action Buttons (Below the Table) ---
    btn_frame = tk.Frame(win, bg="#ecf0f1")
    btn_frame.pack(pady=20)

    # 🟢 Restore Button
    tk.Button(
        btn_frame, text="♻️ Restore Item", bg="#008000", fg="white",
        font=("Arial", 14, "bold"), width=20,
        command=lambda: restore_selected_item(tree, win)
    ).grid(row=0, column=0, padx=10)

    # 🔴 Permanent Delete Button
    tk.Button(
        btn_frame, text="🗑 Permanently Delete", bg="#b30000", fg="white",
        font=("Arial", 14, "bold"), width=20,
        command=lambda: permanently_delete_item(tree, win)
    ).grid(row=0, column=1, padx=10)

    # ⬅ Back Button
    tk.Button(
        btn_frame, text="⬅ Back", bg="#800000", fg="white",
        font=("Arial", 14, "bold"), width=20,
        command=win.destroy
    ).grid(row=0, column=2, padx=10)

    # Context menu (Right-Click)
    menu = tk.Menu(win, tearoff=0)
    menu.add_command(label="🟢 Restore Item", command=lambda: restore_selected_item(tree, win))
    menu.add_command(label="🗑️ Delete Permanently", command=lambda: permanently_delete_item(tree, win))


    def show_context_menu(event):
        try:
            tree.selection_set(tree.identify_row(event.y))
            menu.post(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    tree.bind("<Button-3>", show_context_menu)

    # Load archived items
    def load_archived(search_text=""):
        for row in tree.get_children():
            tree.delete(row)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, name AS item_name, category, rfid_code, remarks, archived_by, archived_at
            FROM archived_items
            ORDER BY archived_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for r in rows:
            if search_text.lower() in r["item_name"].lower() or not search_text:
                tree.insert("", "end", values=(
                    r["id"], r["item_name"], r["category"],
                    r["rfid_code"], r["remarks"], r["archived_by"],
                    r["archived_at"].strftime("%Y-%m-%d %H:%M:%S") if r["archived_at"] else "—"
                ))
                
    def restore_selected_item(tree, parent):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an archived item to restore.", parent=parent)
            return

        values = tree.item(selected[0], "values")
        archive_id = values[0]
        item_name = values[1]
        category = values[2]
        rfid = values[3]

        confirm = messagebox.askyesno(
            "Confirm Restore",
            f"Are you sure you want to restore '{item_name}' back to active inventory?",
            parent=parent
        )
        if not confirm:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            # --- RFID Duplicate Check ---
            cur.execute("SELECT rfid_code FROM archived_items WHERE id=%s", (archive_id,))
            rfid_to_restore = cur.fetchone()[0]  # Get the RFID of the item being restored

            cur.execute("SELECT COUNT(*) FROM items WHERE rfid_code=%s", (rfid_to_restore,))
            exists = cur.fetchone()[0]

            if exists > 0:
                messagebox.showwarning(
                    "Duplicate RFID Detected",
                    f"Cannot restore '{item_name}' because RFID {rfid_to_restore} already exists in active inventory.",
                    parent=parent
                )
                conn.rollback()
                return

            # Move from archived_items back to items table
            cur.execute("""
                INSERT INTO items (name, category, stock, status, image_path, rfid_code)
                SELECT name, category, 1, 'available', NULL, rfid_code
                FROM archived_items WHERE id=%s
            """, (archive_id,))
            
            # Delete from archive table
            cur.execute("DELETE FROM archived_items WHERE id=%s", (archive_id,))
            conn.commit()

            messagebox.showinfo("Restored", f"Item '{item_name}' successfully restored!", parent=parent)

            # Log admin action
            log_admin_action(
                admin_name="Admin",
                action=f"Restored archived item '{item_name}' ({category})",
                item_name=item_name
            )

            # Refresh table
            if exists > 0:
                messagebox.showwarning(
                    "Duplicate RFID Detected",
                    f"Cannot restore '{item_name}' because RFID {rfid_to_restore} already exists in active inventory.",
                    parent=parent
                )
                conn.rollback()

                # ✅ Add this refresh here too
                for row in tree.get_children():
                    tree.delete(row)
                load_archived()

                return


        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Restore failed: {e}", parent=parent)
        finally:
            cur.close()
            conn.close()
    def permanently_delete_item(tree, parent):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an archived item to delete permanently.", parent=parent)
            return

        values = tree.item(selected[0], "values")
        archive_id = values[0]
        item_name = values[1]
        category = values[2]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"⚠️ This will permanently remove '{item_name}' from the system.\nThis action cannot be undone.\n\nProceed?",
            parent=parent
        )
        if not confirm:
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM archived_items WHERE id=%s", (archive_id,))
            conn.commit()

            messagebox.showinfo("Deleted", f"Item '{item_name}' permanently deleted.", parent=parent)

            # Log admin action
            log_admin_action(
                admin_name="Admin",
                action=f"Permanently deleted archived item '{item_name}' ({category})",
                item_name=item_name
            )

            # Refresh table
            for row in tree.get_children():
                tree.delete(row)
            load_archived()


        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Delete failed: {e}", parent=parent)
        finally:
            cur.close()
            conn.close()
    # Initial load
    load_archived()
