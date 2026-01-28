# Speech-to-Text and Translation System

This project implements a speech-to-text and translation pipeline using deep learning models.  
It supports both **pre-recorded audio** and **live microphone input**.

---

## 🔹 Models Used

### 1️⃣ Speech-to-Text
- Model: OpenAI Whisper (`whisper-base.en`)
- Purpose:Converts spoken English audio into English text

### 2️⃣ Translation
- Model: Meta NLLB-200 (`facebook/nllb-200-distilled-600M`)
- Purpose: Translates English text into Indian languages

---

## 🔹 Supported Languages
- Marathi
- Gujarati

---

## 🔹 System Architecture

Audio Input
↓
Whisper (Speech → Text)
↓
English Text
↓
NLLB-200 (Text → Translation)
↓
Marathi / Gujarati Output

## 🔹 Project Structure

speech-translation-project/
├── backend/
│ ├── app.py
│ ├── routes/api.py
│ ├── models/
│ │ ├── stt.py
│ │ └── translate.py
│ └── requirements.txt
├── frontend/
│ └── src/App.jsx
└── README.md


## 🔹 How to Run

### Backend
```bash
cd backend
python app.py


### Frontend
cd frontend
npm install
npm run dev


---

## ✅ 4️⃣ (Optional) Backend `README.md`

Create `backend/README.md` **only if you want**, with this:

```md
## Backend – Flask API

### Models
- Whisper (Speech-to-Text)
- NLLB-200 (Translation)

### Run
```bash
python app.py
