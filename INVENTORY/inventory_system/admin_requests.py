import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
from db import get_connection
import csv
from admin_log import log_admin_action


def auto_expire_reservations():
    """Mark old pending/reserved reservations as expired automatically."""
    import datetime
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.date.today()
    try:
        cur.execute("""
            UPDATE transactions
            SET status = 'expired', updated_at = NOW()
            WHERE type = 'reserve'
              AND status IN ('pending', 'reserved')
              AND reserve_date < %s
        """, (today,))
        conn.commit()
    except Exception as e:
        print(f"[Auto-Expire] Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def open_admin_transactions(root, admin=None):
    win = tk.Toplevel(root)
    win.title("Transactions")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    # HEADER
    header = tk.Frame(win, bg="#800000")
    header.pack(fill="x")
    tk.Label(header, text="📊 Transactions", font=("Arial", 28, "bold"),
             bg="#800000", fg="white", pady=15).pack(side="left", padx=25)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Tabs
    requests_frame = tk.Frame(notebook, bg="#ecf0f1")
    for_release_frame = tk.Frame(notebook, bg="#ecf0f1")
    for_return_frame = tk.Frame(notebook, bg="#ecf0f1")
    history_frame = tk.Frame(notebook, bg="#ecf0f1")
    admin_log_frame = tk.Frame(notebook, bg="#ecf0f1")

    notebook.add(requests_frame, text="Requests")
    notebook.add(for_release_frame, text="For Release")
    notebook.add(for_return_frame, text="For Return")
    notebook.add(history_frame, text="History")
    notebook.add(admin_log_frame, text="Admin Logs")

    

def open_admin_transactions(root, admin=None):
    win = tk.Toplevel(root)
    win.title("Transactions")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    # HEADER
    header = tk.Frame(win, bg="#800000")
    header.pack(fill="x")
    tk.Label(header, text="📊 Transactions", font=("Arial", 28, "bold"),
             bg="#800000", fg="white", pady=15).pack(side="left", padx=25)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Tabs
    requests_frame = tk.Frame(notebook, bg="#ecf0f1")
    for_release_frame = tk.Frame(notebook, bg="#ecf0f1")
    for_return_frame = tk.Frame(notebook, bg="#ecf0f1")
    history_frame = tk.Frame(notebook, bg="#ecf0f1")
    admin_log_frame = tk.Frame(notebook, bg="#ecf0f1")

    notebook.add(requests_frame, text="Requests")
    notebook.add(for_release_frame, text="For Release")
    notebook.add(for_return_frame, text="For Return")
    notebook.add(history_frame, text="History")
    notebook.add(admin_log_frame, text="Admin Logs")

    # =======================================================
    #                    ADMIN LOGS TAB
    # =======================================================
    def load_admin_logs_ui():
        # Import inside the function to avoid circular references
        from db import get_connection
        import csv
        from tkinter import filedialog

        # Clear existing widgets
        for widget in admin_log_frame.winfo_children():
            widget.destroy()

        # =============================
        #  TITLE (Centered Header)
        # =============================
        title_frame = tk.Frame(admin_log_frame, bg="#ecf0f1")
        title_frame.pack(fill="x", pady=(15, 5))

        tk.Label(
            title_frame,
            text="🧾 Admin Activity Logs",
            font=("Arial", 24, "bold"),
            bg="#ecf0f1",
            fg="#000000"
        ).pack(anchor="center")

        # =============================
        #  SEARCH / CONTROL BAR
        # =============================
        search_frame = tk.Frame(admin_log_frame, bg="#ecf0f1")
        search_frame.pack(fill="x", pady=10)

        # Search field and controls
        tk.Label(search_frame, text="Search:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=(20, 5))
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, font=("Arial", 14), width=35).pack(side="left", padx=5)

        tk.Button(
            search_frame, text="🔍 Search", bg="#800000", fg="white",
            font=("Arial", 12, "bold"),
            command=lambda: load_logs(search_var.get().strip())
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame, text="🔄 Reset", bg="#800000", fg="white",
            font=("Arial", 12, "bold"),
            command=lambda: load_logs("")
        ).pack(side="left", padx=5)

        tk.Button(
            search_frame, text="📤 Export CSV", bg="#800000", fg="white",
            font=("Arial", 12, "bold"),
            command=lambda: export_to_csv()
        ).pack(side="left", padx=5)

        # Back to Dashboard Button (right-aligned)
        tk.Button(
            search_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
            font=("Arial", 12, "bold"), command=win.destroy
        ).pack(side="right", padx=15)

        # =============================
        #  TABLE VIEW
        # =============================
        cols = ("Admin", "Action", "Item", "User", "Timestamp")
        tree = ttk.Treeview(admin_log_frame, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=220, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # =============================
        #  FUNCTIONS
        # =============================
        def load_logs(search_text=""):
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            st = search_text.lower().strip()
            for r in rows:
                if not st or any(st in str(v).lower() for v in r.values()):
                    tree.insert(
                        "",
                        "end",
                        values=(r["admin_name"], r["action"], r["item_name"], r["user_name"], r["timestamp"])
                    )

        def export_to_csv():
            admin_log_frame.grab_release()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save Admin Logs As"
            )
            admin_log_frame.grab_set()
            if not file_path:
                return
            rows = [tree.item(i)["values"] for i in tree.get_children()]
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Logs saved to:\n{file_path}")
        # Initial Load
        load_logs()

    def on_tab_change(event):
        current_tab = notebook.tab(notebook.select(), "text")
        if current_tab == "Admin Logs":
            # Start refreshing when Admin Logs tab is active
            load_admin_logs_ui()

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)


    load_admin_logs_ui()

    # =========================================================
    # ---------------- REQUESTS TAB --------------------------- #
    # =========================================================
    search_frame = tk.Frame(requests_frame, bg="#ecf0f1")
    search_frame.pack(fill="x", pady=10)

    tk.Label(search_frame, text="", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=5)
    req_search_var = tk.StringVar()
    tk.Entry(search_frame, textvariable=req_search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔍 Search", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_requests(req_search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(search_frame, text="🔄 Reset", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_requests()).pack(side="left", padx=5)
    tk.Button(search_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=win.destroy).pack(side="right", padx=15)
    tk.Label(requests_frame, text="Users with Pending Requests",
             font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#000000").pack(pady=10)

    req_cols = ("name", "role", "pending_count", "latest_request")
    req_tree = ttk.Treeview(requests_frame, columns=req_cols, show="headings", height=20)
    for col in req_cols:
        req_tree.heading(col, text=col.replace("_", " ").title())
        req_tree.column(col, width=250, anchor="center")
    req_tree.pack(fill="both", expand=True, padx=20, pady=10)

    def load_requests(search_text=""):
        for row in req_tree.get_children():
            req_tree.delete(row)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT u.id AS user_id, u.name, u.role,
                   COUNT(t.id) AS pending_count,
                   MAX(t.created_at) AS latest_request
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            WHERE t.status = 'pending'
            GROUP BY u.id, u.name, u.role
            ORDER BY latest_request DESC
        """)
        for r in cur.fetchall():
            if search_text.lower() in r["name"].lower() or not search_text:
                # set iid to user id for easier lookup on click
                req_tree.insert("", "end", iid=str(r["user_id"]),
                                values=(r["name"], r["role"], r["pending_count"], r["latest_request"]))
        cur.close()
        conn.close()

    def show_user_requests(user_id, name, role):
        popup = tk.Toplevel(win)
        popup.title(f"{name}'s Requests")
        popup.attributes("-fullscreen", True)
        popup.configure(bg="#ecf0f1")

        header = tk.Frame(popup, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text=f"📦 Requests of {name} ({role.title()})",
                 font=("Arial", 26, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Back", bg="#800000", fg="white",
                  font=("Arial", 14, "bold"), command=popup.destroy).pack(side="right", padx=15)

        columns = ("item_id", "item_name", "category", "quantity", "type", "created_at")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=25)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=200, anchor="center")

        tree.pack(fill="both", expand=True, pady=10)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT t.id AS trans_id, i.id AS item_id, i.name AS item_name, 
                i.category, t.quantity, t.type, t.created_at
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.user_id=%s AND t.status='pending'
            ORDER BY t.created_at DESC
        """, (user_id,))


        rows = cur.fetchall()
        cur.close()
        conn.close()

        # insert each transaction using its transaction id as the tree iid
        for r in rows:
            tree.insert("", "end", iid=str(r["trans_id"]),
            values=(r["item_id"], r["item_name"], r["category"], r["quantity"], r["type"], r["created_at"]))


        def approve_or_reject(action):
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select at least one item.")
                return

            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            try:
                for sel in selected:
                    trans_id = sel  # ✅ Treeview iid now stores the transaction ID
                    cur.execute("SELECT item_id, type FROM transactions WHERE id=%s", (trans_id,))
                    result = cur.fetchone()

                    if not result:
                        messagebox.showwarning("Not Found", f"No transaction found for ID {trans_id}.")
                        continue

                    item_id = result["item_id"]
                    req_type = result["type"]

                    # ✅ Determine new status
                    if action == "approved":
                        new_status = "return_approved" if req_type == "return" else "approved"
                    else:
                        new_status = "return_rejected" if req_type == "return" else "rejected"

                    # ✅ Update transaction record
                    cur.execute("UPDATE transactions SET status=%s WHERE id=%s", (new_status, trans_id))

                    # ✅ Handle item updates if approved
                    if action == "approved":
                        if req_type == "borrow":
                            cur.execute("SELECT category, stock FROM items WHERE id=%s", (item_id,))
                            item = cur.fetchone()
                            if item:
                                if item["category"].lower() == "consumables":
                                    # 🔸 Reduce stock for consumables
                                    new_stock = max(0, item["stock"] - 1)
                                    new_status_item = 'available' if new_stock > 0 else 'unavailable'
                                    cur.execute("UPDATE items SET stock=%s, status=%s WHERE id=%s",
                                                (new_stock, new_status_item, item_id))
                                else:
                                    # 🔸 Reserve specific equipment
                                    cur.execute("UPDATE items SET status='reserved' WHERE id=%s", (item_id,))
                        elif req_type == "return":
                            cur.execute("UPDATE items SET status='available' WHERE id=%s", (item_id,))

                conn.commit()
                messagebox.showinfo("Success", f"Items successfully {action}!", parent=popup)
                log_admin_action(
                                admin_name="Admin",
                                action=f"{action.title()} {req_type} request",
                                item_name=result.get("item_name", "Unknown") if 'item_name' in result else None,
                                user_name=name if 'name' in locals() else None
                            )



                load_requests()  # ✅ Refresh the requests list

                # ✅ After pressing OK, refresh this same popup table
                def refresh_user_table():
                    # Remove all rows from current view
                    for row in tree.get_children():
                        tree.delete(row)

                    conn2 = get_connection()
                    cur2 = conn2.cursor(dictionary=True)
                    cur2.execute("""
                        SELECT t.id, i.name AS item_name, i.category, t.quantity, t.type, t.created_at
                        FROM transactions t
                        JOIN items i ON t.item_id = i.id
                        WHERE t.user_id=%s AND t.status='pending'
                        ORDER BY t.created_at DESC
                    """, (user_id,))
                    rows = cur2.fetchall()
                    cur2.close()
                    conn2.close()

                    for r in rows:
                        tree.insert("", "end", iid=str(r["id"]),
                                    values=(r["item_name"], r["category"], r["quantity"], r["type"], r["created_at"]))

                    # Also refresh admin lists (silently)
                    win.after(150, lambda: (load_requests(), load_for_release(), load_for_return(), load_history()))

                # ✅ Schedule the refresh right after the popup closes
                popup.after(100, refresh_user_table)

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Failed to {action} items: {e}", parent=popup)
            finally:
                cur.close()
                conn.close()



        bottom = tk.Frame(popup, bg="#ecf0f1")
        bottom.pack(pady=20)
        tk.Button(bottom, text="✅ Approve Selected", bg="#800000", fg="white",
                  font=("Arial", 16, "bold"), width=20,
                  command=lambda: approve_or_reject("approved")).pack(side="left", padx=60)
        tk.Button(bottom, text="❌ Reject Selected", bg="#800000", fg="white",
                  font=("Arial", 16, "bold"), width=20,
                  command=lambda: approve_or_reject("rejected")).pack(side="left", padx=60)

    def on_request_click(event):
        item_id = req_tree.identify_row(event.y)
        if not item_id:
            return
        values = req_tree.item(item_id, "values")
        if values:
            # we stored user id in iid already; use it instead of querying by name
            try:
                user_id = int(item_id)
            except ValueError:
                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id FROM users WHERE name=%s", (values[0],))
                user = cur.fetchone()
                cur.close()
                conn.close()
                if user:
                    user_id = user["id"]
                else:
                    return
            name, role = values[0], values[1]
            show_user_requests(user_id, name, role)

    req_tree.bind("<Double-1>", on_request_click)

    def auto_refresh_requests():
        """Automatically refresh the Requests table every 5 seconds."""
        load_requests()
        win.after(5000, auto_refresh_requests)
    auto_refresh_requests()


    # =========================================================
    # ---------------- FOR RELEASE TAB ------------------------ #
    # =========================================================
    release_search_frame = tk.Frame(for_release_frame, bg="#ecf0f1")
    release_search_frame.pack(fill="x", pady=10)

    release_search_var = tk.StringVar()
    tk.Entry(release_search_frame, textvariable=release_search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)
    tk.Button(release_search_frame, text="🔍 Search", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_for_release(release_search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(release_search_frame, text="🔄 Reset", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_for_release()).pack(side="left", padx=5)
    tk.Button(release_search_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=win.destroy).pack(side="right", padx=15)
    tk.Label(for_release_frame, text="Users with Approved (Pending Release) Items",
             font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#000000").pack(pady=10)

    release_cols = ("name", "role", "approved_count", "latest_approval")
    release_tree = ttk.Treeview(for_release_frame, columns=release_cols, show="headings", height=20)
    for col in release_cols:
        release_tree.heading(col, text=col.replace("_", " ").title())
        release_tree.column(col, width=250, anchor="center")
    release_tree.pack(fill="both", expand=True, padx=20, pady=10)

    def load_for_release(search_text=""):
        # Clear current list
        for row in release_tree.get_children():
            release_tree.delete(row)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            # ✅ Show only approved (not yet released) transactions
            cur.execute("""
                SELECT u.id AS user_id, u.name, u.role,
                       COUNT(t.id) AS approved_count,
                       MAX(t.created_at) AS latest_approval
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE t.status = 'approved'
                GROUP BY u.id, u.name, u.role
                ORDER BY latest_approval DESC
            """)
            rows = cur.fetchall()

            for r in rows:
                if search_text.lower() in r["name"].lower() or \
                search_text.lower() in r["role"].lower() or \
                search_text == "":
                    release_tree.insert(
                        "", "end", iid=str(r["user_id"]),
                        values=(r["name"], r["role"], r["approved_count"], r["latest_approval"])
                    )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load release list: {e}")
        finally:
            cur.close()
            conn.close()


    def auto_refresh_release():
        load_for_release(release_search_var.get().strip())
        win.after(5000, auto_refresh_release)
    auto_refresh_release()

    def show_user_for_release(user_id, name, role):
        popup = tk.Toplevel(win)
        popup.title(f"{name}'s Pending Releases")
        popup.attributes("-fullscreen", True)
        popup.configure(bg="#ecf0f1")

        header = tk.Frame(popup, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text=f"🔓 Pending Releases of {name} ({role.title()})",
                 font=("Arial", 26, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Close", bg="#800000", fg="white",
                  font=("Arial", 14, "bold"), command=popup.destroy).pack(side="right", padx=15)
        
        filter_frame = tk.Frame(popup, bg="#ecf0f1")
        filter_frame.pack(fill="x", pady=10)
        tk.Label(filter_frame, text="🔍 Search:", bg="#ecf0f1", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 14), width=30)
        search_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Apply Filter", bg="#800000", fg="white",
                font=("Arial", 12, "bold"), command=lambda: load_filtered(search_var.get().strip())).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Reset", bg="#800000", fg="white",
                font=("Arial", 12, "bold"), command=lambda: load_filtered("")).pack(side="left", padx=5)

        columns = ("item_id", "item_name", "quantity", "type", "status", "created_at")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=25)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=220, anchor="center")
        tree.pack(fill="both", expand=True, pady=10)
        
        def load_filtered(search_text=""):
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT t.id AS trans_id, i.id AS item_id, i.name AS item_name,
                t.quantity, t.type, t.status, t.created_at
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.user_id=%s AND t.status='approved'
                ORDER BY t.created_at DESC
            """, (user_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                if (search_text.lower() in r["item_name"].lower() or
                    search_text.lower() in r["type"].lower() or
                    search_text.lower() in r["status"].lower() or
                    search_text == ""):
                    tree.insert("", "end", iid=str(r["trans_id"]),
                    values=(r["item_id"], r["item_name"], r["quantity"], r["type"], r["status"], r["created_at"]))
        # Initial load
        load_filtered()

        def scan_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select an item first.", parent=popup)
                return

            sel = selected[0]
            trans_id = int(sel)  # ✅ Treeview iid = transaction ID
            values = tree.item(sel, "values")

            item_id = int(values[0])   # First column = item_id
            item_name = values[1]
            quantity = int(values[2])
            type_ = values[3]
            status = values[4]

            if status.lower() != "approved":
                messagebox.showwarning("Invalid", "This item is not ready for release.", parent=popup)
                return

            scan_popup = tk.Toplevel(popup)
            scan_popup.title("Scan RFID to Release")
            scan_popup.geometry("500x400")
            scan_popup.configure(bg="#ecf0f1")
            scan_popup.attributes("-topmost", True)

            tk.Label(scan_popup, text=f"Releasing {quantity} × {item_name}",
                     font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=15)
            tk.Label(scan_popup, text="Scan RFID tag for this item...",
                     font=("Arial", 14), bg="#ecf0f1").pack(pady=10)
            listbox = tk.Listbox(scan_popup, font=("Arial", 12), width=50, height=10)
            listbox.pack(pady=10)
            entry = tk.Entry(scan_popup)
            entry.pack()
            entry.focus_set()

            def on_key(event):
                if event.keysym != "Return":
                    return
                tag = entry.get().strip()
                entry.delete(0, tk.END)
                if not tag:
                    return

                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                try:
                    # ✅ Find the item by RFID and ID
                    cur.execute("""
                        SELECT id, name, category, stock, rfid_code, status
                        FROM items
                        WHERE rfid_code = %s AND id = %s
                    """, (tag, item_id))
                    item = cur.fetchone()

                    if not item:
                        messagebox.showerror("Invalid RFID", f"❌ Tag {tag} does not match this item.", parent=scan_popup)
                        return

                    # ✅ Equipment → just mark borrowed
                    if item["category"].lower() != "consumables":
                        cur.execute("UPDATE items SET status='borrowed' WHERE id=%s", (item_id,))
                        cur.execute("""
                            UPDATE transactions
                            SET status='released', release_time=NOW(), updated_at=NOW()
                            WHERE id=%s
                        """, (trans_id,))
                        conn.commit()
                        listbox.insert("end", f"✅ Released {quantity} × {item_name} (RFID: {tag})")
                        messagebox.showinfo("Released", f"Released {quantity} × {item_name}.", parent=scan_popup)
                        log_admin_action(
                            admin_name="Admin",
                            action=f"Released {quantity} × '{item_name}' via RFID (Tag: {tag})",
                            item_name=item_name,
                            user_name=name
                        )
                        # ✅ Remove the released item immediately from the current popup list
                        tree.delete(sel)

                        # ✅ Refresh both the popup and main For Release lists
                        popup.after(100, load_filtered)
                        popup.after(150, load_for_release)

                        scan_popup.destroy()
                        return


                    # ✅ Consumables → one RFID scan, then reduce stock
                    if item["category"].lower() == "consumables":
                        new_stock = max(0, item["stock"] - quantity)
                        new_status_item = 'available' if new_stock > 0 else 'unavailable'
                        cur.execute("""
                            UPDATE items
                            SET stock=%s, status=%s
                            WHERE id=%s
                        """, (new_stock, new_status_item, item_id))
                        cur.execute("""
                            UPDATE transactions
                            SET status='released', release_time=NOW(), updated_at=NOW()
                            WHERE id=%s
                        """, (trans_id,))
                        conn.commit()
                        listbox.insert("end", f"✅ Released (1 RFID: {tag}) - {quantity} × {item_name}")
                        messagebox.showinfo("Released", f"Released {quantity} × {item_name}.", parent=scan_popup)

                        # ✅ Use the actual variables available in this scope and a fallback admin name
                        _admin_name = globals().get("ADMIN_NAME", "Admin")  # change this if you have an admin variable

                        # ✅ Log the release action for consumables
                        log_admin_action(
                            _admin_name,
                            f"Released (consumable) {quantity} × '{item_name}' via RFID (Tag: {tag})",
                            item_name=item_name,
                            user_name=name
                        )

                        # ✅ Remove the released item immediately from the current popup list
                        tree.delete(sel)

                        # ✅ Refresh both the popup and main For Release lists
                        popup.after(100, load_filtered)
                        popup.after(150, load_for_release)

                        scan_popup.destroy()
                        return


                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"RFID scan failed: {e}", parent=scan_popup)
                finally:
                    cur.close()
                    conn.close()

            entry.bind("<Return>", on_key)

            tk.Button(scan_popup, text="Close", bg="#800000", fg="white",
                      font=("Arial", 12, "bold"), command=scan_popup.destroy).pack(pady=10)
        tk.Button(popup, text="🔓 Scan RFID to Release Selected",bg="#800000", fg="white", 
                font=("Arial", 14, "bold"), command=scan_selected).pack(pady=20)



    def on_release_click(event):
        item_id = release_tree.identify_row(event.y)
        if not item_id:
            return
        values = release_tree.item(item_id, "values")
        if values:
            try:
                user_id = int(item_id)
            except ValueError:
                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id FROM users WHERE name=%s", (values[0],))
                user = cur.fetchone()
                cur.close()
                conn.close()
                if user:
                    user_id = user["id"]
                else:
                    return
            name, role = values[0], values[1]
            show_user_for_release(user_id, name, role)

    release_tree.bind("<Double-1>", on_release_click)


    # =========================================================
    # ---------------- FOR RETURN TAB ------------------------ #
    # =========================================================
    return_search_frame = tk.Frame(for_return_frame, bg="#ecf0f1")
    return_search_frame.pack(fill="x", pady=10)

    return_search_var = tk.StringVar()
    tk.Entry(return_search_frame, textvariable=return_search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)
    tk.Button(return_search_frame, text="🔍 Search", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_for_return(return_search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(return_search_frame, text="🔄 Reset", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_for_return()).pack(side="left", padx=5)
    tk.Button(return_search_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=win.destroy).pack(side="right", padx=15)
    tk.Label(for_return_frame, text="Users with Approved (Pending Return) Items",
             font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#000000").pack(pady=10)
    
    return_cols = ("name", "role", "approved_count", "latest_approval")
    return_tree = ttk.Treeview(for_return_frame, columns=return_cols, show="headings", height=20)
    for col in return_cols:
        return_tree.heading(col, text=col.replace("_", " ").title())
        return_tree.column(col, width=250, anchor="center")
    return_tree.pack(fill="both", expand=True, padx=20, pady=10)

    def load_for_return(search_text=""):
        for row in return_tree.get_children():
            return_tree.delete(row)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                u.id AS user_id, 
                u.name, 
                u.role,
                COUNT(t.id) AS return_count,
                MAX(t.updated_at) AS latest_update
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            JOIN items i ON t.item_id = i.id
            WHERE t.status = 'return_approved'
            AND i.category != 'consumables'
            GROUP BY u.id, u.name, u.role
            ORDER BY latest_update DESC
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        for r in rows:
            if search_text.lower() in r["name"].lower() or not search_text:
                return_tree.insert(
                    "",
                    "end",
                    iid=str(r["user_id"]),
                    values=(r["name"], r["role"], r["return_count"], r["latest_update"])
                )


    def auto_refresh_return():
        load_for_return(return_search_var.get().strip())
        win.after(5000, auto_refresh_return)  # refresh every 5 seconds
    auto_refresh_return()


    def show_user_for_return(user_id, name, role):
        popup = tk.Toplevel(win)
        popup.title(f"{name}'s Pending Returns")
        popup.attributes("-fullscreen", True)
        popup.configure(bg="#ecf0f1")

        header = tk.Frame(popup, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text=f"🔁 Pending Returns of {name} ({role.title()})",
                 font=("Arial", 26, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Close", bg="#800000", fg="white",
                  font=("Arial", 14, "bold"), command=popup.destroy).pack(side="right", padx=15)

        # ✅ FILTER BAR
        filter_frame = tk.Frame(popup, bg="#ecf0f1")
        filter_frame.pack(fill="x", pady=10)
        tk.Label(filter_frame, text="🔍 Search:", bg="#ecf0f1", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 14), width=30)
        search_entry.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Apply Filter", bg="#800000", fg="white",
                font=("Arial", 12, "bold"), command=lambda: load_filtered(search_var.get().strip())).pack(side="left", padx=5)
        tk.Button(filter_frame, text="Reset", bg="#800000", fg="white",
                font=("Arial", 12, "bold"), command=lambda: load_filtered("")).pack(side="left", padx=5)

        # Table
        columns = ("item_id", "item_name", "quantity", "type", "status", "created_at")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=25)
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=220, anchor="center")
        tree.pack(fill="both", expand=True, pady=10)


        def load_filtered(search_text=""):
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT 
                    t.id AS trans_id,
                    i.id AS item_id,
                    i.name AS item_name,
                    t.quantity,
                    t.type,
                    t.status,
                    t.created_at
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.user_id=%s AND t.status IN ('return_approved')
                ORDER BY t.created_at DESC
            """, (user_id,))

            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                if (search_text.lower() in str(r["item_id"]).lower() or
                    search_text.lower() in r["item_name"].lower() or
                    search_text.lower() in r["type"].lower() or
                    search_text.lower() in r["status"].lower() or
                    search_text == ""):

                    tree.insert(
                        "",
                        "end",
                        iid=str(r["trans_id"]),
                        values=(r["item_id"], r["item_name"], r["quantity"], r["type"], r["status"], r["created_at"])
                    )


        # Initial load
        load_filtered()
        
        def scan_returned():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select an item first.", parent=popup)
                return

            sel = selected[0]
            trans_id = int(sel)
            values = tree.item(sel, "values")
            item_id = int(values[0])
            item_name = values[1]

            scan_popup = tk.Toplevel(popup)
            scan_popup.title("Scan RFID to Return")
            scan_popup.geometry("500x400")
            scan_popup.configure(bg="#ecf0f1")
            scan_popup.attributes("-topmost", True)

            tk.Label(scan_popup, text=f"Returning {item_name}",
                    font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=15)
            tk.Label(scan_popup, text="Scan the RFID tag of this item...",
                    font=("Arial", 14), bg="#ecf0f1").pack(pady=10)
            entry = tk.Entry(scan_popup)
            entry.pack()
            entry.focus_set()

            def on_key(event):
                if event.keysym != "Return":
                    return
                tag = entry.get().strip()
                entry.delete(0, tk.END)
                if not tag:
                    return

                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                try:
                    cur.execute("""
                        SELECT id, name, rfid_code
                        FROM items
                        WHERE id = %s AND rfid_code = %s
                    """, (item_id, tag))
                    item = cur.fetchone()

                    if not item:
                        messagebox.showerror("Invalid RFID",
                                            f"❌ Tag {tag} does not match this item.",
                                            parent=scan_popup)
                        return

                    # ✅ Update both tables
                    cur.execute("UPDATE items SET status='available' WHERE id=%s", (item_id,))
                    cur.execute("""
                        UPDATE transactions
                        SET status='returned', return_time=NOW(), updated_at=NOW()
                        WHERE id=%s
                    """, (trans_id,))
                    conn.commit()

                    messagebox.showinfo("Returned", f"{item_name} has been returned successfully!", parent=scan_popup)
                    log_admin_action(
                                admin_name="Admin",
                                action=f"Confirmed return of '{item_name}' via RFID (Tag: {tag})",
                                item_name=item_name,
                                user_name=name
                            )

                    # ✅ Remove immediately and refresh lists
                    tree.delete(sel)
                    popup.after(100, load_filtered)
                    popup.after(150, lambda: popup.destroy() if not tree.get_children() else None)

                    scan_popup.destroy()

                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Return failed: {e}", parent=scan_popup)
                finally:
                    cur.close()
                    conn.close()

            entry.bind("<Return>", on_key)
            tk.Button(scan_popup, text="Close", bg="#800000", fg="white",
                    font=("Arial", 12, "bold"), command=scan_popup.destroy).pack(pady=10)


        tk.Button(popup, text="🔁 Scan RFID to Confirm Return",
                  bg="#800000", fg="white", font=("Arial", 14, "bold"),
                  command=scan_returned).pack(pady=20)

    def on_return_click(event):
        item_id = return_tree.identify_row(event.y)
        if not item_id:
            return
        values = return_tree.item(item_id, "values")
        if values:
            try:
                user_id = int(item_id)
            except ValueError:
                conn = get_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id FROM users WHERE name=%s", (values[0],))
                user = cur.fetchone()
                cur.close()
                conn.close()
                if user:
                    user_id = user["id"]
                else:
                    return
            name, role = values[0], values[1]
            show_user_for_return(user_id, name, role)

    return_tree.bind("<Double-1>", on_return_click)

    def auto_refresh_return():
        load_for_return(return_search_var.get().strip())
        win.after(5000, auto_refresh_return)
    auto_refresh_return()

    # =========================================================
    # ---------------- HISTORY TAB --------------------------- #
    # =========================================================
    hist_search_frame = tk.Frame(history_frame, bg="#ecf0f1")
    hist_search_frame.pack(fill="x", pady=10)
    button_frame = tk.Frame(hist_search_frame, bg="#ecf0f1")
    button_frame.pack(side="left")

    tk.Label(hist_search_frame, text="Search:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=5)
    hist_search_var = tk.StringVar()
    tk.Entry(hist_search_frame, textvariable=hist_search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="🔍 Search", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_history(hist_search_var.get().strip())).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="🔄 Reset", bg="#800000", fg="white", font=("Arial", 12, "bold"),
              command=lambda: load_history()).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="📊 Report", bg="#800000", fg="white",
              font=("Arial", 12, "bold"),
              command=lambda: open_history_report(win, user_type="faculty")).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="📅 Calendar View", bg="#800000", fg="white",
          font=("Arial", 12, "bold"),
          command=lambda: open_calendar_view(win)).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="📦 R & R", bg="#800000", fg="white",
          font=("Arial", 12, "bold"),
          command=lambda: open_release_return_history(win)).pack(side="left", padx=5)
    tk.Button(hist_search_frame, text="⬅ Back to Dashboard", bg="#800000", fg="white",
              font=("Arial", 12, "bold"), command=win.destroy).pack(side="right", padx=15)

    hist_cols = ("User", "Role", "Total Transactions")
    hist_tree = ttk.Treeview(history_frame, columns=hist_cols, show="headings", height=20)
    for col in hist_cols:
        hist_tree.heading(col, text=col)
        hist_tree.column(col, width=250 if col == "User" else 200, anchor="center")
    hist_tree.pack(fill="both", expand=True, padx=20, pady=10)


    def load_history(search_text=""):
        auto_expire_reservations()
        for row in hist_tree.get_children():
            hist_tree.delete(row)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            # ✅ Combine both active and archived users
            # ✅ Count all types of transactions for each user
            cur.execute("""
                SELECT 
                    COALESCE(u.name, a.name) AS username,
                    COALESCE(u.role, a.role) AS role,
                    COUNT(t.id) AS total_transactions
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN archived_users a ON t.user_id = a.id
                GROUP BY username, role
                ORDER BY total_transactions DESC
            """)
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        st = (search_text or "").strip().lower()

        for r in rows:
            username = r.get("username") or "—"
            role = r.get("role") or "—"
            total = r.get("total_transactions") or 0

            if not st or st in username.lower() or st in role.lower():
                hist_tree.insert(
                    "",
                    "end",
                    values=(username, role, total)
                )
    def open_user_history(username):
        popup = tk.Toplevel(win)
        popup.title(f"{username}'s Transaction History")
        popup.attributes("-fullscreen", True)
        popup.configure(bg="#ecf0f1")

        header = tk.Frame(popup, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(header, text=f"📋 Transaction History: {username}",
                font=("Arial", 26, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Close", bg="#800000", fg="white",
                font=("Arial", 14, "bold"), command=popup.destroy).pack(side="right", padx=15)

        # Create table for user details
        columns = ("item_name", "type", "status", "quantity", "created_at", "reserve_date", "reserve_time")
        user_tree = ttk.Treeview(popup, columns=columns, show="headings", height=25)
        for col in columns:
            user_tree.heading(col, text=col.replace("_", " ").title())
            user_tree.column(col, width=200, anchor="center")
        user_tree.pack(fill="both", expand=True, pady=10)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            # ✅ Fetch all transactions for this user (borrow, reserve, return)
            cur.execute("""
                SELECT 
                    t.id,
                    i.name AS item_name,
                    t.type,
                    t.status,
                    t.quantity,
                    t.created_at,
                    t.reserve_date,
                    t.reserve_time
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN archived_users a ON t.user_id = a.id
                WHERE COALESCE(u.name, a.name) = %s
                ORDER BY t.created_at DESC
            """, (username,))
            rows = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        if not rows:
            tk.Label(popup, text="No transaction records found for this user.",
                    font=("Arial", 16), bg="#ecf0f1", fg="red").pack(pady=30)
            return

        # ✅ Insert the user's transactions into the popup table
        for r in rows:
            user_tree.insert(
                "",
                "end",
                values=(
                    r["item_name"],
                    r["type"],
                    r["status"],
                    r["quantity"],
                    r["created_at"],
                    r["reserve_date"] or "—",
                    r["reserve_time"] or "—"
                )
            )
            

# =========================================================
# ---------------- CALENDAR VIEW WINDOW ------------------- #
# =========================================================
    def open_calendar_view(root):
        import datetime
        from tkinter import ttk, StringVar
        from db import get_connection

        def load_calendar(filter_mode="Upcoming Only"):
            # Clear old rows
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cur = conn.cursor()

            base_query = """
                SELECT COALESCE(u.name, a.name) AS username,
                    i.name AS item_name,
                    t.reserve_date,
                    t.reserve_time,
                    t.status
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN archived_users a ON t.user_id = a.id
                JOIN items i ON t.item_id = i.id
                WHERE t.type='reserve'
            """

            # Apply filter based on selection
            if filter_mode == "Upcoming Only":
                base_query += """
                AND t.status IN ('reserved', 'released', 'pending')
                AND t.reserve_date >= CURDATE()
                """
            else:  # "All Reservations"
                base_query += """
                AND t.status IN ('reserved', 'released', 'pending', 'expired', 'returned', 'rejected', 'approved')
                """

            base_query += " ORDER BY t.reserve_date, t.reserve_time"

            cur.execute(base_query)
            reservations = cur.fetchall()
            cur.close()
            conn.close()

            for r in reservations:
                tree.insert("", "end", values=r)

        # --- Main Window Setup ---
        cal_win = tk.Toplevel(root)
        cal_win.title("📅 Reservation Calendar")
        cal_win.geometry("950x600")
        cal_win.configure(bg="#ecf0f1")

        today = datetime.date.today()

        # --- Header Bar ---
        header = tk.Frame(cal_win, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text=f"Reservation Calendar — {today.strftime('%B %Y')}",
                font=("Arial", 18, "bold"), bg="#800000", fg="white", pady=10).pack(side="left", padx=20)

        # --- Filter Controls ---
        filter_frame = tk.Frame(cal_win, bg="#ecf0f1")
        filter_frame.pack(fill="x", pady=10)

        tk.Label(filter_frame, text="Show:", font=("Arial", 12, "bold"), bg="#ecf0f1").pack(side="left", padx=10)
        filter_var = StringVar(value="Upcoming Only")
        filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, state="readonly",
                                values=["Upcoming Only", "All Reservations"], width=20)
        filter_menu.pack(side="left", padx=5)
        tk.Button(filter_frame, text="Apply", bg="#510400", fg="white", font=("Arial", 11, "bold"),
                command=lambda: load_calendar(filter_var.get())).pack(side="left", padx=10)

        # --- Treeview Table ---
        frame = tk.Frame(cal_win, bg="#ecf0f1")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        cols = ("Faculty", "Item", "Date", "Time", "Status")
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=170, anchor="center")
        tree.pack(fill="both", expand=True, pady=10)

        # --- Initial Load ---
        load_calendar()
    

    # ================= USER HISTORY POPUP =================
    def show_user_history(user_id, name, role):
        hist_popup = tk.Toplevel(win)
        hist_popup.title(f"{name}'s History")
        hist_popup.attributes("-fullscreen", True)
        win.focus_force()
        hist_popup.configure(bg="#ecf0f1")

        # Header
        header = tk.Frame(hist_popup, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text=f"📜 History of {name} ({role.title()})",
                 font=("Arial", 24, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Back", bg="#800000", fg="white",
                  font=("Arial", 14, "bold"), command=hist_popup.destroy).pack(side="right", padx=15)

        # Search & Filter Bar
        top_bar = tk.Frame(hist_popup, bg="#ecf0f1")
        top_bar.pack(fill="x", pady=10)

        tk.Label(top_bar, text="Search:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=10)
        search_var = tk.StringVar()
        search_entry = tk.Entry(top_bar, textvariable=search_var, font=("Arial", 14), width=30)
        search_entry.pack(side="left", padx=5)

        tk.Label(top_bar, text="Filter by:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=10)
        filter_var = tk.StringVar(value="All")
        options = ["All", "Borrowed", "Returned", "Released", "Reserved"]
        filter_menu = ttk.Combobox(top_bar, textvariable=filter_var, values=options,
                                   state="readonly", width=15)
        filter_menu.pack(side="left", padx=5)

        tk.Button(top_bar, text="🔍 Apply", bg="#800000", fg="white",
                  font=("Arial", 12, "bold"),
                  command=lambda: load_user_history(search_var.get().strip(), filter_var.get())).pack(side="left", padx=5)

        # Table
        columns = ("item_name", "category", "type", "status", "created_at")
        hist_user_tree = ttk.Treeview(hist_popup, columns=columns, show="headings", height=25)
        for col in columns:
            hist_user_tree.heading(col, text=col.replace("_", " ").title())
            hist_user_tree.column(col, width=200, anchor="center")
        hist_user_tree.pack(fill="both", expand=True, padx=20, pady=10)

        def _norm(s):
            return (s or "").strip().lower()

        def load_user_history(search_text="", filter_type="All"):
            for row in hist_user_tree.get_children():
                hist_user_tree.delete(row)
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT i.name AS item_name, i.category, t.type, t.status, t.created_at
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.user_id=%s
                ORDER BY t.created_at DESC
            """, (user_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            search_text = _norm(search_text)
            borrowed_statuses = {"borrow", "borrowed", "approved"}
            returned_statuses = {"returned", "return_approved"}
            released_statuses = {"released"}
            reserved_statuses = {"reserved"}

            for r in rows:
                item = _norm(r.get("item_name"))
                cat = _norm(r.get("category"))
                typ = _norm(r.get("type"))
                stat = _norm(r.get("status"))

                matches_search = (
                    not search_text
                    or search_text in item
                    or search_text in cat
                    or search_text in typ
                    or search_text in stat
                )

                matches_filter = (
                    filter_type == "All"
                    or (filter_type == "Borrowed" and (typ in borrowed_statuses or stat in borrowed_statuses))
                    or (filter_type == "Returned" and (typ in returned_statuses or stat in returned_statuses))
                    or (filter_type == "Released" and (typ in released_statuses or stat in released_statuses))
                    or (filter_type == "Reserved" and (typ in reserved_statuses or stat in reserved_statuses))
                )

                if matches_search and matches_filter:
                    hist_user_tree.insert("", "end", values=(
                        r["item_name"], r["category"], r["type"], r["status"], r["created_at"]
                    ))

        def auto_refresh():
            load_user_history(search_var.get().strip(), filter_var.get())
            hist_popup.after(5000, auto_refresh)

        search_entry.bind("<Return>", lambda e: load_user_history(search_var.get().strip(), filter_var.get()))
        filter_menu.bind("<<ComboboxSelected>>", lambda e: load_user_history(search_var.get().strip(), filter_var.get()))
        load_user_history()
        auto_refresh()
    def open_release_return_history(root, default_filter="All"):
        import csv
        from tkinter import filedialog

        win = tk.Toplevel(root)
        win.title("📦 Released & Returned Items History")
        win.attributes("-fullscreen", True)
        win.configure(bg="#ecf0f1")
        win.focus_force()

        # --- Header ---
        header = tk.Frame(win, bg="#800000")
        header.pack(fill="x")
        tk.Label(header, text="📦 Released & Returned Items History",
                font=("Arial", 26, "bold"), bg="#800000", fg="white", pady=15).pack(side="left", padx=20)
        tk.Button(header, text="⬅ Close", bg="#800000", fg="white",
                font=("Arial", 14, "bold"), command=win.destroy).pack(side="right", padx=15)

        # --- Search + Filter Bar ---
        filter_frame = tk.Frame(win, bg="#ecf0f1")
        filter_frame.pack(fill="x", pady=10)

        tk.Label(filter_frame, text="Search:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=10)
        search_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=search_var, font=("Arial", 14), width=40).pack(side="left", padx=5)

        tk.Label(filter_frame, text="Category:", font=("Arial", 14), bg="#ecf0f1").pack(side="left", padx=10)
        filter_var = tk.StringVar(value=default_filter)
        filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var,
                                values=["All", "Released", "Returned"], state="readonly", width=15)
        filter_menu.pack(side="left", padx=5)

        tk.Button(filter_frame, text="🔍 Search", bg="#800000", fg="white",
                font=("Arial", 12, "bold"),
                command=lambda: load_history_data(search_var.get().strip(), filter_var.get())).pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="🔄 Reset", bg="#800000", fg="white",
                font=("Arial", 12, "bold"),
                command=lambda: [search_var.set(""), filter_var.set("All"), load_history_data("", "All")]).pack(side="left", padx=5)
        
        tk.Button(filter_frame, text="📤 Export CSV", bg="#800000", fg="white",
                font=("Arial", 12, "bold"),
                command=lambda: export_to_csv()).pack(side="left", padx=5)

        tk.Button(filter_frame, text="🧾 Print Summary", bg="#800000", fg="white",
                font=("Arial", 12, "bold"),
                command=lambda: print_summary()).pack(side="left", padx=5)

        # --- Table ---
        cols = ("User", "Role", "Item Name", "Quantity", "Type", "Status", "Updated At")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=25)
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=220, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Summary Bar ---
        summary_frame = tk.Frame(win, bg="#800000")
        summary_frame.pack(fill="x")
        summary_label = tk.Label(summary_frame,
                                text="🧾 Summary: Released: 0 | Returned: 0 | Total: 0",
                                bg="#800000", fg="white", font=("Arial", 12, "bold"))
        summary_label.pack(pady=5)

        # --- Load Function ---
        def load_history_data(search_text="", category="All"):
            for row in tree.get_children():
                tree.delete(row)

            conn = get_connection()
            cur = conn.cursor(dictionary=True)

            base_query = """
                SELECT 
                    COALESCE(u.name, a.name) AS username,
                    COALESCE(u.role, a.role) AS role,
                    i.name AS item_name,
                    t.quantity,
                    t.type,
                    t.status,
                    COALESCE(t.updated_at, t.created_at) AS updated_at
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN archived_users a ON t.user_id = a.id
                JOIN items i ON t.item_id = i.id
                WHERE t.status IN ('released', 'returned')
            """

            if category == "Released":
                base_query += " AND t.status='released'"
            elif category == "Returned":
                base_query += " AND t.status='returned'"

            base_query += " ORDER BY t.updated_at DESC"
            cur.execute(base_query)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            st = (search_text or "").strip().lower()
            released_count = returned_count = 0

            for r in rows:
                username = r["username"] or "—"
                role = r["role"] or "—"
                item = r["item_name"] or "—"
                qty = r["quantity"] or 0
                typ = r["type"] or "—"
                stat = r["status"] or "—"
                updated = r["updated_at"] or "—"

                if not st or any(st in str(v).lower() for v in [username, role, item, typ, stat]):
                    tree.insert("", "end", values=(username, role, item, qty, typ, stat, updated))
                    if stat == "released":
                        released_count += 1
                    elif stat == "returned":
                        returned_count += 1

            total = released_count + returned_count
            summary_label.config(text=f"🧾 Summary: Released: {released_count} | Returned: {returned_count} | Total: {total}")

        # --- Export to CSV ---
        def export_to_csv():
            win.grab_release()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save Released & Returned History As",
                parent=win
            )
            win.grab_set()

            if not file_path:
                return

            rows = [tree.item(i)["values"] for i in tree.get_children()]
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"File saved to:\n{file_path}", parent=win)

        # --- Print Summary ---
        def print_summary():
            summary_text = summary_label.cget("text")
            messagebox.showinfo("Summary", summary_text, parent=win)

        # --- Auto-load ---
        load_history_data("", default_filter)
            # --- Auto-Refresh ---
        def auto_refresh():
            # Re-run load_history_data() using the current search + filter values
            load_history_data(search_var.get().strip(), filter_var.get())
            win.after(5000, auto_refresh)  # refresh every 5 seconds

        auto_refresh()


    def on_history_click(event):
        item_id = hist_tree.identify_row(event.y)
        if not item_id:
            return
        values = hist_tree.item(item_id, "values")
        if not values:
            return
        name, role = values[0], values[1]
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE name=%s", (name,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            show_user_history(user["id"], name, role)

    hist_tree.bind("<Double-1>", on_history_click)
    load_history()

def update_transaction_status(transaction_id, new_status, parent_win=None, refresh_func=None):
    """
    Updates a transaction status (approved, rejected, released, etc.)
    and safely adjusts item stock and reserved_count.
    Includes timestamps, UI refresh, and rollback protection.
    """
    from tkinter import messagebox
    from db import get_connection
    import datetime

    conn = get_connection()
    if not conn:
        messagebox.showerror("Database Error", "Failed to connect to database.", parent=parent_win)
        return

    try:
        cursor = conn.cursor(dictionary=True)

        # 1️⃣ Get transaction info
        cursor.execute("""
            SELECT t.id, t.item_id, t.user_id, t.quantity, t.type, t.status, i.name AS item_name
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.id = %s
        """, (transaction_id,))
        trans = cursor.fetchone()

        if not trans:
            messagebox.showerror("Error", f"Transaction {transaction_id} not found.", parent=parent_win)
            return

        item_id = trans["item_id"]
        qty = int(trans["quantity"] or 0)
        trans_type = trans["type"]
        old_status = trans["status"]

        print(f"[ADMIN] Updating Transaction {transaction_id} | Type: {trans_type} | {old_status} → {new_status}")

        # 2️⃣ Handle different transaction types
        if trans_type == "borrow":
            # ✅ Borrow Logic
            if new_status == "approved":
                # Only marks as approved (item reserved for borrowing)
                print("→ Borrow approved. No stock adjustment yet.")

            elif new_status == "released":
                # Actual release → decrease stock
                cursor.execute("""
                    UPDATE items
                    SET stock = GREATEST(stock - %s, 0)
                    WHERE id = %s
                """, (qty, item_id))
                print(f"→ Borrow released: -{qty} from stock")

            elif new_status in ("returned", "return_approved", "cancelled"):
                # Return or cancel → restore stock
                cursor.execute("""
                    UPDATE items
                    SET stock = stock + %s
                    WHERE id = %s
                """, (qty, item_id))
                print(f"→ Borrow returned/cancelled: +{qty} back to stock")

        elif trans_type == "reserve":
            # ✅ Reserve Logic (faculty)
            if new_status == "approved":
                # Reserve approved → decrease stock, increase reserved_count
                cursor.execute("""
                    UPDATE items
                    SET 
                        reserved_count = COALESCE(reserved_count, 0) + %s,
                        stock = GREATEST(stock - %s, 0)
                    WHERE id = %s
                """, (qty, qty, item_id))
                print(f"→ Reserve approved: +{qty} reserved, -{qty} stock")

            elif new_status in ("rejected", "expired", "cancelled"):
                # Undo reservation → decrease reserved_count, restore stock
                cursor.execute("""
                    UPDATE items
                    SET 
                        reserved_count = GREATEST(COALESCE(reserved_count, 0) - %s, 0),
                        stock = stock + %s
                    WHERE id = %s
                """, (qty, qty, item_id))
                print(f"→ Reserve undone: -{qty} reserved, +{qty} stock")

            elif new_status == "released":
                # Reservation released → decrease reserved_count only
                cursor.execute("""
                    UPDATE items
                    SET reserved_count = GREATEST(COALESCE(reserved_count, 0) - %s, 0)
                    WHERE id = %s
                """, (qty, item_id))
                print(f"→ Reserve released: -{qty} reserved only")

        elif trans_type == "return":
            # ✅ Return Logic
            if new_status in ("approved", "return_approved", "completed"):
                # When return is approved → stock increases
                cursor.execute("""
                    UPDATE items
                    SET stock = stock + %s
                    WHERE id = %s
                """, (qty, item_id))
                print(f"→ Return processed: +{qty} back to stock")

        # 3️⃣ Update the transaction itself
        cursor.execute("""
            UPDATE transactions
            SET status=%s, updated_at=%s
            WHERE id=%s
        """, (new_status, datetime.datetime.now(), transaction_id))

        # Update timestamps for release/return
        if new_status == "released":
            cursor.execute("""
                UPDATE transactions 
                SET release_time=%s 
                WHERE id=%s
            """, (datetime.datetime.now(), transaction_id))
        elif new_status in ("returned", "return_approved", "completed"):
            cursor.execute("""
                UPDATE transactions 
                SET return_time=%s 
                WHERE id=%s
            """, (datetime.datetime.now(), transaction_id))

        # ✅ Prevent negative stock/reserved_count before commit
        cursor.execute("""
            UPDATE items
            SET 
                stock = GREATEST(COALESCE(stock, 0), 0),
                reserved_count = GREATEST(COALESCE(reserved_count, 0), 0)
        """)
            

        # 4️⃣ Commit changes
        conn.commit()
        print(f"[SUCCESS] Transaction {transaction_id} updated to {new_status}")

        # ✅ Optional UI refresh
        if callable(refresh_func):
            refresh_func()

        # ✅ Notify user
        messagebox.showinfo("Success", f"Transaction {transaction_id} marked as {new_status}.", parent=parent_win)
        log_admin_action("Admin", f"Transaction {transaction_id} updated → {new_status}", item_name=trans["item_name"], user_name=str(trans["user_id"]))

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to update transaction {transaction_id}: {e}")
        messagebox.showerror("Error", f"Failed to update transaction: {e}", parent=parent_win)

    finally:
        cursor.close()
        conn.close()


def open_history_report(root, user_id=None, user_type="user"):
    win = tk.Toplevel(root)
    win.title("📜 Transaction History Report")
    win.attributes("-fullscreen", True)
    win.focus_force()
    win.configure(bg="#ecf0f1")

    win.transient(root)      # Tie this window to its parent (keeps on top)
    win.grab_set()           # Make it modal (user can’t click behind it)
    win.focus_set()          # Keep focus on this window


    # --- Header / Filter Bar ---
    filter_frame = tk.Frame(win, bg="#2c3e50")
    filter_frame.pack(fill="x")

    tk.Label(filter_frame, text="Filter:", bg="#2c3e50", fg="white").pack(side="left", padx=10, pady=10)

    filter_var = tk.StringVar(value="All")
    filter_menu = ttk.Combobox(filter_frame, textvariable=filter_var, state="readonly",
                               values=["All", "Daily", "Weekly", "Monthly"])
    filter_menu.pack(side="left", padx=10)

    include_archived = tk.BooleanVar(value=True)
    tk.Checkbutton(filter_frame, text="Show Archived Users", variable=include_archived,
                   bg="#2c3e50", fg="white", selectcolor="#34495e").pack(side="left", padx=10)

    tk.Button(filter_frame, text="Apply", command=lambda: load_history()).pack(side="left", padx=10)
    tk.Button(filter_frame, text="Export CSV", command=lambda: export_to_csv()).pack(side="left", padx=10)
    tk.Button(filter_frame, text="Close", command=win.destroy).pack(side="right", padx=10, pady=10)

    # --- Table Setup ---
    cols = ("Username", "Item", "Type", "Status", "Qty", "Created", "Released", "Returned")
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    # --- Summary Bar ---
    summary_frame = tk.Frame(win, bg="#34495e")
    summary_frame.pack(fill="x")
    summary_label = tk.Label(summary_frame, text="🧾 Summary:  Borrowed: 0  Returned: 0  Reserved: 0  Total: 0",
                             bg="#34495e", fg="white", font=("Arial", 12, "bold"))
    summary_label.pack(pady=5)

    # --- Sorting Function ---
    def sort_column(tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]) if t[0] else 0, reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower() if t[0] else "", reverse=reverse)
        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)
        for c in tree["columns"]:
            tree.heading(c, text=c, command=lambda c=c: sort_column(tree, c, False))
        arrow = " ↑" if not reverse else " ↓"
        tree.heading(col, text=col + arrow, command=lambda: sort_column(tree, col, not reverse))

    for col in cols:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))

    # --- Load / Filter Logic ---
    def load_history():
        conn = get_connection()
        cursor = conn.cursor()

        # Determine date filter
        selected = filter_var.get()
        if selected == "Daily":
            date_filter = "AND DATE(t.created_at) = CURDATE()"
        elif selected == "Weekly":
            date_filter = "AND t.created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)"
        elif selected == "Monthly":
            date_filter = "AND t.created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        else:
            date_filter = ""

        # Archived user join logic
        if include_archived.get():
            user_join = """
                LEFT JOIN users u ON t.user_id = u.id
                LEFT JOIN archived_users a ON t.user_id = a.id
            """
            user_name = "COALESCE(u.name, a.name)"
        else:
            user_join = "JOIN users u ON t.user_id = u.id"
            user_name = "u.name"

        # Query logic (faculty sees all)
        if user_type == "faculty":
            cursor.execute(f"""
                SELECT {user_name} AS username, i.name AS item_name, 
                       t.type, t.status, t.quantity, 
                       t.created_at, t.released_at, t.returned_at
                FROM transactions t
                {user_join}
                JOIN items i ON t.item_id = i.id
                WHERE 1=1 {date_filter}
                ORDER BY username ASC, item_name ASC, t.created_at ASC
            """)
        else:
            cursor.execute(f"""
                SELECT {user_name} AS username, i.name AS item_name, 
                       t.type, t.status, t.quantity, 
                       t.created_at, t.released_at, t.returned_at
                FROM transactions t
                {user_join}
                JOIN items i ON t.item_id = i.id
                WHERE t.user_id = %s {date_filter}
                ORDER BY username ASC, item_name ASC, t.created_at ASC
            """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        # Clear old data
        for r in tree.get_children():
            tree.delete(r)

        borrowed = returned = reserved = 0
        for r in rows:
            tree.insert("", "end", values=r)
            status = (r[3] or "").lower()
            if "borrow" in status:
                borrowed += 1
            elif "return" in status:
                returned += 1
            elif "reserve" in status:
                reserved += 1

        total = len(rows)
        summary_label.config(
            text=f"🧾 Summary:  Borrowed: {borrowed}  Returned: {returned}  Reserved: {reserved}  Total: {total}"
        )

    # --- Export to CSV ---
    def export_to_csv():
        # Pause grab temporarily so filedialog works properly
        win.grab_release()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Report As",
            parent=win  # ✅ ensures dialog is attached to report window
        )

        # Re-grab focus immediately after closing the dialog
        win.grab_set()
        win.focus_force()

        if not file_path:
            return

        rows = [tree.item(i)["values"] for i in tree.get_children()]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(rows)
        messagebox.showinfo("Export Successful", f"Report saved to:\n{file_path}", parent=win)

    
       

