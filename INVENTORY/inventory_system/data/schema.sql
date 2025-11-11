DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rfid_code VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user','faculty','admin') NOT NULL DEFAULT 'user',
    section VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    type ENUM('borrow','reserve','return') NOT NULL,
    status ENUM('pending','approved','rejected','returned') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

INSERT INTO items (name, category, description, stock) VALUES
('Laptop', 'Electronics', 'Dell Inspiron 15', 10),
('Projector', 'Electronics', 'Epson XGA Projector', 5),
('HDMI Cable', 'Networking', 'High-speed HDMI cable 2m', 20),
('Router', 'Networking', 'TP-Link WiFi Router', 8),
('Screwdriver Set', 'Equipment', 'Set of 6 precision screwdrivers', 15),
('Multimeter', 'Equipment', 'Digital multimeter for electronics testing', 7);
