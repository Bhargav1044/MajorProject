import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/nllb-200-distilled-600M"

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    src_lang="eng_Latn"
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
).to(device)

model.eval()

def _translate(text: str, target_lang_code: str) -> str:
    """
    Low-level translation helper.
    """
    if not text or not text.strip():
        return ""

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True
    ).to(device)

    forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_lang_code)

    with torch.no_grad():
        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_length=256
        )

    return tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )[0]

def translate_to_marathi(text: str) -> str:
    """
    English → Marathi
    """
    return _translate(text, "mar_Deva")


def translate_to_gujarati(text: str) -> str:
    """
    English → Gujarati
    """
    return _translate(text, "guj_Gujr")


def translate(text: str, target_language: str) -> str:
    """
    Dispatcher used by API.
    """
    if target_language == "gujarati":
        return translate_to_gujarati(text)

    # Default fallback
    return translate_to_marathi(text)
