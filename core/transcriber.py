import whisper
import os
import requests
import subprocess
import streamlit as st

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

SARVAM_PIECE_SECONDS = 25

WHISPER_MODEL = st.secrets["WHISPER_MODEL"]

SARVAM_API_KEY = st.secrets["SARVAM_API_KEY"]
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = st.secrets["SARVAM_STT_MODEL"]

_model = None


# ─────────────────────────────────────────────────────────────
# Whisper Model Loader
# ─────────────────────────────────────────────────────────────

def load_model():
    global _model

    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL} ...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")

    return _model


# ─────────────────────────────────────────────────────────────
# Whisper Transcription
# ─────────────────────────────────────────────────────────────

def transcribe_chunk_whisper(chunk_path: str) -> str:
    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe"
    )

    return result["text"]


# ─────────────────────────────────────────────────────────────
# Sarvam API Helper
# ─────────────────────────────────────────────────────────────

def _send_to_sarvam(piece_path: str) -> str:
    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

    with open(piece_path, "rb") as f:
        files = {
            "file": (
                os.path.basename(piece_path),
                f,
                "audio/wav"
            )
        }

        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }

        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        print(f"\nSarvam returned {response.status_code}")
        print(f"Response body: {response.text}\n")
        response.raise_for_status()

    return response.json().get("transcript", "")


# ─────────────────────────────────────────────────────────────
# Sarvam Transcription
# ─────────────────────────────────────────────────────────────

def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """
    Split audio into 25-second pieces using FFmpeg
    and send each piece to Sarvam.
    """

    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set")

    output_pattern = f"{chunk_path}_sv_%03d.wav"

    command = [
        "ffmpeg",
        "-i",
        chunk_path,
        "-f",
        "segment",
        "-segment_time",
        str(SARVAM_PIECE_SECONDS),
        "-c",
        "copy",
        output_pattern,
    ]

    subprocess.run(command, check=True)

    piece_files = sorted([
        f for f in os.listdir(".")
        if f.startswith(os.path.basename(chunk_path) + "_sv_")
        and f.endswith(".wav")
    ])

    full_text = ""

    for i, piece_file in enumerate(piece_files):
        try:
            print(f" → Sarvam piece {i+1}/{len(piece_files)}...")
            full_text += _send_to_sarvam(piece_file) + " "
        finally:
            if os.path.exists(piece_file):
                os.remove(piece_file)

    return full_text.strip()


# ─────────────────────────────────────────────────────────────
# Router
# ─────────────────────────────────────────────────────────────

def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    """
    Route one chunk to Whisper or Sarvam depending on language choice.
    """

    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)

    return transcribe_chunk_whisper(chunk_path)


# ─────────────────────────────────────────────────────────────
# Full Transcription
# ─────────────────────────────────────────────────────────────

def transcribe_all(chunks: list, language: str = "english") -> str:
    full_transcript = ""

    engine = "Sarvam AI" if language.lower() == "hinglish" else "Whisper"

    print(f"Using {engine} for transcription.")

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(
            chunk,
            language=language
        )

        full_transcript += text + " "

    print("Transcription complete.")

    return full_transcript.strip()