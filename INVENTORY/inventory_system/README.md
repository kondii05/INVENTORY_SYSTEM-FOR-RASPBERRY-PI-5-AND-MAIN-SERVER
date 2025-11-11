# Inventory Management System (MySQL + bcrypt)

## Setup
1. Install dependencies:
   ```bash
   pip install mysql-connector-python bcrypt reportlab
   ```

2. Create database in MySQL (via XAMPP Shell or phpMyAdmin):
   ```sql
   CREATE DATABASE inventory_db;
   USE inventory_db;
   ```

3. Import schema.sql via phpMyAdmin or MySQL:
   - In phpMyAdmin, select database -> Import -> Choose `data/schema.sql` -> Go

4. Create admin/user/faculty accounts with bcrypt password hashes:
   ```python
   import bcrypt
   pw = "admin123"
   print(bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode())
   ```

   Insert the hash into MySQL:
   ```sql
   INSERT INTO users (name, rfid_code, password, role)
   VALUES ('System Admin', 'ADMIN001', '<hash_here>', 'admin');
   ```

5. Update db.py with your database credentials (if not using inventory_user/invpass123).

6. Run the application:
   ```bash
   python login.py
   ```
