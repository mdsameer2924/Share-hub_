from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import socket
import sys

app = Flask(__name__)

# PyInstaller ke liye base path
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['Upload_folder'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    files = os.listdir(app.config['Upload_folder'])
    return render_template("index.html", files=files)

@app.route('/upload', methods=['POST'])
def upload_File():
    if 'file' not in request.files:
        return redirect(url_for('home'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('home'))
    file_path = os.path.join(app.config['Upload_folder'], file.filename)
    file.save(file_path)
    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['Upload_folder'], filename, as_attachment=True)

if __name__ == "__main__":
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    print(f"Phone → http://{ip}:8000")
    app.run(debug=True, port=8000, host="0.0.0.0")