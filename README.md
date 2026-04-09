# 📡 ShareHub

> A lightweight local network file & note sharing web app built with Python + Flask.  
> No internet required. Just connect to the same WiFi and go.

---

## 🚀 What is ShareHub?

ShareHub is a LAN-based file sharing tool that runs on your machine and lets anyone on the same network upload, download, and share files or notes — just by scanning a QR code.

No cloud. No signup. No internet dependency.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📁 File Upload | Upload any file type from any device on the network |
| 📝 Note Sharing | Type and save notes directly from the browser |
| ⬇️ File Download | Download any shared file instantly |
| 🗑️ File Delete | Remove files from the shared folder |
| 📱 QR Code Connect | Scan QR to open ShareHub on any phone — no typing needed |
| 👥 Connected Devices | See which devices are currently connected |
| 🌐 Auto Browser Launch | Opens in browser automatically when app starts |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, Jinja2 (inline template)
- **Libraries:** `qrcode`, `Pillow`, `socket`, `threading`, `webbrowser`
- **Storage:** Local filesystem (`uploads/` folder)

---

## 📦 Installation

### 1. Clone or download the project

```bash
git clone https://github.com/yourname/sharehub.git
cd sharehub
```

### 2. Install dependencies

```bash
pip install flask qrcode[pil]
```

### 3. Run the app

```bash
python app.py
```

App will start at `http://<your-local-ip>:5000` and open automatically in your browser.

---

## 📲 How to Connect from Another Device

1. Make sure your phone/device is on the **same WiFi network** as the host machine
2. Scan the **QR code** shown in the app header
3. Or manually open `http://<shown-ip>:5000` in any browser

---

## 🗂️ Project Structure

```
sharehub/
├── app.py          ← Main Flask application
├── uploads/        ← All uploaded files stored here (auto-created)
└── README.md
```

---

## ⚙️ How It Works

```
Host runs app.py
      ↓
Flask starts on 0.0.0.0:5000 (listens on all interfaces)
      ↓
QR code generated with local IP
      ↓
Anyone on same network scans QR → opens ShareHub
      ↓
Upload files / notes → saved to uploads/ folder
      ↓
Anyone can download from Available Files section
```

---

## 📋 Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | Main page — shows files, upload forms, devices |
| `/upload` | POST | Upload a file |
| `/add_note` | POST | Save a text note as `.txt` file |
| `/download/<filename>` | GET | Download a file |
| `/delete/<filename>` | POST | Delete a file |
| `/qr` | GET | Returns QR code image of server URL |

---

## ⚠️ Requirements

- Python 3.7+
- All devices must be on the **same local network** (WiFi or Ethernet via same router)
- Internet not required for core functionality

---

## 🔮 Planned Features (v2)

- Role-based access control (admin vs guest)
- Per-file delete protection
- DBMS integration (SQLite3) for upload history and user tracking
- Cloudflare Tunnel support for internet-based sharing

---

## 👨‍💻 Built By

Made for IT Fest — demonstrating practical LAN networking with Python Flask.
