# 🎓RFID-Based Inventory and Borrowing System Using Raspberry Pi 5

A modern and efficient **Inventory and Borrowing Management System** developed as a **thesis project**.  
This system uses **RFID technology** integrated with a **Raspberry Pi 5** to manage item borrowing and returning securely and efficiently.  
It features a user-friendly **Python Tkinter GUI**, a **MySQL/SQLite database**, and an **admin dashboard** for monitoring item transactions in real time.

---

## 🧠 Project Overview

This project was developed to improve the manual process of borrowing and returning laboratory equipment and electronic components.  
Using **RFID cards**, users can log in, borrow items, and return them seamlessly.  
Administrators can monitor item availability, approve requests, view history logs, and manage inventory through a centralized interface.

The system can be deployed in multiple rooms using Raspberry Pi units, all connected to a shared database — allowing a **multi-device setup** (e.g., two Raspberry Pi stations for borrowing and one laptop for admin monitoring).

---

## ⚙️ Features

### 👤 User Side
- RFID-based login authentication  
- Borrow items by scanning RFID tags  
- Automatic item stock updates  
- Real-time return process via RFID scanning  
- View personal borrowing and return history  

### 🧩 Admin Side
- Dashboard overview of all items and requests  
- Approve or deny borrow requests  
- View and filter borrowing and return history  
- Manage users, items, and categories  
- Archive and restore items  
- Notifications after approval or rejection  

### 🖥️ System
- Multi-Raspberry Pi setup (borrow stations + admin monitoring)  
- Fullscreen GUI using Tkinter  
- Database integration with MySQL or SQLite  
- RFID reader and tag compatibility  

---

## 🛠️ Tech Stack

| Component | Technology Used |
|------------|----------------|
| Hardware | Raspberry Pi 5, RFID Reader/Tags |
| Programming Language | Python |
| GUI Framework | Tkinter |
| Database | MySQL or SQLite |
| Image Processing | Pillow (PIL) |
| OS | Raspberry Pi OS (Linux-based) |

---

