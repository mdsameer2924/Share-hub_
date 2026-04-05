from flask import Flask, render_template, request,redirect, url_for,send_from_directory
import os


app = Flask(__name__)
app.config['Upload_folder']='uploads'
os.makedirs(app.config['Upload_folder'],exist_ok=True)


@app.route("/")
def home():
    files=os.listdir(app.config['Upload_folder'])
    return render_template("index.html",files=files)

@app.route('/upload', methods=['POST'])
def upload_File():
    file=request.files['file']
    file_path=os.path.join(app.config['Upload_folder'],file.filename)
    file.save(file_path)
    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['Upload_folder'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
