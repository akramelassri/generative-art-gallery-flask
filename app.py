from flask import Flask, render_template, request,jsonify, url_for
from werkzeug.utils import secure_filename
import numpy as np
import cv2
from image.process_image import process_image_test
import os 
import subprocess
import sys

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/gallery")
def gallery_page():
    return render_template("gallery.html")

@app.route("/apps")
def apps_page():
    return render_template("apps.html")

@app.route("/drawing-app")
def drawing_app():
    venv_python = sys.executable

    # Get the absolute path of the script inside the "draw" folder
    script_path = os.path.abspath(os.path.join("draw", "testingpygame.py"))

    # Run the script using the same Python executable
    subprocess.Popen([venv_python, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return jsonify({"message": "Script started successfully!"}), 200
@app.route("/data-app")
def data_app():
    return render_template("data-app.html")

@app.route("/image-app")
def image_app():
    return render_template("image-app.html")

@app.route('/upload-image', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    filename = secure_filename(file.filename)
    
    file_bytes = np.frombuffer(file.read(), np.uint8)

    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cv2.imwrite(file_path, img)

    # Build the URL for the saved image.
    image_url = url_for('static', filename='uploads/' + filename, _external=True)
    return jsonify({'image_url': image_url})


@app.route('/process-image', methods=['POST']) 
def process_image():
    data = request.get_json()
    image_url = data.get("image_url")
    print(type(image_url))
    type_process = data.get("type_process")
    name_process = data.get("name_process")
    if not hasattr(process_image, "previous_effect"): 
        process_image.previous_effect = type_process
    value = int(data.get("value"))
    img = cv2.imread(image_url)
    filename = os.path.basename(image_url)  # Extracts "example.jpg"
    image_path = os.path.join("static/uploads", filename)  # Constructs "static/uploads/example.jpg"
    img = cv2.imread(image_path)
    img = process_image_test(img, type_process, name_process, value)
    processed_path = os.path.join(app.config['UPLOAD_FOLDER'], "processed_" + filename)
    cv2.imwrite(processed_path, img)
    processed_url = url_for('static', filename='uploads/' + "processed_" + filename, _external=True)
    return jsonify({'image_url': processed_url})


@app.route("/audio-app")
def audio_app():
    return render_template("audio-app.html")

if __name__ == '__main__':
    app.run(debug=True)