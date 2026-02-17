from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.api import api
from models.tts import preload_models

app = Flask(__name__)
CORS(app)

# Register API blueprint
app.register_blueprint(api, url_prefix="/api")


@app.route("/")
def health():
    return {"status": "Backend running"}


# 🔹 TTS audio serving endpoint
@app.route("/output/tts/<filename>")
def get_tts_audio(filename):
    return send_from_directory("output/tts", filename)


# 🔹 ALWAYS keep this last
if __name__ == "__main__":
    print("🚀 Preloading TTS models...")
    preload_models()
    print("🚀 Model preload complete")
    
    app.run(port=5000, debug=True)
