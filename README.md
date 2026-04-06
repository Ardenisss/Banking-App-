# 🏦 Banking App

A desktop banking application built with Python and Kivy, designed to resemble a modern mobile banking experience. The app uses Google Firebase for secure authentication and real-time data management.

> ⚠️ This project is currently in active development. Features are being added progressively.

---

## 📸 Screenshots

### Login
<img width="1919" height="1021" alt="Screenshot 2026-04-04 130721" src="https://github.com/user-attachments/assets/f6499893-7255-44d3-9e8b-6ca7e1ddc794" />

### Sign Up
<p align="center">
  <img src="https://github.com/user-attachments/assets/19d269e5-07a5-47ce-9006-b2701efd3f6f" width="45%" />
  <img src="https://github.com/user-attachments/assets/b79854b9-67e8-435c-8d17-55b4e578bf2a" width="45%" />
</p>

### Reset Password
<img width="1919" height="1019" alt="image" src="https://github.com/user-attachments/assets/670e566f-d365-4bb7-9bdb-7f2e34a20236" />

### Accounts Dashboard
<img width="1912" height="990" alt="Screenshot 2026-04-05 233022" src="https://github.com/user-attachments/assets/3481da58-0dbc-4143-8e82-92a82075a162" />

### Send Money Dashboard
<img width="1919" height="1017" alt="image" src="https://github.com/user-attachments/assets/110fca2c-9758-44f6-9ab9-0f14694c3f70" />

---

## ✅ Features (Current)

### Authentication
- **Sign Up** — Create a new account with email and password via Firebase Authentication
- **Login** — Secure login with credential validation and error handling
- **Forgot Password** — Password reset flow sent to the user's email through Firebase

### Dashboard (UI Preview)
- Account balance display
- Checking and Savings account sections
- Interactive buttons for future banking actions

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| UI Framework | Kivy |
| Backend / Auth | Google Firebase |
| Database | Firebase Firestore |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12
- pip

### Installation

```bash
# Clone the repo
git clone https://github.com/Ardenisss/banking-app.git
cd banking-app

# Install dependencies
pip install kivy firebase-admin
```

### Run the App

```bash
py -3.12 main.py
```

---

## 📁 Project Structure

```
banking-app/
│
├── main.py              # Entry point
├── login.py             # Login screen logic
├── signup.py            # Sign up screen logic
├── forgot_password.py   # Password reset logic
├── dashboard.py         # Main dashboard UI
└── firebase_config.py   # Firebase initialization
```

> Note: File structure may vary as the project grows.

---

## 🔮 Planned Features/Currently being worked on

- [ ] Transaction history
- [ ] Account settings

---

## 👤 Author

**Ardenis Del Rosario**
- GitHub: [@Ardenisss](https://github.com/Ardenisss)
- LinkedIn: [linkedin.com/in/ardenisd](https://linkedin.com/in/ardenisd)
