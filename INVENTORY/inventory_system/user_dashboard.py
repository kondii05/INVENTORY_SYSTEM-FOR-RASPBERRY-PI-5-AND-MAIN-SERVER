import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import sys
import subprocess
from db import get_connection
from tkinter import ttk 
from archived_items import open_archived_items



def logout_and_return(win, root):
    win.destroy()       # close the dashboard window
    root.deiconify()    # ✅ show RFID window again

# ---------------- USER DASHBOARD ---------------- #
# ---------------- USER DASHBOARD ---------------- #
def open_user_dashboard(root, user):
    # ✅ Create a Toplevel window (child of main Tk)
    win = tk.Toplevel(root)
    win.title("User Dashboard")
    win.configure(bg="#ffffff")

    # ✅ Real fullscreen that’s stable on Raspberry Pi
    win.attributes("-fullscreen", True)
    win.after(100, lambda: win.state('zoomed'))
    
    # ---------- CONFIGURATION ----------
    PRIMARY_COLOR = "#800000"   # Maroon
    ACCENT_COLOR = "#800000"    # Gold
    TEXT_COLOR = "#800000"      # Maroon text on white
    FONT_HEADER = ("Segoe UI", 22, "bold")
    FONT_BUTTON = ("Segoe UI", 18, "bold")

    # ---------- HEADER ----------
    tk.Label(
        win,
        text=f"Welcome, {user['name']} (User)",
        bg=PRIMARY_COLOR,
        fg="white",
        font=FONT_HEADER,
        pady=15
    ).pack(fill="x")

    # ---------- MAIN FRAME ----------
    frame = tk.Frame(win, bg="#ffffff")
    frame.pack(expand=True)

    # ---------- BUTTON STYLE ----------
    btn_style = {
        "font": FONT_BUTTON,
        "width": 25,
        "height": 2,
        "relief": "flat",
        "bd": 0,
        "bg": PRIMARY_COLOR,
        "fg": "white",
        "activebackground": ACCENT_COLOR,
        "activeforeground": "black",
        "cursor": "hand2"
    }

    # ---------- BUTTONS ----------
    tk.Button(
        frame,
        text="📦 Borrow Items",
        command=lambda: open_borrow_items(win, user),
        **btn_style
    ).pack(pady=20)

    tk.Button(
        frame,
        text="↩ Return Items",
        command=lambda: open_return_items(win, user),
        **btn_style
    ).pack(pady=20)

    tk.Button(
        frame,
        text="🛒 My Cart",
        command=lambda: open_cart_window(win, user),
        **btn_style
    ).pack(pady=20)

    tk.Button(
        frame,
        text="📑 History",
        command=lambda: open_history(win, user),
        **btn_style
    ).pack(pady=20)

    tk.Button(
        frame,
        text="🚪 Logout",
        command=lambda: logout_and_return(win, root),
        **btn_style
    ).pack(pady=40)

    # ---------- FOOTER ----------
    tk.Label(
        win,
        text="© 2025 - E-Borrow System | Manuel S. Enverga University Foundation - Candelaria Inc.",
        bg="#ffffff",
        fg=PRIMARY_COLOR,
        font=("Segoe UI", 10)
    ).pack(side="bottom", pady=10)
    
    win.protocol("WM_DELETE_WINDOW", lambda: logout_and_return(win, root))

    win.mainloop()


# ---------------- CATEGORY SELECTION ---------------- #
def open_borrow_items(root, user):
    category_win = tk.Toplevel(root)
    category_win.title("Select Category")
    category_win.attributes("-fullscreen", True)
    category_win.configure(bg="#ffffff")  # ✅ White background (matches main UI)

    # ---------- CONFIGURATION ----------
    PRIMARY_COLOR = "#800000"   # Maroon
    ACCENT_COLOR = "#510400"    # Gold
    TEXT_COLOR = "#800000"      # Maroon text
    FONT_HEADER = ("Segoe UI", 28, "bold")
    FONT_BUTTON = ("Segoe UI", 20, "bold")

    # ---------- HEADER ----------
    tk.Label(
        category_win,
        text="🛍 Borrow Items",
        font=FONT_HEADER,
        bg=PRIMARY_COLOR,
        fg="white",
        pady=20
    ).pack(fill="x")

    tk.Label(
        category_win,
        text="Select a category to view available items",
        font=("Segoe UI", 18),
        bg="#ffffff",
        fg=TEXT_COLOR,
        pady=10
    ).pack()

    # ---------- MAIN FRAME ----------
    frame = tk.Frame(category_win, bg="#ffffff")
    frame.pack(expand=True)

    # ---------- CATEGORY BUTTON FUNCTION ----------
    def category_button(text, emoji):
        return tk.Button(
            frame,
            text=f"{emoji}  {text}",
            bg=PRIMARY_COLOR,
            fg="white",
            font=FONT_BUTTON,
            width=25,
            height=2,
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=ACCENT_COLOR,
            activeforeground="black",
            command=lambda: open_category_items(category_win, user, text)
        )

    # ---------- CATEGORY BUTTONS ----------
    category_button("Electronics", "💻").pack(pady=25)
    category_button("Networking", "🌐").pack(pady=25)
    category_button("Consumables", "🧰").pack(pady=25)

    # ---------- BACK BUTTON ----------
    tk.Button(
        frame,
        text="⬅ Back",
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Segoe UI", 16, "bold"),
        width=31,
        height=2,
        relief="flat",
        bd=0,
        cursor="hand2",
        activebackground=ACCENT_COLOR,
        activeforeground="black",
        command=category_win.destroy
    ).pack(pady=40)

    # ---------- FOOTER ----------
    tk.Label(
        category_win,
        text="© 2025 - E-Borrow System | Manuel S. Enverga University Foundation - Candelaria Inc.",
        bg="#ffffff",
        fg=PRIMARY_COLOR,
        font=("Segoe UI", 10)
    ).pack(side="bottom", pady=10)


# ---------------- ITEM DISPLAY ---------------- #

def open_category_items(prev_win, user, category):
    import os
    from PIL import Image, ImageTk

    prev_win.destroy()

    # ---------- WINDOW SETUP ----------
    win = tk.Toplevel()
    win.title(f"{category} Items")
    win.attributes("-fullscreen", True)
    win.configure(bg="#ffffff")  # White background for clean look

    # ---------- COLOR CONFIG ----------
    PRIMARY_COLOR = "#800000"   # Maroon
    ACCENT_COLOR = "#ffd700"    # Gold
    TEXT_COLOR = "#800000"

    # ---------- HEADER (now on TOP) ----------
    header = tk.Frame(win, bg=PRIMARY_COLOR)
    header.pack(fill="x")

    tk.Label(
        header, text=f"🛒 {category} Items",
        font=("Segoe UI", 26, "bold"),
        bg=PRIMARY_COLOR, fg="white", pady=15
    ).pack(side="left", padx=30)

    # ---------- MAIN SPLIT LAYOUT ----------
    main_frame = tk.Frame(win, bg="#ffffff")
    main_frame.pack(fill="both", expand=True)

    # LEFT: SCROLLABLE AREA
    left_frame = tk.Frame(main_frame, bg="#ffffff")
    left_frame.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(left_frame, bg="#ffffff", highlightthickness=0)
    scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
    store_frame = tk.Frame(canvas, bg="#ffffff")

    # ✅ Keep the window ID so we can layer it correctly
    store_window = canvas.create_window((0, 0), window=store_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    store_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    # ✅ Let mouse clicks pass through the canvas window (prevents global event block)
    canvas.bind("<Button-1>", lambda e: None)

    # ✅ Fix: properly layer the frame inside the canvas
    canvas.lower(store_window)


    # RIGHT: FIXED PANEL (search + buttons)
    right_frame = tk.Frame(main_frame, bg="#ffffff", width=350, relief="flat",
                           highlightthickness=2, highlightbackground="#ddd")
    right_frame.pack(side="right", fill="y", padx=10, pady=10)

    # ---------- SEARCH BAR ----------
    tk.Label(
        right_frame, text="Search Items", font=("Segoe UI", 14, "bold"),
        bg="#ffffff", fg=TEXT_COLOR
    ).pack(pady=(20, 5))

    search_var = tk.StringVar()
    search_entry = tk.Entry(
        right_frame,
        textvariable=search_var,
        font=("Segoe UI", 12),
        width=25,
        relief="solid",
        bd=2,
        justify="center"
    )
    search_entry.pack(pady=(0, 10))

    # ---------- STYLED BUTTON HELPER ----------
    def styled_button(parent, text, command=None, color=PRIMARY_COLOR, icon=None):
        return tk.Button(
            parent, text=f"{icon or ''} {text}",
            bg=color, fg="white",
            font=("Segoe UI", 12, "bold"),
            width=22, height=2,
            relief="flat", cursor="hand2",
            activebackground=ACCENT_COLOR, activeforeground="black",
            command=command
        )

    # ---------- RIGHT BUTTONS ----------
    styled_button(right_frame, "🔍 Search", lambda: load_items(search_var.get())).pack(pady=10)
    styled_button(right_frame, "🛍 Add Selected to Cart", lambda: add_selected_to_cart()).pack(pady=10)
    styled_button(right_frame, "🛒 My Cart", lambda: open_cart_window(win, user)).pack(pady=10)
    styled_button(right_frame, "⬅ Back", lambda: [win.destroy(), open_borrow_items(None, user)]).pack(pady=10)
    selected_items = []

    # ---------- LOAD ITEMS ----------
    def load_items(search_term=""):
        for w in store_frame.winfo_children():
            w.destroy()
        selected_items.clear()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

# ✅ Different query logic for consumables vs other categories
        if category.lower() == "consumables":
            query = """
                SELECT 
                    name,
                    category,
                    SUM(stock) AS stock,          -- Fix for consumables
                    MIN(status) AS status,
                    MIN(image_path) AS image_path
                FROM items
                WHERE category=%s 
                AND status IN ('available', 'partially_reserved')
                GROUP BY name, category
                ORDER BY name ASC
            """
        else:
            query = """
                SELECT 
                    name,
                    category,
                    COUNT(*) AS stock,            -- Keep original logic for others
                    MIN(status) AS status,
                    MIN(image_path) AS image_path
                FROM items
                WHERE category=%s 
                AND status IN ('available', 'partially_reserved')
                GROUP BY name, category
                ORDER BY name ASC
            """

        params = [category]
        if search_term:
            query = query.replace("ORDER BY", "HAVING name LIKE %s ORDER BY")
            params.append(f"%{search_term}%")

        cursor.execute(query, params)
        items = cursor.fetchall()
        cursor.close()
        conn.close()

        if not items:
            tk.Label(
                store_frame,
                text="No items found.",
                font=("Segoe UI", 16, "italic"),
                bg="#ffffff",
                fg="#800000"  # Maroon text for empty message
            ).pack(pady=50)
            return

        # ---------- COLOR SCHEME ----------
        PRIMARY_COLOR = "#800000"   # Maroon
        ACCENT_COLOR = "#510400"    # Gold
        BG_COLOR = "#ffffff"        # White
        BORDER_COLOR = "#dcdde1"

        cols = 6
        for idx, item in enumerate(items):
            # Determine stock and availability
            stock = int(item["stock"] or 0)
            available = stock > 0

            # ---------- CARD ----------
            card = tk.Frame(
                store_frame,
                bg=BG_COLOR if available else "#f0f0f0",
                bd=0,
                relief="solid",
                padx=15,
                pady=15,
                highlightthickness=3,
                highlightbackground=BORDER_COLOR if available else "#c0c0c0"
            )
            card.grid(row=idx // cols, column=idx % cols, padx=25, pady=25)

            # ---------- IMAGE ----------
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_dir = os.path.join(base_dir, "images")
            img_path = os.path.join(img_dir, item.get("image_path") or "default.png")

            try:
                img = Image.open(img_path).resize((130, 130))
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"[Warning] Could not load image for {item['name']}: {e}")
                placeholder = Image.new("RGB", (130, 130), "#dcdde1")  # soft gray fallback
                photo = ImageTk.PhotoImage(placeholder)

            img_label = tk.Label(card, image=photo, bg=BG_COLOR if available else "#f0f0f0")
            img_label.image = photo
            img_label.pack(pady=5)

            # ---------- ITEM INFO ----------
            name_label = tk.Label(
                card,
                text=item["name"],
                font=("Segoe UI", 13, "bold"),
                bg=BG_COLOR if available else "#f0f0f0",
                fg=PRIMARY_COLOR if available else "#a0a0a0"
            )
            name_label.pack()

            stock_label = tk.Label(
                card,
                text=f"Stock: {stock}",
                font=("Segoe UI", 10),
                bg=BG_COLOR if available else "#f0f0f0",
                fg="#2c3e50" if available else "#b0b0b0"
            )
            stock_label.pack(pady=5)
            # ---------- OUT OF STOCK LABEL ----------
            if stock <= 0:
                out_label = tk.Label(
                    card,
                    text="OUT OF STOCK",
                    font=("Segoe UI", 11, "bold"),
                    fg="#b22222",   # 🔴 softer maroon-red tone
                    bg="#f0f0f0",
                    anchor="center",
                    justify="center"
                )
                out_label.pack(pady=(2, 8))

            # ---------- DROPDOWN ----------
            qty_var = tk.StringVar(value="1")
            if available:
                from tkinter import ttk
                qty_values = [str(i) for i in range(1, stock + 1)]
                qty_dropdown = ttk.Combobox(
                    card,
                    textvariable=qty_var,
                    values=qty_values,
                    width=5,
                    state="readonly",
                    justify="center"
                )
                qty_dropdown.pack(pady=5)
            else:
                qty_dropdown = None

            # ---------- SELECTION LOGIC ----------
            selected_state = {"selected": False}

            def toggle_select(event, c=card, it=item, qv=qty_var, st=selected_state, is_avail=available):
                if not is_avail:
                    return
                if not st["selected"]:
                    c.config(highlightbackground=ACCENT_COLOR)
                    st["selected"] = True
                    selected_items.append({
                        "name": it["name"],
                        "qty": qv,
                        "selected": True
                    })
                else:
                    c.config(highlightbackground=BORDER_COLOR)
                    st["selected"] = False
                    selected_items[:] = [s for s in selected_items if s["name"] != it["name"]]

        # ---------- BIND EVENTS ----------
            if available:
                # ✅ Bind clicks only for available items
                card.bind("<Button-1>", toggle_select)
                for child in card.winfo_children():
                    child.bind("<Button-1>", toggle_select)
                    child.bind("<ButtonRelease-1>", toggle_select)


    # ---------- ADD SELECTED TO CART ----------
    def add_selected_to_cart():
        chosen = [i for i in selected_items if i["selected"]]
        if not chosen:
            messagebox.showwarning("No Selection", "Please select at least one item.", parent=win)
            return

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        added_count = 0

        for i in chosen:
            item_name = i["name"]
            qty = int(i["qty"].get())

            # ✅ Special handling for Consumables
            if category.lower() == "consumables":
                # Fetch the single consumable record
                cursor.execute("""
                    SELECT id FROM items 
                    WHERE name=%s AND category=%s
                    LIMIT 1
                """, (item_name, category))
                row = cursor.fetchone()

                if not row:
                    messagebox.showerror("Error", f"Item '{item_name}' not found in database.", parent=win)
                    continue

                item_id = row["id"]

                # ✅ Check if item already exists in the cart for this user
                cursor.execute("""
                    SELECT id, quantity FROM cart
                    WHERE user_id=%s AND item_id=%s
                    LIMIT 1
                """, (user["id"], item_id))
                existing = cursor.fetchone()

                if existing:
                    # ✅ Update the quantity (add to existing)
                    new_qty = int(existing["quantity"]) + qty
                    cursor.execute("""
                        UPDATE cart
                        SET quantity = %s, added_at = NOW()
                        WHERE id = %s
                    """, (new_qty, existing["id"]))
                else:
                    # ✅ Insert as new record
                    cursor.execute("""
                        INSERT INTO cart (user_id, item_id, quantity, added_at)
                        VALUES (%s, %s, %s, NOW())
                    """, (user["id"], item_id, qty))

                added_count += qty

            else:
                # ✅ Keep existing logic for Equipment / Networking
                cursor.execute("""
                    SELECT id FROM items 
                    WHERE name=%s AND status IN ('available', 'partially_reserved')
                    LIMIT %s
                """, (item_name, qty))
                ids = cursor.fetchall()

                for row in ids:
                    cursor.execute("""
                        INSERT INTO cart (user_id, item_id, quantity, added_at)
                        VALUES (%s, %s, 1, NOW())
                    """, (user["id"], row["id"]))
                    added_count += 1

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"{added_count} item(s) added to cart successfully!", parent=win)
        load_items()


    load_items()


# ---------------- MY CART ---------------- #
def open_cart_window(parent_win, user):
    """Display user's cart with quantity, remove, and borrow controls."""
    import tkinter as tk
    from tkinter import ttk, messagebox
    from db import get_connection
    import os
    from PIL import Image, ImageTk

    # ===== COLOR PALETTE =====
    PRIMARY_COLOR = "#800000"   # Maroon
    ACCENT_COLOR = "#510400"    # Gold
    BG_COLOR = "#FFFFFF"        # White
    PANEL_COLOR = "#F4F4F4"     # Light Gray
    TEXT_COLOR = "#800000"      # Maroon Text
    DANGER_COLOR = "#800000"    # Dark Red for Remove Button

    # ===== WINDOW SETUP =====
    cart_win = tk.Toplevel(parent_win)
    cart_win.title(f"🛒 My Cart - {user.get('name', '')}")
    cart_win.attributes("-fullscreen", True)
    cart_win.configure(bg=BG_COLOR)

    # ===== HEADER =====
    header = tk.Frame(cart_win, bg=PRIMARY_COLOR)
    header.pack(fill="x")
    tk.Label(
        header,
        text=f"🛒 My Cart - {user.get('name', '')}",
        font=("Segoe UI", 20, "bold"),
        bg=PRIMARY_COLOR,
        fg="white",
        pady=12
    ).pack()

    # ===== BODY =====
    body = tk.Frame(cart_win, bg=BG_COLOR)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    # LEFT SIDE (Scrollable Items)
    left = tk.Frame(body, bg=BG_COLOR)
    left.pack(side="left", fill="both", expand=True)

    canvas = tk.Canvas(left, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(left, orient="vertical", command=canvas.yview)
    list_frame = tk.Frame(canvas, bg=BG_COLOR)
    canvas.create_window((0, 0), window=list_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # RIGHT SIDE (Summary + Buttons)
    right = tk.Frame(body, width=320, bg=PANEL_COLOR, highlightthickness=2, highlightbackground="#E0E0E0")
    right.pack(side="right", fill="y")

    summary_label = tk.Label(
        right,
        text="0 selected — Total quantity: 0",
        font=("Segoe UI", 13, "bold"),
        bg=PANEL_COLOR,
        fg=TEXT_COLOR
    )
    summary_label.pack(pady=20)

    # ===== STYLED BUTTON FUNCTION =====
    def styled_button(parent, text, color, cmd):
        return tk.Button(
            parent,
            text=text,
            bg=color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=20,
            height=2,
            relief="flat",
            cursor="hand2",
            activebackground=ACCENT_COLOR,
            activeforeground=PRIMARY_COLOR,
            command=cmd
        )

    selected = {}
    select_all_state = tk.BooleanVar(value=False)

    # ===== SUMMARY UPDATE =====
    def update_summary():
        total_selected = 0
        total_qty = 0
        for cid, info in selected.items():
            val = info["var"]
            checked = val.get() if hasattr(val, "get") else val
            if checked:
                qty_val = info["qty"]
                qty = int(qty_val.get()) if hasattr(qty_val, "get") else int(qty_val)
                total_selected += 1
                total_qty += qty
        summary_label.config(text=f"{total_selected} selected — Total quantity: {total_qty}")

        # Update select all button appearance
        if selected:
            all_selected = all(
                (info["var"].get() if hasattr(info["var"], "get") else info["var"])
                for info in selected.values()
            )
        else:
            all_selected = False
        select_all_state.set(all_selected)
        toggle_select_btn.config(
            text="Unselect All" if all_selected else "Select All",
            bg=ACCENT_COLOR if all_selected else PRIMARY_COLOR,
            fg=PRIMARY_COLOR if all_selected else "white"
        )

    # ===== LOAD CART =====
    def load_cart():
        nonlocal selected
        selected = {}
        for w in list_frame.winfo_children():
            w.destroy()
        update_summary()

        conn = get_connection()
        if not conn:
            messagebox.showerror("DB Error", "Cannot connect to database.", parent=cart_win)
            return

        cur = conn.cursor(dictionary=True)
        cur.execute("""
        SELECT 
            MIN(c.id) AS cart_id,
            MIN(i.id) AS item_id,
            i.name,
            i.category,
            i.image_path,
            SUM(c.quantity) AS quantity,
            CASE 
                WHEN i.category = 'Consumables' THEN 
                    (SELECT SUM(stock) FROM items AS ii WHERE ii.name = i.name AND ii.category = i.category)
                ELSE 
                    (SELECT COUNT(*) FROM items AS ii 
                    WHERE ii.name = i.name AND ii.category = i.category
                    AND ii.status IN ('available', 'partially_reserved'))
            END AS stock
        FROM cart c
        JOIN items i ON c.item_id = i.id
        WHERE c.user_id = %s
        GROUP BY i.name, i.category, i.image_path
        ORDER BY i.name ASC
    """, (user["id"],))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            tk.Label(list_frame, text="Your cart is empty.", font=("Segoe UI", 14, "italic"),
                     bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=30)
            return

        for r in rows:
            cart_id = r["cart_id"]
            name = r["name"]
            stock = int(r["stock"] or 0)
            qty = int(r["quantity"] or 1)
            img_file = r["image_path"]
            available = stock > 0

            # CARD
            card = tk.Frame(
                list_frame,
                bg=BG_COLOR if available else PANEL_COLOR,
                relief="solid",
                padx=10,
                pady=10,
                highlightthickness=3,
                highlightbackground="#DCDCDC"
            )
            card.pack(fill="x", pady=6, padx=8)

            # LEFT IMAGE
            leftc = tk.Frame(card, bg=BG_COLOR)
            leftc.pack(side="left", padx=8, pady=8)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            img_path = os.path.join(base_dir, "images", img_file or "default.png")
            try:
                img = Image.open(img_path).resize((80, 80))
                photo = ImageTk.PhotoImage(img)
            except Exception:
                placeholder = Image.new("RGB", (80, 80), "gray")
                photo = ImageTk.PhotoImage(placeholder)
            thumbnail = tk.Label(leftc, image=photo, bg=BG_COLOR)
            thumbnail.image = photo
            thumbnail.pack()

            # CENTER
            center = tk.Frame(card, bg=BG_COLOR)
            center.pack(side="left", fill="x", expand=True, padx=10)
            tk.Label(center, text=name, font=("Segoe UI", 12, "bold"),
                     bg=BG_COLOR, fg=TEXT_COLOR, anchor="w").pack(fill="x")
            tk.Label(center, text=f"Stock: {stock}  |  In Cart: {qty}",
                     bg=BG_COLOR, fg="#145A32" if available else "#A10000",
                     font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(3, 0))

            # RIGHT
            rightc = tk.Frame(card, bg=BG_COLOR)
            rightc.pack(side="right", padx=10, pady=8)
            qty_var = tk.StringVar(value=str(qty))
            qty_dropdown = ttk.Combobox(rightc, textvariable=qty_var,
                                        values=[str(i) for i in range(1, max(1, stock) + 1)],
                                        width=5, state="readonly")
            qty_dropdown.pack(side="left", padx=5)
            qty_dropdown.bind("<<ComboboxSelected>>", lambda e: update_summary())

            def remove_this(cid=cart_id, n=name):
                if not messagebox.askyesno("Confirm", f"Remove {n}?", parent=cart_win):
                    return
                conn = get_connection()
                if conn:
                    cur2 = conn.cursor()
                    cur2.execute("DELETE FROM cart WHERE id=%s", (cid,))
                    conn.commit()
                    cur2.close()
                    conn.close()
                load_cart()

            tk.Button(rightc, text="Remove", bg=DANGER_COLOR, fg="white",
                      font=("Segoe UI", 10, "bold"), relief="flat",
                      activebackground=ACCENT_COLOR, activeforeground=PRIMARY_COLOR,
                      command=remove_this).pack(side="left", padx=6)

            # SELECTION
            selected_state = {"selected": False}
            def toggle_select(event=None, c=card, cid=cart_id, qv=qty_var, n=name):
                if not available:
                    return
                if not selected_state["selected"]:
                    c.config(highlightbackground=ACCENT_COLOR)
                    selected_state["selected"] = True
                    selected[cid] = {"var": True, "qty": qv, "item_id": r["item_id"], "name": n}
                else:
                    c.config(highlightbackground="#DCDCDC")
                    selected_state["selected"] = False
                    if cid in selected:
                        del selected[cid]
                update_summary()

            if available:
                card.bind("<Button-1>", toggle_select)
                for child in card.winfo_children():
                    child.bind("<Button-1>", toggle_select)
                    child.bind("<ButtonRelease-1>", toggle_select)

            update_summary()

            # ✅ Hover effect (for desktop)
            def on_hover(event, c=card):
                if available and not selected_state["selected"]:
                    c.config(highlightbackground="#a3e4a7")

            def on_leave(event, c=card):
                if available and not selected_state["selected"]:
                    c.config(highlightbackground="#dcdde1")

            if available:
                card.bind("<Enter>", on_hover)
                card.bind("<Leave>", on_leave)

        update_summary()


    def toggle_select_all():
        new_state = not select_all_state.get()
        select_all_state.set(new_state)
        for widget in list_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(highlightbackground=ACCENT_COLOR if new_state else "#DCDCDC")
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                MIN(c.id) AS cart_id,
                MIN(i.id) AS item_id,
                i.name,
                SUM(c.quantity) AS quantity
            FROM cart c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = %s
            GROUP BY i.name
        """, (user["id"],))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        selected.clear()
        if new_state:
            for r in rows:
                qty_var = tk.StringVar(value=str(r["quantity"]))
                selected[r["cart_id"]] = {"var": True, "qty": qty_var, "item_id": r["item_id"], "name": r["name"]}
        update_summary()

    def request_borrow():
        chosen = [info for _, info in selected.items() if (info["var"].get() if hasattr(info["var"], "get") else info["var"])]
        if not chosen:
            messagebox.showwarning("No selection", "Select items to request borrow.", parent=cart_win)
            return
        conn = get_connection()
        cur = conn.cursor()
        added = 0
        for _, info in selected.items():
            if (info["var"].get() if hasattr(info["var"], "get") else info["var"]):
                qty = int(info["qty"].get())
                for _ in range(qty):
                    cur.execute("""
                        INSERT INTO transactions (user_id, item_id, type, status, created_at)
                        VALUES (%s, %s, 'borrow', 'pending', NOW())
                    """, (user["id"], info["item_id"]))
                    added += 1
                cur.execute("DELETE FROM cart WHERE user_id=%s AND item_id=%s", (user["id"], info["item_id"]))
                
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Borrow Request", f"{added} item(s) sent for approval.", parent=cart_win)
        load_cart()

    def remove_selected():
        to_remove = [cid for cid, info in selected.items() if info.get("var") and (info["var"].get() if hasattr(info["var"], "get") else info["var"])]
        if not to_remove:
            messagebox.showinfo("Notice", "Select items to remove first.", parent=cart_win)
            return
        conn = get_connection()
        cur = conn.cursor()
        for cid in to_remove:
            cur.execute("DELETE FROM cart WHERE id = %s", (cid,))
        conn.commit()
        cur.close()
        conn.close()
        load_cart()

    def clear_all():
        if not messagebox.askyesno("Clear All", "Remove all items from your cart?", parent=cart_win):
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE user_id = %s", (user["id"],))
        conn.commit()
        cur.close()
        conn.close()
        load_cart()

    # ===== BUTTONS =====
    toggle_select_btn = styled_button(right, "Select All", PRIMARY_COLOR, toggle_select_all)
    toggle_select_btn.pack(pady=8)
    styled_button(right, "Send Borrow Request", PRIMARY_COLOR, request_borrow).pack(pady=8)
    styled_button(right, "Remove Selected", PRIMARY_COLOR, remove_selected).pack(pady=8)
    styled_button(right, "Clear All", PRIMARY_COLOR, clear_all).pack(pady=8)
    styled_button(right, "Close", PRIMARY_COLOR, cart_win.destroy).pack(pady=8)

    # Faculty Extras
    if "faculty" in user.get("role", "").lower():
        try:
            from faculty_dashboard import open_reserve_cart
            styled_button(right, "🗓 Reserve Cart", PRIMARY_COLOR,
                          lambda: [cart_win.destroy(), open_reserve_cart(parent_win, user)]).pack(pady=8)
        except ImportError:
            print("[Warning] Could not import open_reserve_cart.")

    load_cart()


def open_return_items(root, user):
    import tkinter as tk
    from tkinter import ttk, messagebox
    from db import get_connection
    import os
    from PIL import Image, ImageTk

    # ====== COLOR PALETTE ======
    PRIMARY_COLOR = "#800000"   # Maroon
    ACCENT_COLOR = "#510400"    # Gold
    BG_COLOR = "#FFFFFF"        # White
    TEXT_COLOR = "#800000"
    SUBTEXT_COLOR = "#7f8c8d"
    BORDER_DEFAULT = "#dcdde1"

    # ====== WINDOW SETUP ======
    return_win = tk.Toplevel()
    return_win.title("Return Items")
    return_win.attributes("-fullscreen", True)
    return_win.configure(bg=BG_COLOR)

    # ====== HEADER ======
    header = tk.Frame(return_win, bg=PRIMARY_COLOR)
    header.pack(fill="x")

    tk.Label(
        header,
        text="📦 Return Borrowed Items",
        font=("Segoe UI", 26, "bold"),
        bg=PRIMARY_COLOR,
        fg="white",
        pady=15
    ).pack(side="left", padx=30)

    # ====== BODY FRAME ======
    body_frame = tk.Frame(return_win, bg=BG_COLOR)
    body_frame.pack(fill="both", expand=True)

    # ====== LEFT SIDE (ITEM GRID) ======
    canvas = tk.Canvas(body_frame, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(body_frame, orient="vertical", command=canvas.yview)
    store_frame = tk.Frame(canvas, bg=BG_COLOR)
    canvas.create_window((0, 0), window=store_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    store_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="left", fill="y")
    
    canvas.bind("<Button-1>", lambda e: "break")  # ✅ stops the canvas from stealing clicks

    # ====== RIGHT PANEL (BUTTONS) ======
    right_panel = tk.Frame(body_frame, width=400, bg="#f7f7f7", highlightthickness=1, highlightbackground="#e0e0e0")
    right_panel.pack(side="right", fill="y")

    # Utility: Styled buttons
    def styled_button(parent, text, color, command, icon=None):
        return tk.Button(
            parent,
            text=f"{icon or ''} {text}",
            bg=color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            width=18,
            height=2,
            relief="flat",
            cursor="hand2",
            activebackground=ACCENT_COLOR,
            activeforeground=PRIMARY_COLOR,
            command=command
        )

    # Global selection list
    selected_items = []
    all_selected_state = tk.BooleanVar(value=False)

    # ====== LOAD BORROWED ITEMS ======
    def load_borrowed():
        for w in store_frame.winfo_children():
            w.destroy()
        selected_items.clear()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.id AS trans_id, i.id AS item_id, i.name, i.image_path, t.created_at, t.status
            FROM transactions t
            JOIN items i ON t.item_id = i.id
            WHERE t.user_id=%s AND t.status='released' AND i.category != 'Consumables'
            ORDER BY t.created_at DESC
        """, (user["id"],))
        borrowed = cursor.fetchall()
        cursor.close()
        conn.close()

        if not borrowed:
            tk.Label(
                store_frame,
                text="No released items to return yet.",
                font=("Segoe UI", 18, "italic"),
                bg=BG_COLOR,
                fg=SUBTEXT_COLOR
            ).pack(pady=80)
            return

        columns = 4
        for i, item in enumerate(borrowed):
            card = tk.Frame(
                store_frame,
                bg=BG_COLOR,
                bd=2,
                relief="solid",
                highlightthickness=2,
                highlightbackground=BORDER_DEFAULT
            )
            card.grid(row=i // columns, column=i % columns, padx=20, pady=20)

            # Load image safely
            img_path = os.path.join("images", item.get("image_path") or "default.png")
            try:
                img = Image.open(img_path).resize((150, 150))
                photo = ImageTk.PhotoImage(img)
            except:
                photo = ImageTk.PhotoImage(Image.new("RGB", (150, 150), "gray"))

            img_label = tk.Label(card, image=photo, bg=BG_COLOR)
            img_label.image = photo
            img_label.pack(pady=10)

            # Item info
            tk.Label(
                card, text=item["name"],
                font=("Segoe UI", 14, "bold"),
                bg=BG_COLOR,
                fg=TEXT_COLOR
            ).pack()

            tk.Label(
                card, text=f"Released: {item['created_at']:%Y-%m-%d}",
                font=("Segoe UI", 11),
                bg=BG_COLOR,
                fg=SUBTEXT_COLOR
            ).pack(pady=5)

            tk.Label(
                card, text=f"Status: {item['status'].capitalize()}",
                font=("Segoe UI", 11, "bold"),
                bg=BG_COLOR,
                fg="#16a085"
            ).pack(pady=5)

            # --- Selection behavior ---
            selected_state = {"selected": False}

            def toggle_select(event=None, c=card, data=item):
                if not selected_state["selected"]:
                    c.config(highlightbackground=PRIMARY_COLOR)
                    selected_items.append(data)
                    selected_state["selected"] = True
                else:
                    c.config(highlightbackground=BORDER_DEFAULT)
                    if data in selected_items:
                        selected_items.remove(data)
                    selected_state["selected"] = False

            # Bind click to select/deselect
            card.bind("<Button-1>", toggle_select)
            for child in card.winfo_children():
                child.bind("<Button-1>", toggle_select)

    # ====== SELECT ALL / UNSELECT ALL ======
    def toggle_select_all():
        nonlocal selected_items
        if all_selected_state.get():
            # Unselect all
            all_selected_state.set(False)
            for w in store_frame.winfo_children():
                if isinstance(w, tk.Frame):
                    w.config(highlightbackground=BORDER_DEFAULT)
            selected_items.clear()
        else:
            # Select all
            all_selected_state.set(True)
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id AS trans_id, i.id AS item_id, i.name, i.image_path, t.created_at, t.status
                FROM transactions t
                JOIN items i ON t.item_id = i.id
                WHERE t.user_id=%s AND t.status='released' AND i.category != 'Consumables'
            """, (user["id"],))
            selected_items = cursor.fetchall()
            cursor.close()
            conn.close()
            for w in store_frame.winfo_children():
                if isinstance(w, tk.Frame):
                    w.config(highlightbackground=PRIMARY_COLOR)

        select_all_btn.config(
            text="Unselect All" if all_selected_state.get() else "Select All"
        )

    # ====== SEND RETURN REQUEST ======
    def send_return_request():
        if not selected_items:
            messagebox.showinfo("No Selection", "Please select at least one item to return.", parent=return_win)
            return

        confirm = messagebox.askyesno("Confirm Return", f"Send return request for {len(selected_items)} item(s)?", parent=return_win)
        if not confirm:
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            for i in selected_items:
                    cursor.execute("""
                        INSERT INTO transactions (user_id, item_id, type, status, created_at)
                        VALUES (%s, %s, 'return', 'pending', NOW())
                    """, (user["id"], i["item_id"]))
                    conn.commit()

                    # Mark the original borrow record as return_pending
                    cursor.execute("""
                        UPDATE transactions
                        SET status = 'return_pending',
                            updated_at = NOW()
                        WHERE id = %s
                    """, (i["trans_id"],))
                    conn.commit()

                    messagebox.showinfo(
                        "Success",
                        f"Return request for '{i['name']}' has been sent to the admin.",
                        parent=return_win
                    )
                    load_borrowed()  # refresh list after request

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to send return requests: {e}", parent=return_win)
        finally:
            cursor.close()
            conn.close()

    # ====== AUTO REFRESH ======
    def auto_refresh():
        load_borrowed()
        return_win.after(10000, auto_refresh)

    # ====== RIGHT PANEL BUTTONS ======
    styled_button(right_panel, "🌀 Refresh", PRIMARY_COLOR, load_borrowed).pack(pady=15)
    select_all_btn = styled_button(right_panel, "Select All", "#800000", toggle_select_all)
    select_all_btn.pack(pady=15)
    styled_button(right_panel, "📤 Send Return Request", "#800000", send_return_request).pack(pady=15)
    styled_button(right_panel, "⬅ Back", "#800000", lambda: [return_win.destroy(), open_user_dashboard(root, user)]).pack(pady=15)

    # ====== INITIAL LOAD ======
    load_borrowed()
    auto_refresh()


# ---------------- HISTORY (Borrow + Return) ---------------- #
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

    notebook = ttk.Notebook(hist_win)
    notebook.pack(fill="both", expand=True, padx=20, pady=20)

    # Borrow History
    borrow_frame = tk.Frame(notebook, bg="#ecf0f1")
    notebook.add(borrow_frame, text="Borrow History")

    cols = ("id", "item", "status", "created_at")
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
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        status_labels = {
            "pending": "⏳ Pending Approval",
            "approved": "✅ Approved",
            "rejected": "❌ Rejected",
            "released": "📦 Released",
            "borrowed": "🔧 Borrowed",
            "returned": "↩ Returned",
            "return_pending": "🕓 Return Pending",
            "return_approved": "✔ Return Approved",
            "return_rejected": "❌ Return Rejected"
        }

        if not rows:
            borrow_tree.insert("", "end", values=("", "No borrow history available", "", ""))
            return

        for r in rows:
            status_display = status_labels.get(r["status"], r["status"].capitalize())
            borrow_tree.insert("", "end", values=(r["id"], r["name"], status_display, r["created_at"]))

    load_borrow_history()

    # Return History
    return_frame = tk.Frame(notebook, bg="#ecf0f1")
    notebook.add(return_frame, text="Return History")

    cols = ("id", "item", "status", "created_at")
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
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        status_labels = {
            "pending": "⏳ Pending Approval",
            "approved": "✅ Approved",
            "rejected": "❌ Rejected",
            "released": "📦 Released",
            "borrowed": "🔧 Borrowed",
            "returned": "↩ Returned",
            "return_pending": "🕓 Return Pending",
            "return_approved": "✔ Return Approved",
            "return_rejected": "❌ Return Rejected"
        }
        
        if not rows:
            return_tree.insert("", "end", values=("", "No return history available", "", ""))
            return

        for r in rows:
            status_display = status_labels.get(r["status"], r["status"].capitalize())
            return_tree.insert("", "end", values=(r["id"], r["name"], status_display, r["created_at"]))

    load_return_history()


    tk.Button(hist_win, text="⬅ Back", bg="#800000", fg="white",
              font=("Arial", 14, "bold"), width=20,
              command=hist_win.destroy).pack(pady=15)
