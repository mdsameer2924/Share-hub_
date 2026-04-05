from flask import Flask, render_template, request
import os


app = Flask(__name__)
app.config['Upload_folder']='uploads'
os.makedirs(app.config['Upload_folder'],exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_File():
    file=request.files['file']
    file_path=os.path.join(app.config['Upload_folder'],file.filename)
    file.save(file_path)
    return f"file {file_path} sucessfully uploaded!"

if __name__ == "__main__":
    app.run(debug=True, port=8000)
