import os
import socket
import sys
from flask import Flask, request, redirect, render_template_string, send_from_directory

app = Flask(__name__)

# PyInstaller ke liye base path
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Track connected devices (IP + user-agent)
connected_devices = {}

ICONS = {
    ".txt": "📄", ".pdf": "📕", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️",
    ".mp4": "🎬", ".mp3": "🎵", ".zip": "🗜️", ".py": "🐍",
    ".cpp": "💻", ".c": "💻", ".js": "🌐", ".html": "🌐", ".css": "🎨",
}

def get_icon(filename):
    ext = os.path.splitext(filename)[-1].lower()
    return ICONS.get(ext, "📁")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShareHub</title>
    <style>
        body { margin: 0; font-family: system-ui; background: #0f172a; color: white; }
        header { text-align: center; padding: 20px; border-bottom: 1px solid #334155; }
        header h1 { margin: 0; font-size: 24px; }
        .ip { font-size: 12px; color: #94a3b8; }
        main { max-width: 600px; margin: auto; padding: 20px; }
        .step { font-size: 14px; margin-bottom: 8px; color: #cbd5e1; }
        form { border: 2px dashed #38bdf8; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; }
        input[type="file"] { margin: 10px 0; color: white; }
        button { background: #38bdf8; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: 500; }
        .file { display: flex; justify-content: space-between; align-items: center; background: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 10px; transition: 0.2s; }
        .file:hover { transform: scale(1.02); }
        .file p { margin: 0; }
        a.dl { background: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; color: black; font-size: 14px; }
        .devices { margin-top: 25px; padding-top: 10px; border-top: 1px solid #334155; }
        .device { font-size: 14px; margin-top: 5px; color: #cbd5e1; }
        .flash { background: #166534; color: #bbf7d0; padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 14px; }
        .empty { color: #475569; font-size: 14px; }
    </style>
    <script src="https://code.iconify.design/3/3.1.0/iconify.min.js"></script>
</head>
<body>
    <header>
        <h1>ShareHub</h1>
        <p class="ip">{{ local_ip }}:5000</p>
    </header>
    <main>
        {% if message %}
        <div class="flash">{{ message }}</div>
        {% endif %}

        <section>
            <p class="step">Upload File</p>
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <p>Select a file to share</p>
                <input type="file" name="file">
                <br>
                <button type="submit">Upload</button>
            </form>
        </section>

        <section>
            <p class="step">Available Files</p>
            {% if files %}
                {% for f in files %}
                <article class="file">
                    <p>{{ get_icon(f) }} {{ f }}</p>
                    <a class="dl" href="/download/{{ f }}">
                      <span class="iconify" data-icon="line-md:download-outline"></span>
                    Download
                    </a>
                </article>
                <form action="/delete/{{ f }}" method="POST" style="border:none;padding:0;margin:0;">
               
    <button type="submit" style="style=text-align: right;"> <span class="iconify" data-icon="weui:delete-on-filled" style="font-size: 15px;"></span></button>
</form>
                {% endfor %}
            {% else %}
                <p class="empty">No files uploaded yet.</p>
            {% endif %}
        </section>

        <section class="devices">
            <p class="step">Connected Devices</p>
            {% if devices %}
                {% for ip, ua in devices.items() %}
                <p class="device">📱 {{ ip }} — {{ ua[:40] }}</p>
                {% endfor %}
            {% else %}
                <p class="empty">No other devices connected.</p>
            {% endif %}
        </section>
    </main>
</body>
</html>
"""

@app.before_request
def track_device():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent", "Unknown")
    connected_devices[ip] = ua

@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    local_ip = get_local_ip()
    return render_template_string(
        TEMPLATE,
        files=files,
        local_ip=local_ip,
        devices=connected_devices,
        get_icon=get_icon,
        message=request.args.get("msg")
    )

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect("/?msg=No file selected.")
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(f"/?msg='{file.filename}' uploaded successfully!")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Delete file options
@app.route("/delete/<filename>",methods=['POST'])
def delete(filename):
    file_path=os.path.join(UPLOAD_FOLDER,filename)
    os.remove(file_path)
    return redirect("/?msg=File deleted!")


if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n🚀 ShareHub running at http://{local_ip}:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=True)