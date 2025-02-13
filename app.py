from werkzeug.utils import secure_filename
import numpy as np
import cv2
from image.process_image import process_image_test
import os 
import subprocess
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Required for non-GUI environments
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from werkzeug.utils import secure_filename
from pydub import AudioSegment
app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

# Vérification du type de fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3'}

# Traitement de l'audio
def process_audio(action, input_path, output_path, **kwargs):
    audio = AudioSegment.from_file(input_path)

    if action == 'cut':
        start = kwargs.get('start', 0) * 1000
        end = kwargs.get('end', len(audio)) * 1000
        audio = audio[start:end]
    elif action == 'speed':
        speed = kwargs.get('factor', 1.0)
        audio = audio.speedup(playback_speed=speed)
    elif action == 'reverse':
        audio = audio.reverse()

    audio.export(output_path, format="mp3")
    return output_path

# Endpoint pour uploader un fichier
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    return jsonify({'audio_url': f'/static/uploads/{filename}'})

# Endpoint pour traiter un fichier audio
@app.route('/process', methods=['POST'])
def process_file():
    data = request.json
    input_url = data['current_file']
    action = data['action']

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(input_url))

    output_filename = f"processed_{uuid.uuid4()}.mp3"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    try:
        data.pop('action', None)
        process_audio(action, input_path, output_path, **data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'processed_url': f'/static/uploads/{output_filename}'})
@app.route('/mix', methods=['POST'])
def mix_audio():
    if 'file' not in request.files or 'current_file' not in request.form:
        return jsonify({'error': 'Missing files'}), 400
    
    mix_file = request.files['file']
    current_file = request.form['current_file']
    
    if mix_file.filename == '' or not allowed_file(mix_file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(current_file))
    mix_filename = str(uuid.uuid4()) + os.path.splitext(mix_file.filename)[1]
    mix_path = os.path.join(app.config['UPLOAD_FOLDER'], mix_filename)
    mix_file.save(mix_path)
    
    audio1 = AudioSegment.from_file(input_path)
    audio2 = AudioSegment.from_file(mix_path)
    
    mixed_audio = audio1.overlay(audio2)
    output_filename = f"mixed_{uuid.uuid4()}.mp3"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    mixed_audio.export(output_path, format="mp3")
    return jsonify({'mixed_url': f'/static/uploads/{output_filename}'})


if __name__ == '__main__':
    app.run(debug=True)