from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import librosa
from pydub import AudioSegment

from models.stt import transcribe
from models.translate import translate

api = Blueprint("api", __name__)


@api.route("/process-audio", methods=["POST"])
def process_audio():
    """
    Handles both:
    - Pre-recorded audio uploads
    - Live microphone recordings (webm)

    Steps:
    1. Validate request
    2. Prepare directories
    3. Save incoming audio temporarily
    4. Convert to WAV (ffmpeg via pydub)
    5. Load audio for Whisper
    6. Transcribe English text
    7. Translate to Marathi
    8. Persist audio + transcript locally
    9. Return JSON response
    10. Handle errors safely
    """

    # 1. Validate request
    if "audio" not in request.files:
        return jsonify({"error": "No audio file received"}), 400

    audio_file = request.files["audio"]
    target_lang = request.form.get("language", "marathi")

    # 2. Ensure required directories exist
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # 3. Prepare filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_webm_path = f"temp/{timestamp}.webm"
    temp_wav_path = f"temp/{timestamp}.wav"
    final_audio_path = f"output/{timestamp}.wav"
    transcript_path = f"output/{timestamp}.txt"

    try:
        # 4. Save incoming audio temporarily
        audio_file.save(temp_webm_path)

        # 5. Convert WEBM → WAV using ffmpeg (via pydub)
        try:
            audio = AudioSegment.from_file(temp_webm_path)
            audio.export(temp_wav_path, format="wav")
        except Exception:
            return jsonify({
                "error": "Audio format not supported or ffmpeg is missing."
            }), 400

        # 6. Load WAV audio for Whisper
        audio_array, _ = librosa.load(temp_wav_path, sr=16000)

        # 7. Speech → Text (English)
        english_text = transcribe(audio_array)

        # 8. Translate English → Marathi
        if not english_text or not english_text.strip():
            translated_text = "काहीही आवाज आढळला नाही. कृपया पुन्हा प्रयत्न करा."
        else:
           translated_text = translate(english_text, target_lang)


        # 9. Persist final audio + transcript
        os.replace(temp_wav_path, final_audio_path)

        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write("ENGLISH:\n")
            f.write(english_text + "\n\n")
            f.write("TRANSLATED:\n")
            f.write(translated_text)

        # Cleanup temp webm if still present
        if os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)

        # 10. Return successful response
        return jsonify({
            "english": english_text,
            "translated": translated_text,
            "language": target_lang,
            "audio_file": final_audio_path
        })

    except Exception as e:
        # Final safety net: cleanup temp files
        if os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

        return jsonify({"error": str(e)}), 500
