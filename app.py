from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np
import cv2
from image.process_image import process_image_test
import os 
import subprocess
import sys
import uuid
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Required for non-GUI environments
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from werkzeug.utils import secure_filename
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xls', 'xlsx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['GALLERY_FOLDER'] = 'static/gallery'
def get_gallery_images():
    # List all image files (adjust extensions as needed)
    images = [f for f in os.listdir(app.config['GALLERY_FOLDER']) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return images

@app.route("/")
@app.route("/home")
def home_page():
    images = get_gallery_images()
    return render_template("home.html", images=images)

@app.route("/gallery")
def gallery_page():
    images = get_gallery_images()
    return render_template('gallery.html', images=images)

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
    return jsonify({"message": "App started successfully!"}), 200

# Helper functions


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()

def read_data_file(filepath, extension):
    if extension == 'csv':
        return pd.read_csv(filepath)
    elif extension in {'xls', 'xlsx'}:
        return pd.read_excel(filepath)
    return None
@app.route('/data-app')
def data_app():
    return render_template('data-app.html')
# Endpoint 1: File Upload
def allowed_file_data(filename):
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
    else:
        ext = ''
        print("No extension fouZnd in filename")
    is_allowed = ext in app.config['ALLOWED_EXTENSIONS']
    return is_allowed

@app.route('/data-app/upload', methods=['POST'])
def handle_file_upload():
    if 'data-file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['data-file']
    
    if file.filename == '' or not allowed_file_data(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        save_filename = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], save_filename)
        file.save(filepath)

        # Read file and get columns
        extension = get_file_extension(filename)
        df = read_data_file(filepath, extension)
        columns = df.columns.tolist()

        return jsonify({
            'message': 'File uploaded successfully',
            'columns': columns,
            'file_id': unique_id,
            'original_filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Endpoint 2: Data Cleaning
@app.route('/clean-data', methods=['POST'])
def clean_data():
    data = request.json
    file_id = data.get('file_id')
    cleaning_options = data.get('cleaning_options', {})

    try:
        # Find original file
        original_file = next(f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(file_id))
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_file)
        
        # Read and process data
        df = read_data_file(original_path, get_file_extension(original_file))
        
        # Apply cleaning operations
        if cleaning_options.get('handle_missing'):
            df = df.dropna()
        if cleaning_options.get('remove_duplicates'):
            df = df.drop_duplicates()
        if cleaning_options.get('convert_types'):
            df = df.convert_dtypes()
        if cleaning_options.get('rename_columns'):
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        if cleaning_options.get('handle_outliers'):
            numeric_cols = df.select_dtypes(include='number').columns
            df[numeric_cols] = df[numeric_cols].apply(lambda x: x.clip(*x.quantile([0.05, 0.95])))
        if cleaning_options.get('clean_text'):
            text_cols = df.select_dtypes(include='object').columns
            df[text_cols] = df[text_cols].apply(lambda x: x.str.strip().str.lower())

        # Overwrite original file with cleaned data
        cleaned_filename = f"cleaned_{file_id}_{data.get('original_filename')}"
        cleaned_path = os.path.join(app.config['UPLOAD_FOLDER'], cleaned_filename)
        df.to_csv(cleaned_path, index=False)

        return jsonify({
            'message': 'Data cleaned successfully',
            'columns': df.columns.tolist(),
            'cleaned_file': cleaned_filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 3: Get Available Plots
@app.route('/get_plots', methods=['POST'])
def get_available_plots():
    data = request.json
    columns = data.get('columns', [])
    file_id = data.get('file_id')

    try:
        # Find cleaned file
        cleaned_file = next(f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(f"cleaned_{file_id}"))
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], cleaned_file))

        # Determine available plot types
        plot_types = []
        numeric_cols = df[columns].select_dtypes(include='number').columns
        text_cols = df[columns].select_dtypes(include='object').columns

        if len(numeric_cols) >= 1:
            plot_types.extend(['Histogram', 'Box Plot'])
        if len(numeric_cols) >= 2:
            plot_types.extend(['Scatter Plot', 'Line Plot'])
        if len(text_cols) >= 1:
            plot_types.append('Word Cloud')
        if len(numeric_cols) >= 2 and len(text_cols) >= 1:
            plot_types.append('Heatmap')

        return jsonify({'plots': list(set(plot_types))})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint 4: Generate Visualization
@app.route('/generate-plot', methods=['POST'])
def generate_visualization():
    data = request.json
    file_id = data.get('file_id')
    columns = data.get('columns', [])
    plot_type = data.get('plot_type')

    try:
        # Find cleaned file
        cleaned_file = next(f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.startswith(f"cleaned_{file_id}"))
        df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], cleaned_file))

        # Generate plot
        plot_filename = f"plot_{uuid.uuid4()}.png"
        plot_path = os.path.join('static/plots', plot_filename)
        
        plt.figure(figsize=(10, 6))
        
        if plot_type == 'Histogram':
            sns.histplot(df[columns[0]])
        elif plot_type == 'Scatter Plot':
            sns.scatterplot(x=columns[0], y=columns[1], data=df)
        elif plot_type == 'Line Plot':
            sns.lineplot(x=columns[0], y=columns[1], data=df)
        elif plot_type == 'Box Plot':
            sns.boxplot(x=df[columns[0]])
        elif plot_type == 'Heatmap':
            sns.heatmap(df[columns].corr(), annot=True)
        
        plt.title(f"{plot_type} of {', '.join(columns)}")
        plt.savefig(plot_path)
        plt.close()

        return jsonify({
            'plot_url': f'/static/plots/{plot_filename}',
            'message': 'Plot generated successfully'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    type_process = data.get("type_process")
    name_process = data.get("name_process")
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


@app.route("/upload-gallery", methods=['POST'])
def upload_gallery():
    data = request.get_json()
    image_url = data.get("image_url")
    filename = os.path.basename(image_url)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = cv2.imread(image_path)
    if not hasattr(upload_gallery,"count"):
        upload_gallery.count = 0
    else:
        upload_gallery.count += 1
    image_path = os.path.join(app.config['GALLERY_FOLDER'], str(upload_gallery.count) + filename)
    cv2.imwrite(image_path, img)
    return jsonify({"message": "Image Saved"}), 200


if __name__ == '__main__':
    app.run(debug=True)