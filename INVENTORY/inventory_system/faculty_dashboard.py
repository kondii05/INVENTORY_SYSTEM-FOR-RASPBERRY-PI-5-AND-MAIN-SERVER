import os
import sys
import subprocess
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from db import get_connection
import datetime
from tkinter import simpledialog
from user_dashboard import open_cart_window


def logout_and_return(win):
    """Close the dashboard and reopen the login screen from main.py."""
    win.destroy()

    # Get the current python executable
    python = sys.executable

    # Relaunch main.py (the login screen)
    script_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.Popen([python, script_path])

    # Exit current process to avoid multiple windows
    sys.exit()


# ---------------- FACULTY DASHBOARD ---------------- #
def open_faculty_dashboard(root, user):
    win = tk.Toplevel(root)
    win.title("Faculty Dashboard")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ecf0f1")

    tk.Label(
        win, text=f"Welcome, {user['name']} (Faculty)",
        font=("Arial", 28, "bold"),
        bg="#800000", fg="white", pady=20
    ).pack(fill="x")

    frame = tk.Frame(win, bg="#ecf0f1")
    frame.pack(expand=True)

    btn_style = {"font": ("Arial", 22, "bold"), "width": 25, "height": 2, "relief": "flat", "bd": 0}

    tk.Button(frame, text="📦 Borrow Items", bg="#800000", fg="white",
              command=lambda: open_borrow_items(win, user), **btn_style).pack(pady=20)

    tk.Button(frame, text="↩ Return Items", bg="#800000", fg="white",
              command=lambda: open_return_items(win, user), **btn_style).pack(pady=20)

    tk.Button(frame, text="📦 Reserve Items", bg="#800000", fg="white",
    command=lambda: open_reserve_items(win, user), **btn_style).pack(pady=20)

    tk.Button(frame, text="🛒 My Cart", bg="#800000", fg="white",
              command=lambda: open_cart_window(win, user), **btn_style).pack(pady=20)
    
    tk.Button(frame, text="📑 History", bg="#800000", fg="white",
              command=lambda: open_history(win, user), **btn_style).pack(pady=20)

    tk.Button(frame, text="🚪 Logout", bg="#800000", fg="white",
             command=lambda: logout_and_return(win), **btn_style).pack(pady=20)    

    win.bind("<Escape>", lambda e: win.destroy())


# ---------------- BORROW ITEMS (same as user) ---------------- #
def open_borrow_items(root, user):
    from user_dashboard import open_borrow_items
    open_borrow_items(root, user)


# ---------------- MY CART (same as user) ---------------- #
def open_cart(root, user):
    from user_dashboard import open_cart_window
    open_cart(root, user)


# ---------------- RETURN ITEMS (same as user) ---------------- #
def open_return_items(root, user):
    from user_dashboard import open_return_items
    open_return_items(root, user)


# ---------------- HISTORY (Borrow + Return + Reserve) ---------------- #
def open_history(root, user):
    hist_win = tk.Toplevel(root)
    hist_win.title("History")
    hist_win.attributes("-fullscreen", True)
    hist_win.configure(bg="#ecf0f1")

    tk.Label(
        hist_win, text=f"History - {user['name']}",
        font=("Arial", 24, "bold"),
        bg="#800000", fg="white", pady=15
    ).pack(fill="x")

    # Main container
    main_frame = tk.Frame(hist_win, bg="#ecf0f1")
    main_frame.pack(fill="both", expand=True)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    cols = ("id", "item", "status", "created_at")

    # ---------------- Borrow History ----------------
    borrow_frame = tk.Frame(notebook, bg="#ecf0f1")
    notebook.add(borrow_frame, text="Borrow History")

    borrow_tree = ttk.Treeview(borrow_frame, columns=cols, show="headings", height=20)
    for col in cols:
        borrow_tree.heading(col, text=col.capitalize())
        borrow_tree.column(col, width=250, anchor="center")
    borrow_tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def load_borrow_history():
        for row in borrow_tree.get_children():
            borrow_tree.delete(row)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, i.name, t.status, t.created_at
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.user_id=%s AND t.type='borrow'
            ORDER BY t.created_at DESC
        """, (user["id"],))
        for r in cursor.fetchall():
            borrow_tree.insert("", "end", values=(r["id"], r["name"], r["status"], r["created_at"]))
        cursor.close()
        conn.close()
    load_borrow_history()


    # ---------------- Return History ----------------
    return_frame = tk.Frame(notebook, bg="#ecf0f1")
    notebook.add(return_frame, text="Return History")

    return_tree = ttk.Treeview(return_frame, columns=cols, show="headings", height=20)
    for col in cols:
        return_tree.heading(col, text=col.capitalize())
        return_tree.column(col, width=250, anchor="center")
    return_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_return_history():
        for row in return_tree.get_children():
            return_tree.delete(row)
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, i.name, t.status, t.created_at
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.user_id=%s AND t.type='return'
            ORDER BY t.created_at DESC
        """, (user["id"],))
        for r in cursor.fetchall():
            return_tree.insert("", "end", values=(r["id"], r["name"], r["status"], r["created_at"]))
        cursor.close()
        conn.close()
    load_return_history()


    # ---------------- Reserve History ----------------
    reserve_frame = tk.Frame(notebook, bg="#ecf0f1")
    notebook.add(reserve_frame, text="Reserve History")

    # ✅ Added reserve_date and reserve_time columns
    cols = ("id", "item", "status", "created_at", "reserve_date", "reserve_time")

    reserve_tree = ttk.Treeview(reserve_frame, columns=cols, show="headings", height=20)
    for col in cols:
        reserve_tree.heading(col, text=col.replace("_", " ").title())
        reserve_tree.column(col, width=200, anchor="center")
    reserve_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def load_reserve_history():
        for row in reserve_tree.get_children():
            reserve_tree.delete(row)

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id, i.name, t.status, t.created_at, t.reserve_date, t.reserve_time
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.user_id=%s AND t.type='reserve'
            ORDER BY t.created_at DESC
        """, (user["id"],))

        for r in cursor.fetchall():
            reserve_tree.insert("", "end", values=(
                r["id"],
                r["name"],
                r["status"],
                r["created_at"],
                r["reserve_date"].strftime("%b %d, %Y") if r["reserve_date"] else "—",
                (datetime.datetime.strptime(str(r["reserve_time"])[:-3], "%H:%M").strftime("%I:%M %p")
                if r["reserve_time"] else "—")
            ))

        cursor.close()
        conn.close()

    load_reserve_history()

    # ---------------- Back Button (always visible at bottom) ----------------
    bottom_frame = tk.Frame(hist_win, bg="#ecf0f1")
    bottom_frame.pack(fill="x", side="bottom", pady=15)

    def go_back():
        hist_win.destroy()
        open_faculty_dashboard(root, user)  # reopen faculty dashboard

    tk.Button(bottom_frame, text="⬅ Back", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=go_back).pack()


# ---------------- RESERVE ITEMS (faculty only) ---------------- #
def open_reserve_items(win, faculty):
    win.destroy()  # Close previous window
    reserve_win = tk.Toplevel()
    reserve_win.title("Reserve Items")
    reserve_win.attributes("-fullscreen", True)
    reserve_win.configure(bg="#f4f6f7")

    # ======= HEADER =======
    header = tk.Frame(reserve_win, bg="#800000")
    header.pack(fill="x")

    tk.Label(
        header, text="📦 Select Items to Reserve",
        font=("Segoe UI", 26, "bold"),
        bg="#800000", fg="white", pady=15
    ).pack(side="left", padx=30)


    # ======= SCROLLABLE ITEM GRID =======
    canvas = tk.Canvas(reserve_win, bg="#f4f6f7", highlightthickness=0)
    scrollbar = ttk.Scrollbar(reserve_win, orient="vertical", command=canvas.yview)
    store_frame = tk.Frame(canvas, bg="#f4f6f7")
    canvas.create_window((0, 0), window=store_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    store_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    selected = []
    def reserve_selected():
        chosen = [i for i in selected if i["selected"]]
        if not chosen:
            messagebox.showwarning("No Selection", "Please select at least one item.", parent=reserve_win)
            return

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        added = 0
        try:
            for i in chosen:
                cursor.execute("""
                    SELECT id FROM items
                    WHERE name=%s AND status IN ('available','partially_reserved')
                    LIMIT %s
                """, (i["name"], int(i["qty"].get())))
                ids = cursor.fetchall()
                for row in ids:
                    item_id = row[0] if isinstance(row, tuple) else row.get("id")
                    cursor.execute("""
                        INSERT INTO reserve_cart (user_id, item_id, quantity, added_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (faculty["id"], i["item_id"], int(i["qty"].get())))
                    added += 1
            conn.commit()
            messagebox.showinfo("Success", f"{added} item(s) added to Reserve Cart!", parent=reserve_win)
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to add items: {e}", parent=reserve_win)
        finally:
            cursor.close()
            conn.close()

    # ======= LOAD ITEMS FUNCTION =======
    def load_items():
        for widget in store_frame.winfo_children():
            widget.destroy()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                MIN(id) AS item_id,
                name,
                category,
                SUM(stock) AS stock,
                MIN(image_path) AS image_path
            FROM items
            WHERE status IN ('available', 'partially_reserved')
            GROUP BY name, category
            ORDER BY name ASC;
        """)
        items = cursor.fetchall()
        cursor.close()
        conn.close()

        if not items:
            tk.Label(
                store_frame,
                text="No items available for reservation.",
                font=("Segoe UI", 16, "italic"),
                bg="#f4f6f7",
                fg="#7f8c8d"
            ).pack(pady=50)
            return

        cols = 4
        for idx, item in enumerate(items):
            # ✅ Check stock availability
            has_stock = item["stock"] > 0
            card_color = "white" if has_stock else "#dcdde1"

            # 🪧 Card layout
            card = tk.Frame(
                store_frame,
                bg=card_color,
                bd=0,
                relief="solid",
                padx=10,
                pady=12,
                highlightthickness=2,
                highlightbackground="#dcdde1"
            )
            card.grid(row=idx // cols, column=idx % cols, padx=15, pady=15)

            # 🖼 Load image
            img_path = os.path.join("images", item.get("image_path") or "default.png")
            try:
                img = Image.open(img_path).resize((120, 120))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                photo = ImageTk.PhotoImage(Image.new("RGB", (120, 120), "gray"))

            img_label = tk.Label(card, image=photo, bg=card_color)
            img_label.image = photo
            img_label.pack(pady=5)

            # 🧾 Item name and stock info
            tk.Label(
                card,
                text=item["name"],
                font=("Segoe UI", 13, "bold"),
                bg=card_color,
                fg="#800000" if has_stock else "#7f8c8d"
            ).pack()

            if not has_stock:
                tk.Label(
                    card,
                    text="Out of Stock",
                    font=("Segoe UI", 10, "italic"),
                    bg=card_color,
                    fg="#800000"
                ).pack(pady=2)

            tk.Label(
                card,
                text=f"Stock: {int(item['stock'])}",
                font=("Segoe UI", 10),
                bg=card_color,
                fg="#000000"
            ).pack(pady=2)

            # 🧩 Disable interaction if no stock
            if not has_stock:
                card.bind(
                    "<Button-1>",
                    lambda e: messagebox.showwarning("Out of Stock", "This item is not available for reservation!")
                )
                continue

            # Quantity selector
            qty_var = tk.IntVar(value=1)
            qty_dropdown = ttk.Combobox(
                card,
                textvariable=qty_var,
                values=[str(i) for i in range(1, int(item["stock"]) + 1)],
                width=4,
                state="readonly"
            )
            qty_dropdown.pack(pady=4)

            # ====== Toggle Select Function ======
            selected_state = {"selected": False}

            def toggle_select(event=None, c=None, i=None, q=None, item_id=None, state=None):
                if not state["selected"]:
                    # ✅ Highlight green border when selected
                    c.config(highlightbackground="#510400", highlightcolor="#510400", highlightthickness=4)
                    state["selected"] = True

                    # ✅ Add item with full data
                    selected.append({
                        "name": i,
                        "qty": q,
                        "selected": True,
                        "item_id": item_id
                    })
                else:
                    # ❌ Revert to gray border when unselected
                    c.config(highlightbackground="#dcdde1", highlightcolor="#dcdde1", highlightthickness=2)
                    state["selected"] = False

                    # ✅ Remove deselected item
                    for s in list(selected):
                        if s["name"] == i:
                            selected.remove(s)

            # ✅ Bind selection events
            card.bind(
                "<Button-1>",
                lambda e, c=card, i=item["name"], q=qty_var, iid=item["item_id"], s=selected_state:
                toggle_select(e, c, i, q, iid, s)
            )
            for child in card.winfo_children():
                child.bind(
                    "<Button-1>",
                    lambda e, c=card, i=item["name"], q=qty_var, iid=item["item_id"], s=selected_state:
                    toggle_select(e, c, i, q, iid, s)
                )
 # ======= ACTION BAR (RESERVE + CART + BACK) ======= #
    action_bar = tk.Frame(reserve_win, bg="#ecf0f1")
    action_bar.pack(fill="x", pady=20)

    # ➕ Reserve Selected button
    tk.Button(
        action_bar, text="➕ Reserve Selected", bg="#800000", fg="white",
        font=("Segoe UI", 14, "bold"), width=25, height=1,
        command=reserve_selected, relief="flat"
    ).pack(pady=10)

    # 🗓 My Reserve Cart button
    tk.Button(
        action_bar, text="🗓 My Reserve Cart", bg="#800000", fg="white",
        font=("Segoe UI", 14, "bold"), width=25, height=1,
        command=lambda: open_reserve_cart(reserve_win, faculty), relief="flat"
    ).pack(pady=10)

    # ⬅ Back button
    tk.Button(
        action_bar, text="⬅ Back", bg="#800000", fg="white",
        font=("Segoe UI", 14, "bold"), width=25, height=1,
        command=lambda: [reserve_win.destroy(), open_faculty_dashboard(None, faculty)], relief="flat"
    ).pack(pady=10)

    # ======= AUTO-REFRESH FUNCTION =======
    def auto_refresh_items():
        load_items()  # reload DB data
        reserve_win.after(3000, auto_refresh_items)  # refresh every 3 seconds

    # ✅ Start-up
    load_items()          # Initial load
    auto_refresh_items()  # Continuous auto-refresh

# ---------------- RESERVE CART ---------------- #
def open_reserve_cart(root, faculty):
    cart_win = tk.Toplevel(root)
    cart_win.title(f"🗓 Reserve Cart - {faculty.get('name','')}")
    cart_win.attributes("-fullscreen", True)
    cart_win.configure(bg="#f4f6f7")

    # ======= HEADER (Borrow-style) =======
    header = tk.Frame(cart_win, bg="#800000")
    header.pack(fill="x")
    tk.Label(
        header, text=f"🗓 My Reserve Cart - {faculty.get('name','')}",
        font=("Segoe UI", 20, "bold"),
        bg="#800000", fg="white", pady=12
    ).pack()

    # ======= MAIN BODY =======
    body = tk.Frame(cart_win, bg="#f4f6f7")
    body.pack(fill="both", expand=True, padx=20, pady=10)

    # Left scrollable list
    left = tk.Frame(body, bg="#f4f6f7")
    left.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(left, bg="#f4f6f7", highlightthickness=0)
    scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
    list_frame = tk.Frame(canvas, bg="#f4f6f7")
    canvas.create_window((0, 0), window=list_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ======= RIGHT PANEL (Borrow-style) =======
    right = tk.Frame(body, width=320, bg="#ecf0f1")
    right.pack(side="right", fill="y")

    summary_label = tk.Label(
        right, text="Selected: 0 items | Total Qty: 0",
        font=("Segoe UI", 14, "bold"),
        bg="#ecf0f1"
    )
    summary_label.pack(pady=20)

    def styled_button(parent, text, color, cmd):
        return tk.Button(
            parent, text=text, bg=color, fg="white",
            font=("Segoe UI", 12, "bold"),
            width=20, height=2, relief="flat", cursor="hand2",
            command=cmd
        )

    # ======= INTERNAL FUNCTIONS =======
    selected = {}

    def update_summary():
        total_selected = 0
        total_qty = 0
        for cid, info in selected.items():
            try:
                qty = int(info["qty"].get()) if hasattr(info["qty"], "get") else int(info["qty"])
                if info["selected"]:
                    total_selected += 1
                    total_qty += qty
            except Exception:
                pass
        summary_label.config(text=f"Selected: {total_selected} items | Total Qty: {total_qty}")

    def load_cart():
        for w in list_frame.winfo_children():
            w.destroy()
        selected.clear()
        update_summary()

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                MIN(c.id) AS cart_id,
                MIN(i.id) AS item_id,
                i.name,
                i.category,
                i.image_path,
                SUM(c.quantity) AS quantity,
                (
                    SELECT COUNT(*) FROM items AS ii
                    WHERE ii.name = i.name AND ii.status IN ('available','partially_reserved')
                ) AS stock
            FROM reserve_cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = %s
            GROUP BY i.name, i.category, i.image_path
            ORDER BY i.name ASC
        """, (faculty["id"],))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            tk.Label(list_frame, text="Your reserve cart is empty.",
                     font=("Segoe UI", 14), bg="#f4f6f7").pack(pady=30)
            return

        for r in rows:
            name = r["name"]
            qty = int(r["quantity"] or 1)
            stock = int(r["stock"] or 0)
            img_file = r["image_path"]
            available = stock > 0

            card = tk.Frame(
                list_frame,
                bg="white" if available else "#f0f0f0",
                bd=0, relief="solid", padx=20, pady=10,
                highlightthickness=4, highlightbackground="#dcdde1"
            )
            card.pack(fill="x", pady=6, padx=8)

            # Image
            leftc = tk.Frame(card, bg="white")
            leftc.pack(side="left", padx=8, pady=8)

            try:
                img_path = os.path.join("images", img_file) if img_file else None
                if img_path and os.path.exists(img_path):
                    img = Image.open(img_path).resize((80, 80))
                    photo = ImageTk.PhotoImage(img)
                else:
                    photo = ImageTk.PhotoImage(Image.new("RGB", (80, 80), "gray"))
            except Exception:
                photo = ImageTk.PhotoImage(Image.new("RGB", (80, 80), "gray"))

            thumbnail = tk.Label(leftc, image=photo, bg="white")
            thumbnail.image = photo
            thumbnail.pack()

            # Info
            center = tk.Frame(card, bg="white")
            center.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(center, text=name, font=("Segoe UI", 12, "bold"),
                     bg="white", anchor="w").pack(fill="x")
            tk.Label(center, text=f"Stock: {stock} | In Cart: {qty}",
                     bg="white", fg="#2ecc71" if available else "#e74c3c",
                     font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(3, 0))

            # Right controls
            rightc = tk.Frame(card, bg="white")
            rightc.pack(side="right", padx=10, pady=8)
            qty_var = tk.StringVar(value=str(qty))
            qty_values = [str(i) for i in range(1, max(1, stock) + 1)]
            qty_dropdown = ttk.Combobox(rightc, textvariable=qty_var, values=qty_values,
                                        width=5, state="readonly")
            qty_dropdown.pack(side="left", padx=5)
            qty_dropdown.bind("<<ComboboxSelected>>", lambda e: update_summary())

            def remove_this(item_name=name):
                if not messagebox.askyesno("Confirm", f"Remove {item_name}?", parent=cart_win):
                    return
                conn = get_connection()
                if conn:
                    c2 = conn.cursor()
                    c2.execute("""
                        DELETE FROM reserve_cart
                        WHERE user_id = %s
                        AND item_id IN (SELECT id FROM items WHERE name = %s)
                    """, (faculty["id"], item_name))
                    conn.commit()
                    c2.close()
                    conn.close()
                load_cart()

            tk.Button(rightc, text="Remove", bg="#800000", fg="white",
                      relief="flat", command=remove_this).pack(side="left", padx=6)

            # Highlight select
            selected_state = {"selected": False}

            def toggle_select(event=None, c=card, n=name, q=qty_var, item_id=None):
                if not selected_state["selected"]:
                    # ✅ Highlight the selected card
                    c.config(highlightbackground="#27ae60", highlightcolor="#27ae60")
                    selected_state["selected"] = True

                    # ✅ Make sure item_id is stored correctly
                    selected[n] = {
                        "qty": q,
                        "selected": True,
                        "item_id": item_id if item_id is not None else None
                    }

                else:
                    # ❌ Unselect and revert appearance
                    c.config(highlightbackground="#dcdde1", highlightcolor="#dcdde1")
                    selected_state["selected"] = False

                    # ✅ Safely remove the item from selection
                    if n in selected:
                        del selected[n]

                update_summary()

            card.bind("<Button-1>", lambda event, c=card, n=name, q=qty_var, iid=r["item_id"]: toggle_select(event, c, n, q, iid))

            for child in card.winfo_children():
                child.bind("<Button-1>", lambda event, c=card, n=name, q=qty_var, iid=r["item_id"]: toggle_select(event, c, n, q, iid))
                child.bind("<ButtonRelease-1>", toggle_select)

        update_summary()

    # ======= BUTTONS (Borrow-style right panel) =======
    def select_all():
        for w in list_frame.winfo_children():
            if isinstance(w, tk.Frame):
                w.config(highlightbackground="#27ae60")
        for name in list(selected.keys()):
            selected[name]["selected"] = True
        update_summary()

    def clear_all():
        if not messagebox.askyesno("Confirm", "Clear all items?", parent=cart_win):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM reserve_cart WHERE user_id = %s", (faculty["id"],))
        conn.commit()
        cur.close()
        conn.close()
        load_cart()

    def remove_selected():
        # Check if user has selected anything
        if not selected:
            messagebox.showwarning("No selection", "Please select at least one item to remove.", parent=cart_win)
            return

        # Confirm action
        if not messagebox.askyesno("Confirm Remove", "Are you sure you want to remove the selected items?", parent=cart_win):
            return

        # Connect to database
        conn = get_connection()
        cur = conn.cursor()

        try:
            # Loop through all selected items and delete them by item_id
            for n, data in selected.items():
                item_id = data.get("item_id")
                if not item_id:
                    print(f"⚠ Skipped item '{n}' because item_id is missing.")
                    continue

                cur.execute("""
                    DELETE FROM reserve_cart
                    WHERE user_id = %s AND item_id = %s
                """, (faculty["id"], item_id))

            conn.commit()
            messagebox.showinfo("Removed", "Selected items have been removed from your reserve cart.", parent=cart_win)

            # Refresh cart display
            load_cart()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to remove selected items:\n{e}", parent=cart_win)
        finally:
            cur.close()
            conn.close()


    def send_request():
        import datetime
        from tkinter import Toplevel, Label, Button, StringVar, OptionMenu, messagebox
        from tkcalendar import Calendar

        chosen = [(cid, d) for cid, d in selected.items()]
        if not chosen:
            messagebox.showwarning("No Selection", "Please select at least one item to reserve.", parent=cart_win)
            return

        # ---------- Date/Time Picker ----------
        picker = Toplevel(cart_win)
        picker.title("Select Reservation Date & Time")
        picker.geometry("420x450")
        picker.configure(bg="#ecf0f1")
        picker.resizable(False, False)

        Label(picker, text="Select Reservation Date:", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)

        today = datetime.date.today()
        cal = Calendar(picker, selectmode="day", date_pattern="yyyy-mm-dd", mindate=today,
                    background="#2c3e50", headersbackground="#34495e", foreground="white",
                    normalbackground="#ecf0f1", weekendbackground="#bdc3c7")
        cal.pack(pady=10)

        # ----- Time picker -----
        Label(picker, text="Select Time:", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        time_frame = tk.Frame(picker, bg="#ecf0f1")
        time_frame.pack(pady=5)

        hour_var = tk.IntVar(value=9)
        minute_var = tk.IntVar(value=0)
        am_pm_var = tk.StringVar(value="AM")

        hour_spin = tk.Spinbox(time_frame, from_=1, to=12, width=5, font=("Arial", 12), textvariable=hour_var)
        hour_spin.pack(side="left", padx=5)
        Label(time_frame, text=":", bg="#ecf0f1", font=("Arial", 14, "bold")).pack(side="left")
        minute_spin = tk.Spinbox(time_frame, from_=0, to=59, width=5, font=("Arial", 12),
                                format="%02.0f", textvariable=minute_var)
        minute_spin.pack(side="left", padx=5)

        am_pm_menu = OptionMenu(time_frame, am_pm_var, "AM", "PM")
        am_pm_menu.config(font=("Arial", 12), width=4)
        am_pm_menu.pack(side="left", padx=5)

        # ---------- Confirm logic ----------
        def confirm_date_time():
            reserve_date = cal.get_date()

            hour = int(hour_var.get())
            minute = int(minute_var.get())
            am_pm = am_pm_var.get()

            # Convert to 24-hour time for MySQL
            if am_pm == "PM" and hour != 12:
                hour += 12
            elif am_pm == "AM" and hour == 12:
                hour = 0
            reserve_time = f"{hour:02}:{minute:02}"

            # Validate against current time
            try:
                selected_dt = datetime.datetime.strptime(f"{reserve_date} {reserve_time}", "%Y-%m-%d %H:%M")
                if selected_dt < datetime.datetime.now():
                    messagebox.showwarning("Invalid Selection", "You cannot select a past date/time.", parent=picker)
                    return
            except ValueError:
                messagebox.showerror("Invalid Input", "Please select a valid date/time.", parent=picker)
                return

            display_time = f"{hour_var.get():02}:{minute_var.get():02} {am_pm}"
            if not messagebox.askyesno("Confirm Reservation",
                                    f"Send reservation request for:\n\n📅 {reserve_date}\n⏰ {display_time}",
                                    parent=picker):
                return

            # ---------- Database Insert ----------
            conn = get_connection()
            cur = conn.cursor()
            added = 0

            try:
                for cid, d in chosen:
                    qty = int(d["qty"].get()) if hasattr(d["qty"], "get") else int(d["qty"])
                    item_id = d.get("item_id")

                    if not item_id:
                        messagebox.showerror(
                            "Error",
                            f"This item has no item_id set: {d.get('name', 'unknown')}",
                            parent=picker
                        )
                        return

                    cur.execute("""
                        INSERT INTO transactions
                        (user_id, item_id, type, status, quantity, created_at, reserve_date, reserve_time)
                        VALUES (%s, %s, 'reserve', 'pending', %s, NOW(), %s, %s)
                    """, (faculty["id"], item_id, qty, reserve_date, reserve_time))


                    # ✅ Clean up the reserve_cart
                    cur.execute("""DELETE FROM reserve_cart 
                                WHERE user_id=%s AND item_id=%s
                                """, (faculty["id"], d["item_id"]))

                    added += 1

                conn.commit()

                messagebox.showinfo("Success",
                                    f"Reservation set for {reserve_date} at {display_time}.",
                                    parent=picker)
                picker.destroy()
                load_cart()

            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Failed to send reservation: {e}", parent=picker)
            finally:
                cur.close()
                conn.close()

        # ---------- Buttons ----------
        btn_frame = tk.Frame(picker, bg="#ecf0f1")
        btn_frame.pack(pady=15)

        Button(btn_frame, text="Confirm", font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
            width=10, command=confirm_date_time).pack(side="left", padx=10)
        Button(btn_frame, text="Cancel", font=("Arial", 12, "bold"), bg="#c0392b", fg="white",
            width=10, command=picker.destroy).pack(side="left", padx=10)
    


    # Add buttons (right panel)
    styled_button(right, "Select All", "#800000", select_all).pack(pady=8)
    styled_button(right, "Send Reserve Request", "#800000", send_request).pack(pady=8)
    styled_button(right, "Remove Selected", "#800000", remove_selected).pack(pady=8)
    styled_button(right, "Clear All", "#800000", clear_all).pack(pady=8)

    # Borrow Cart button
    try:
        from user_dashboard import open_cart_window
        styled_button(right, "🛒 Borrow Cart", "#800000",
                      lambda: [cart_win.destroy(), open_cart_window(root, faculty)]).pack(pady=8)
    except Exception:
        styled_button(right, "🛒 Borrow Cart", "#95a5a6", lambda: None).pack(pady=8)

    # Back to faculty dashboard
    
    styled_button(right, "⬅ Back", "#800000",
                  lambda: [cart_win.destroy(), open_reserve_items(root, faculty)]).pack(pady=8)

    # Load cart items
    load_cart()
