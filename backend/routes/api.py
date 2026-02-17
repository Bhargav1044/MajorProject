from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import librosa
from pydub import AudioSegment

from models.stt import transcribe
from models.translate import translate
from models.tts import synthesize_speech
from flask import send_from_directory

api = Blueprint("api", __name__)

@api.route("/output/tts/<path:filename>")
def get_tts_audio(filename):
    return send_from_directory(
        directory="output/tts",
        path=filename,
        as_attachment=False
    )
@api.route("/process-audio", methods=["POST"])
def process_audio():
    # --------------------------------------------------
    # 1. Validate request
    # --------------------------------------------------
    if "audio" not in request.files:
        return jsonify({"error": "No audio file received"}), 400

    audio_file = request.files["audio"]

    # ISO-like language codes: mr, hi, ta, en, etc.
    target_lang = request.form.get("language", "mr").lower()
    engine = request.form.get("engine", "auto")  # auto | indic | xtts

    # -------------------------------
    # Normalize language & engine
    # -------------------------------
    LANGUAGE_MAP = {
    "marathi": "mr",
    "gujarati": "gu",
    "english": "en",

    "mr": "mr",
    "gu": "gu",
    "en": "en",
}

    ENGINE_MAP = {
        "indic parler": "indic",
        "coqui xtts": "xtts",
        "xtts": "xtts",
        "indic": "indic",
        "auto": "auto",
    }

    target_lang = LANGUAGE_MAP.get(target_lang)
    engine = ENGINE_MAP.get(engine, "auto")

    if not target_lang:
        return jsonify({
            "error": f"Unsupported language: {target_lang}"
        }), 400

    # --------------------------------------------------
    # 2. Ensure required directories exist
    # --------------------------------------------------
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/tts", exist_ok=True)

    # --------------------------------------------------
    # 3. Prepare filenames
    # --------------------------------------------------
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    temp_webm_path = f"temp/{timestamp}.webm"
    temp_wav_path = f"temp/{timestamp}.wav"
    transcript_path = f"output/{timestamp}.txt"

    tts_filename = f"{timestamp}.wav"
    final_audio_path = f"output/tts/{tts_filename}"

    final_audio_path = f"output/tts/tts_{timestamp}_{target_lang}.wav"

    try:
        # --------------------------------------------------
        # 4. Save incoming audio
        # --------------------------------------------------
        audio_file.save(temp_webm_path)

        # --------------------------------------------------
        # 5. Convert WEBM → WAV
        # --------------------------------------------------
        try:
            audio = AudioSegment.from_file(temp_webm_path)
            audio.export(temp_wav_path, format="wav")
        except Exception:
            return jsonify({
                "error": "Audio format not supported or ffmpeg is missing."
            }), 400

        # --------------------------------------------------
        # 6. Load WAV audio for Whisper
        # --------------------------------------------------
        audio_array, _ = librosa.load(temp_wav_path, sr=16000)

        # --------------------------------------------------
        # 7. Speech → Text (English)
        # --------------------------------------------------
        english_text = transcribe(audio_array)

        # --------------------------------------------------
        # 8. Translate English → target language
        # --------------------------------------------------
        if not english_text or not english_text.strip():
            translated_text = "काहीही आवाज आढळला नाही. कृपया पुन्हा प्रयत्न करा."
        else:
            translated_text = translate(english_text, target_lang)

        # --------------------------------------------------
        # 9. Text → Speech (Indic Parler / XTTS)
        # --------------------------------------------------
        tts_audio_path = f"output/tts/{timestamp}.wav"

        synthesize_speech(
            text=translated_text,
            language=target_lang,
            output_path=tts_audio_path,
            engine=engine
        )

        # --------------------------------------------------
        # 10. Persist transcript
        # --------------------------------------------------
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write("ENGLISH:\n")
            f.write(english_text + "\n\n")
            f.write("TRANSLATED:\n")
            f.write(translated_text + "\n")

        # --------------------------------------------------
        # 11. Cleanup temp files
        # --------------------------------------------------
        if os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)

        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

        # --------------------------------------------------
        # 12. Return success response
        # --------------------------------------------------
        tts_filename = os.path.basename(tts_audio_path)

        return jsonify({
            "english": english_text,
            "translated": translated_text,
            "language": target_lang,
            "tts_audio_file": f"/output/tts/{tts_filename}"
        })

    except Exception as e:
        # Final safety cleanup
        if os.path.exists(temp_webm_path):
            os.remove(temp_webm_path)
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

        return jsonify({"error": str(e)}), 500