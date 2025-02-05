from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template("base-apps.html")

@app.route("/data-app")
def data_app():
    pass

@app.route("/image-app")
def image_app():
    return render_template("base-apps.html")

@app.route("/audio-app")
def audio_app():
    pass

if __name__ == '__main__':
    app.run(debug=True)