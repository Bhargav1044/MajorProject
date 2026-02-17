import { useState, useRef } from "react";
import "./index.css";

export default function App() {
  const [mode, setMode] = useState(null);          // null | "batch" | "live"
  const [file, setFile] = useState(null);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("No file chosen");
  const [liveAudioUrl, setLiveAudioUrl] = useState(null);
  const [language, setLanguage] = useState("marathi");
  const [liveBlob, setLiveBlob] = useState(null);
  
  const recorderRef = useRef(null);
  const chunksRef = useRef([]);
  const [engine, setEngine] = useState("auto");
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);

  function clearOutput() {
  setResult("");
}

  /* =========================
     PRE-RECORDED AUDIO LOGIC
     ========================= */
  async function handlePreRecorded() {
    if (!file) {
      alert("Please choose an audio file first");
      return;
    }

    setLoading(true);
    setResult("");

    const formData = new FormData();
    formData.append("audio", file);
    formData.append("language", language);
    formData.append("engine", engine); 

    try {
      const res = await fetch("http://localhost:5000/api/process-audio", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data.translated || data.error);
        if (data.tts_audio_file) {
          setTtsAudioUrl(`http://localhost:5000/${data.tts_audio_file}`);
        } else {
          setTtsAudioUrl(null);
      }

    } catch (err) {
      setResult("Error while processing audio.");
    } finally {
      setLoading(false);
    }
  }

  /* =========================
     LIVE MIC RECORDING LOGIC
     ========================= */
  async function startMic() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recorderRef.current = new MediaRecorder(stream, {
      mimeType: "audio/webm"});
    chunksRef.current = [];

    recorderRef.current.ondataavailable = (e) => {
      chunksRef.current.push(e.data);
    };

    recorderRef.current.start();
  }

  async function stopMic() {
  if (!recorderRef.current) return;

  recorderRef.current.stop();

  recorderRef.current.onstop = () => {
    const blob = new Blob(chunksRef.current, { type: "audio/webm" });

    const audioUrl = URL.createObjectURL(blob);
    setLiveAudioUrl(audioUrl);

    setLiveBlob(blob); 
    chunksRef.current = [];
  };
}


async function translateLiveAudio() {
  if (!liveBlob) {
    alert("Please record audio first");
    return;
  }

  setLoading(true);
  setResult("");

  const formData = new FormData();
  formData.append("audio", liveBlob, "live.webm");
  formData.append("language", language);
  formData.append("engine", engine);

  try {
    const res = await fetch("http://127.0.0.1:5000/api/process-audio", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResult(data.translated);
      if (data.tts_audio_file) {
        setTtsAudioUrl(`http://localhost:5000/${data.tts_audio_file}`);
      } else {
        setTtsAudioUrl(null);
    }
  } catch (err) {
    setResult("Network error while processing live audio.");
  } finally {
    setLoading(false);
  }
}

  /* =========================
     UI
     ========================= */
  return (
    <>
      {/* Background */}
      <div className="bg-ornaments">
        <div className="orb orb1" />
        <div className="orb orb2" />
        <div className="orb orb3" />
      </div>

      <div className="container">
        {/* MODE SELECTION */}
        {!mode && (
          <div className="panel-switch">
            <button className="switch" onClick={() => setMode("batch")}>
              Pre-recorded Translation
            </button>
            <button className="switch" onClick={() => setMode("live")}>
              Live Translation
            </button>
          </div>
        )}

        {/* PRE-RECORDED MODE */}
        {mode === "batch" && (
          <div className="card">
            <button className="cta secondary" onClick={() => setMode(null)}>
              ← Back
            </button>

            <div className="row">
              <label style={{ fontSize: "14px" }}>Translate to:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="marathi">Marathi</option>
                <option value="gujarati">Gujarati</option>
              </select>
            </div>

            <div className="row">
              <label style={{ fontSize: "14px" }}>TTS Engine:</label>
              <select
                value={engine}
                onChange={(e) => setEngine(e.target.value)}
              >
                <option value="auto">Auto (Indic → XTTS)</option>
                <option value="indic">Indic Parler</option>
                <option value="xtts">Coqui XTTS</option>
              </select>
            </div>

            <div className="row">
              <label className="file-upload-label">
                Choose File
                <input
                  type="file"
                  accept="audio/*"
                  hidden
                  onChange={(e) => {
                    const selectedFile = e.target.files[0];
                    setFile(selectedFile);
                    setFileName(selectedFile ? selectedFile.name : "No file chosen");}}
                />
              </label>
              
              <span style={{ color: "#a0a6b6" }}>{fileName}</span>
              <button
                className="cta"
                onClick={handlePreRecorded}
                disabled={loading}
              >
                {loading ? "Processing..." : "Transcribe & Translate"}
              </button>
            </div>
            
             <button
              className="cta secondary"
              onClick={() => {
                setResult("");
                setFile(null);
                setFileName("No file chosen");
              }}
              disabled={!result && !file}
            >
              Clear Output
            </button>

            <div className="result-box">
              {result ? (
                <>
                  <strong>Translation:</strong>
                  <p>{result}</p>
                </>
              ) : ( "Your translated text will appear here...")}
              {ttsAudioUrl && (
                <>
                  <div className="section-title">Generated Speech</div>
                  <audio controls src={ttsAudioUrl} style={{ width: "100%" }} />
                </>
              )}
            </div>
          </div>
        )}

        {/* LIVE MODE */}
        {mode === "live" && (
          <div className="card">
            <button className="cta secondary" onClick={() => {
              setMode(null);
              setLiveAudioUrl(null);
              setLiveBlob(null);
              setResult("");}}>
              ← Back
            </button>

            <div className="row">
              <label style={{ fontSize: "14px" }}>Translate to:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="marathi">Marathi</option>
                <option value="gujarati">Gujarati</option>
              </select>
            </div>

            <div className="row">
              <label style={{ fontSize: "14px" }}>TTS Engine:</label>
              <select
                value={engine}
                onChange={(e) => setEngine(e.target.value)}
              >
                <option value="auto">Auto (Indic → XTTS)</option>
                <option value="indic">Indic Parler</option>
                <option value="xtts">Coqui XTTS</option>
              </select>
            </div>

            <div className="row">
              <button className="cta" onClick={startMic} disabled={loading}>
                Start Listening
              </button>
              <button
                className="cta secondary"
                onClick={stopMic}
                disabled={loading}
              >
                Stop Listening
              </button>
              <button
                className="cta"
                onClick={translateLiveAudio}
                disabled={loading || !liveBlob}
              >
                {loading ? "Translating..." : "Translate Live Audio"}
              </button>

              <button
                className="cta secondary"
                onClick={() => {
                  setResult("");
                  setLiveAudioUrl(null);
                  setLiveBlob(null);
                }}
                disabled={!result && !liveBlob}
              >
                Clear Output
              </button>

            </div>
            {liveAudioUrl && (
              <div style={{ marginTop: "15px", width: "100%" }}>
                <div className="section-title">Recorded Audio Preview</div>
                  <audio controls src={liveAudioUrl} style={{ width: "100%" }} />
                </div>
            )}

            <div className="result-box">
              {result || "Your translated text will appear here..."}
              {ttsAudioUrl && (
                <>
                  <div className="section-title">Generated Speech</div>
                  <audio controls src={ttsAudioUrl} style={{ width: "100%" }} />
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
