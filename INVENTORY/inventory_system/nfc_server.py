from flask import Flask, request, render_template_string, redirect, url_for, flash
from db import get_connection  # your existing database function

app = Flask(__name__)
app.secret_key = "secret123"  # for flash messages

# ============================
# 🔹 HTML Template with PWA setup
# ============================
template = """
<!DOCTYPE html>
<html lang="en">
<head>
<link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">

<link rel="manifest" href="/site.webmanifest">
  <title>Add Item (NFC)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then(() => console.log('✅ Service worker registered.'))
      .catch(err => console.error('Service worker failed:', err));
  }
</script>


  <style>
    body { font-family: Arial; background:#ecf0f1; padding:20px; text-align:center; }
    input, select { font-size:18px; padding:10px; width:90%; margin:8px; border-radius:8px; border:1px solid #ccc; }
    button { font-size:18px; background:#27ae60; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer; }
    button:hover { background:#2ecc71; }
    .msg { color:green; font-weight:bold; }
  </style>
</head>
<body>
  <h2>📱 Add Item via NFC</h2>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <div class="msg">{{ messages[0] }}</div>
    {% endif %}
  {% endwith %}
  <form action="/add_item" method="post">
    <input type="text" name="name" placeholder="Item Name" required><br>
    <select name="category" required>
      <option value="">Select Category</option>
      <option>Electronics</option>
      <option>Networking</option>
      <option>Consumables</option>
      <option>Tools</option>
    </select><br>
    <input type="number" name="quantity" placeholder="Quantity" required><br>
    <input type="text" name="rfid" id="rfid" placeholder="Tap NFC tag..." value="{{ rfid_value or '' }}" required><br>
    <button type="submit">Add Item</button>
  </form>
  <script>
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Automatically show prompt after a short delay
    setTimeout(() => {
      deferredPrompt.prompt();
    }, 3000);
  });
</script>

</body>
</html>
"""

# ============================
# 🔹 Flask routes
# ============================
@app.route("/", methods=["GET"])
def home():
    return redirect("/add_item")

@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    rfid_value = request.args.get("rfid") or request.form.get("rfid")
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        qty = request.form.get("quantity")
        rfid = request.form.get("rfid")

        if not (name and category and qty and rfid):
            flash("All fields are required.")
            return redirect(url_for("add_item"))

        conn = get_connection()
        if not conn:
            flash("Database connection failed.")
            return redirect(url_for("add_item"))
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO items (name, category, stock, status, image_path, rfid_code)
                   VALUES (%s, %s, %s, 'available', NULL, %s)""",
                (name, category, qty, rfid)
            )
            conn.commit()
            flash(f"Item '{name}' added successfully with tag {rfid}!")
        except Exception as e:
            flash(f"Database error: {e}")
        finally:
            cur.close()
            conn.close()

        return redirect(url_for("add_item"))

    return render_template_string(template, rfid_value=rfid_value)

# ============================
# 🔹 Run server for mobile access
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
