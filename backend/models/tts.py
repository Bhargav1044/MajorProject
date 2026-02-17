import os
import torch
import soundfile as sf
from transformers import LlamaTokenizer
from transformers import AutoTokenizer
from parler_tts import ParlerTTSForConditionalGeneration

from typing import Optional
from parler_tts import ParlerTTSForConditionalGeneration
from TTS.api import TTS

# ============================================================
# INDIC PARLER TTS (PRIMARY – MULTILINGUAL)
# ============================================================

INDIC_PARLER_MODEL_ID = "ai4bharat/indic-parler-tts"

_indic_model = None
_prompt_tokenizer = None
_description_tokenizer = None
_indic_device = None

def _load_indic_parler():
    global _indic_model, _prompt_tokenizer, _description_tokenizer, _indic_device

    if _indic_model is not None:
        return _indic_model, _prompt_tokenizer, _description_tokenizer, _indic_device

    _indic_device = "cpu"  # keep CPU for stability first

    # 🔹 Load model
    _indic_model = ParlerTTSForConditionalGeneration.from_pretrained(
        "ai4bharat/indic-parler-tts"
    ).to(_indic_device)
    _indic_model.eval()

    # 🔹 Tokenizer for the ACTUAL TEXT (prompt)
    _prompt_tokenizer = AutoTokenizer.from_pretrained(
        "ai4bharat/indic-parler-tts"
    )

    # 🔹 Tokenizer for the DESCRIPTION (style / speaker)
    _description_tokenizer = AutoTokenizer.from_pretrained(
        _indic_model.config.text_encoder._name_or_path
    )

    return _indic_model, _prompt_tokenizer, _description_tokenizer, _indic_device


def _build_indic_prompt(text: str, language: str) -> str:
    return text.strip()

def _synthesize_indic_parler(text: str, language: str, output_path: str):
    model, prompt_tokenizer, description_tokenizer, device = _load_indic_parler()

    # 🔹 The text you want spoken (already Marathi / Gujarati etc.)
    prompt = text.strip()

    # 🔹 Minimal, SAFE description (required!)
    description = "A clear, natural human voice with very high quality audio."

    prompt_inputs = prompt_tokenizer(
        prompt,
        return_tensors="pt"
    ).to(device)

    description_inputs = description_tokenizer(
        description,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        generation = model.generate(
            input_ids=description_inputs.input_ids,
            attention_mask=description_inputs.attention_mask,
            prompt_input_ids=prompt_inputs.input_ids,
            prompt_attention_mask=prompt_inputs.attention_mask,
        )

    audio = generation.cpu().numpy().squeeze()
    sf.write(output_path, audio, model.config.sampling_rate)

    return output_path


# ============================================================
# COQUI XTTS (FALLBACK – HI / EN ONLY)
# ============================================================

_xtts_model = None


def _load_xtts():
    global _xtts_model

    if _xtts_model is not None:
        return _xtts_model

    # FORCE CPU for XTTS
    _xtts_model = TTS(
        model_name="tts_models/multilingual/multi-dataset/xtts_v2",
        progress_bar=False
    ).to("cpu")

    return _xtts_model

def _synthesize_xtts(
    text: str,
    language: str,
    output_path: str,
    speaker_wav: str
):
    """
    Coqui XTTS synthesis (requires speaker_wav).
    """
    if language not in ["hi", "en"]:
        raise ValueError("XTTS supports only 'hi' and 'en'")

    if not speaker_wav or not os.path.exists(speaker_wav):
        raise FileNotFoundError(f"speaker_wav not found: {speaker_wav}")

    tts = _load_xtts()

    tts.tts_to_file(
        text=text,
        language=language,
        speaker_wav=speaker_wav,
        file_path=output_path
    )

    return output_path


# ============================================================
# PUBLIC ROUTER API
# ============================================================

def synthesize_speech(
    text: str,
    language: str,
    output_path: str,
    speaker_wav: Optional[str] = None,
    engine: str = "indic",  # NEW
):
    """
    TTS Router

    PRIMARY:
        Indic Parler → all supported Indic languages

    FALLBACK:
        Coqui XTTS → Hindi, English (requires speaker_wav)
    """

    language = language.lower().strip()
    engine = engine.lower()

    # ---- FORCE INDIC PARLER ----
    if engine == "indic":
        return _synthesize_indic_parler(
            text=text,
            language=language,
            output_path=output_path
        )

    # ---- FORCE XTTS ----
    if engine == "xtts":
        if not speaker_wav:
            raise ValueError("speaker_wav required for XTTS")
        return _synthesize_xtts(
            text=text,
            language=language,
            output_path=output_path,
            speaker_wav=speaker_wav
        )

    #---- AUTO (DEFAULT) ----
    if language in ["mr", "hi", "ta", "te", "kn", "bn", "gu", "pa", "or", "ml"]:
        return _synthesize_indic_parler(text, language, output_path)

    if language in ["en"]:
        return _synthesize_xtts(text, language, output_path, speaker_wav)

    raise ValueError(f"Unsupported language: {language}")

def preload_models():
    """
    Preload TTS models at app startup
    """
    try:
        _load_indic_parler()
        print("✅ Indic Parler loaded")
    except Exception as e:
        print("⚠️ Indic Parler failed:", e)

    try:
        _load_xtts()
        print("✅ XTTS loaded")
    except Exception as e:
        print("⚠️ XTTS failed:", e)
