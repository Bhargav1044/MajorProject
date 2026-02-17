from models.tts import synthesize_speech

if __name__ == "__main__":
    output = synthesize_speech(
        text="नमस्कार, हे Indic Parler चे अंतिम चाचणी वाक्य आहे.",
        language="mr",
        output_path="indic_parler_mr.wav"
    )

    print("Generated:", output)
