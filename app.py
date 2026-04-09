import os
import socket
import sys
import qrcode
import io
import webbrowser ## for open exe/bin as click autlaunch web
from threading import Timer
from flask import Flask, request, redirect\
    , render_template_string, send_from_directory,send_file

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
        
        /* NO-JS Fade Out Animation */
        @keyframes fadeAway {
            0% { opacity: 1; }
            80% { opacity: 1; }
            100% { opacity: 0; visibility: hidden; }
        }
        .flash { 
            background: #166534; color: #bbf7d0; padding: 10px 14px; 
            border-radius: 8px; margin-bottom: 16px; font-size: 14px;
            animation: fadeAway 2s forwards;
        }

        form { border: 2px dashed #38bdf8; padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; }
        input[type="file"], textarea { margin: 10px 0; color: white; width: 100%; box-sizing: border-box; }
        textarea { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 10px; color: white; font-family: inherit; }
        button { background: #38bdf8; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-weight: 500; }
        
        .file { 
            display: flex; justify-content: space-between; 
            align-items: center; background: #1e293b; padding: 12px; 
            border-radius: 8px; margin-bottom: 10px; gap: 8px; 
        }
        .file-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 14px; }
        .file-actions { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
        a.dl { background: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; color: black; font-size: 14px; }
        
        .devices { margin-top: 25px; padding-top: 10px; border-top: 1px solid #334155; }
        .device { font-size: 13px; margin-top: 5px; color: #94a3b8; }
        .empty { color: #475569; font-size: 14px; text-align: center; margin-top: 20px; }
    </style>
  <script src="https://code.iconify.design/3/3.1.0/iconify.min.js"></script>
</head>
<body>
    <header>
        <h1><span class="iconify" data-icon=hugeicons:shared-wifi></span> ShareHub</h1>
       <p class="ip"> <span class="iconify" data-icon=material-symbols:info></span> {{ local_ip }}:5000</p>
        <img src="/qr" height="50px" width="50px" alt="scan to connect">
    </header>
    <main>
        {% if message %}
        <div class="flash">{{ message }}</div>
        {% endif %}

        

        <section>
            <p class="step">Upload File</p>
            <form  action="/upload" method="POST" enctype="multipart/form-data">
                <p>Select a file to share</p>
                <input style=display: none;  type="file" name="file" id="fileInput">
                <br>
                <button type="submit" >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="18" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-dasharray="60" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 19h11c2.21 0 4 -1.79 4 -4c0 -2.21 -1.79 -4 -4 -4h-1v-1c0 -2.76 -2.24 -5 -5 -5c-2.42 0 -4.44 1.72 -4.9 4h-0.1c-2.76 0 -5 2.24 -5 5c0 2.76 2.24 5 5 5Z"><animate fill="freeze" attributeName="stroke-dashoffset" dur="0.6s" values="60;0"/></path><path fill="currentColor" d="M10.5 16h3v0h2.5l-4 0l-4 0h2.5Z"><animate fill="freeze" attributeName="d" begin="0.6s" dur="0.4s" keyTimes="0;0.4;1" 
                values="M10.5 16h3v0h2.5l-4 0l-4 0h2.5Z;M10.5 16h3v0h2.5l-4 -4l-4 4h2.5Z;M10.5 16h3v-3h2.5l-4 -4l-4 4h2.5Z"/></path></svg>Upload
                </button>
            </form>

        </section> 

        <section>
            <p class="step">Add Note</p>
            <form action="/add_note" method="POST">
                <textarea name="note_text" rows="3" placeholder="Write something and save..."></textarea>
                <button type="submit"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="18" viewBox="0 0 24 24"><path fill="#000" d="M3 21V3h18v8.7q-.475-.225-.975-.387T19 11.075V5H5v14h6.05q.075.55.238 1.05t.387.95zm2-3v1V5v6.075V11zm2-1h4.075q.075-.525.238-1.025t.362-.975H7zm0-4h6.1q.8-.75 1.788-1.25T17 11.075V11H7zm0-4h10V7H7zm11 14q-2.075 0-3.537-1.463T13 18t1.463-3.537T18 13t3.538 1.463T23 18t-1.463 3.538T18 23m-.5-2h1v-2.5H21v-1h-2.5V15h-1v2.5H15v1h2.5z"/></svg>Save Note</button>
            </form>
        </section>
        

        <section>
            <p class="step">Available Files</p>
            {% if files %}
                {% for f in files %}
                <article class="file">
                    <p class="file-name">{{ get_icon(f) }} {{ f }}</p>
                    <div class="file-actions">
                        <a class="dl" href="/download/{{ f }}"> <span class="iconify" data-icon="line-md:download-outline"></span> Download</a>
                        <form action="/delete/{{ f }}" method="POST" style="margin:0;padding:0;border:none;">
                            <button type="submit" style="background:#blue; color:white; padding: 6px 10px;">
                                <span class="iconify" data-icon="weui:delete-on-filled"></span>
                            </button>
                        </form>
                    </div>
                </article>
                {% endfor %}
            {% else %}
                <p class="empty">Folder is empty (Zero Items)</p>
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
        return redirect("/?msg=Select a file first!")
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(f"/?msg=File '{file.filename}' Uploaded!")

@app.route("/add_note", methods=["POST"])
def add_note():
    text = request.form.get("note_text")
    if not text or text.strip() == "":
        return redirect("/?msg=Note cannot be empty!")
    count = len([f for f in os.listdir(UPLOAD_FOLDER) if f.startswith("Note")]) + 1
    filename = f"Note_{count}.txt"
    with open(os.path.join(UPLOAD_FOLDER, filename), "w", encoding="utf-8") as f:
        f.write(text)
    return redirect(f"/?msg=Note saved as {filename}!")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<filename>", methods=['POST'])
def delete(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect("/?msg=Item deleted!")

@app.route('/qr')
def gen_qr():
    img = qrcode.make(f"http://{get_local_ip()}:5000")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def open_browser():
    webbrowser.open_new(f"http://{get_local_ip()}:5000/")

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n🚀 ShareHub running at http://{local_ip}:5000\n")
    Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
    
