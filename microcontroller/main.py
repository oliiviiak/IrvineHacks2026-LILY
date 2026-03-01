"""
microcontroller/main.py  —  fully offline, no internet required

STT:  Vosk  (local model, ~50MB)
TTS:  pyttsx3 / espeak  (local, no API)

Setup:
    1. pip install -r requirements.txt
    2. Download a model:
         mkdir -p microcontroller/model
         cd microcontroller/model
         # Tiny English (~50 MB, fine for RPi 3+):
         wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
         unzip vosk-model-small-en-us-0.15.zip
         mv vosk-model-small-en-us-0.15 en
       Final path should be:  microcontroller/model/en/
    3. Set NEEDER_ID in microcontroller/.env
"""

import json
import os
import queue
import tempfile
import threading
import time

import cv2
import pyttsx3
import requests
import sounddevice as sd
from vosk import KaldiRecognizer, Model
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

BASE_URL   = os.getenv("BACKEND_URL", "http://localhost:3000")
NEEDER_ID  = os.getenv("NEEDER_ID")
SAMPLE_RATE = 16000          # Vosk expects 16 kHz mono

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "en")

# ---------------------------------------------------------------------------
# Load Vosk model once at startup (takes ~2 s on RPi)
# ---------------------------------------------------------------------------

print("[vosk] loading model…")
_model = Model(MODEL_PATH)
print("[vosk] model ready")

# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------

_tts = pyttsx3.init()
_tts.setProperty("rate", 155)
_tts_lock = threading.Lock()


def speak(text: str):
    print(f"[LILY] {text}")
    with _tts_lock:
        _tts.say(text)
        _tts.runAndWait()

# ---------------------------------------------------------------------------
# STT  —  stream mic audio through Vosk until a pause, return transcript
# ---------------------------------------------------------------------------

def listen(silence_timeout: float = 3.0, max_duration: float = 20.0) -> str | None:
    """
    Record from mic, run Vosk locally, return lowercased transcript.
    Returns None if nothing was heard within `silence_timeout` seconds.
    `max_duration` is a hard cap so we never block forever mid-conversation.
    """
    q: queue.Queue[bytes] = queue.Queue()

    def _callback(indata, frames, time_info, status):
        q.put(bytes(indata))

    rec = KaldiRecognizer(_model, SAMPLE_RATE)
    rec.SetWords(False)       # faster without word timestamps

    result_text = None
    deadline = time.time() + max_duration
    last_speech_at = time.time()

    print("[listening…]")
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=_callback,
    ):
        while True:
            if time.time() > deadline:
                break

            try:
                data = q.get(timeout=0.2)
            except queue.Empty:
                continue

            if rec.AcceptWaveform(data):
                # Vosk returned a final result for this utterance
                text = json.loads(rec.Result()).get("text", "").strip()
                if text:
                    result_text = text.lower()
                    break
                # Empty final result — keep going
            else:
                # Check partial to detect speech activity
                partial = json.loads(rec.PartialResult()).get("partial", "")
                if partial:
                    last_speech_at = time.time()
                elif time.time() - last_speech_at > silence_timeout:
                    # Long silence with nothing partial → bail out
                    # Grab whatever Vosk has finalised so far
                    text = json.loads(rec.FinalResult()).get("text", "").strip()
                    if text:
                        result_text = text.lower()
                    break

    if result_text:
        print(f"[heard] {result_text}")
    return result_text


def listen_for_wake() -> bool:
    """
    Lightweight hot-word loop: short clips, just look for the wake phrase.
    Uses a smaller buffer and short silence timeout so idle CPU is low.
    """
    q: queue.Queue[bytes] = queue.Queue()

    def _callback(indata, frames, time_info, status):
        q.put(bytes(indata))

    rec = KaldiRecognizer(_model, SAMPLE_RATE)

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=_callback,
    ):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "").lower()
            else:
                text = json.loads(rec.PartialResult()).get("partial", "").lower()

            if any(w in text for w in ("hey lily", "hi lily", "okay lily")):
                print(f"[wake] detected: '{text}'")
                return True

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------

def take_photo() -> str | None:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[camera] could not open")
        return None
    for _ in range(5):          # warm-up frames
        cap.read()
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    path = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(path, frame)
    print(f"[camera] saved {path}")
    return path

# ---------------------------------------------------------------------------
# Backend API
# ---------------------------------------------------------------------------

def api_create_convo() -> str | None:
    try:
        res = requests.post(
            f"{BASE_URL}/convo/",
            json={"needer_id": NEEDER_ID},
            timeout=10,
        )
        res.raise_for_status()
        return res.json()["convo_id"]
    except Exception as e:
        print(f"[api] create_convo: {e}")
        return None


def api_send_message(convo_id: str, text: str) -> str | None:
    try:
        res = requests.post(
            f"{BASE_URL}/transcript/",
            json={"convo_id": convo_id, "content": text},
            timeout=30,
        )
        res.raise_for_status()
        return res.json().get("response")
    except Exception as e:
        print(f"[api] send_message: {e}")
        return None


def api_upload_document(convo_id: str, photo_path: str) -> dict | None:
    try:
        with open(photo_path, "rb") as f:
            res = requests.post(
                f"{BASE_URL}/document/",
                params={"convo_id": convo_id},
                files={"file": ("document.jpg", f, "image/jpeg")},
                timeout=60,
            )
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[api] upload_document: {e}")
        return None
    finally:
        try:
            os.remove(photo_path)
        except OSError:
            pass

# ---------------------------------------------------------------------------
# Keyword helpers
# ---------------------------------------------------------------------------

END_WORDS = ("bye lily", "goodbye lily", "bye", "goodbye", "stop lily")

SCAN_WORDS = (
    "scan", "photo", "photograph", "read this", "look at this",
    "what does this say", "what is this", "analyze", "document",
    "letter", "mail", "paper", "hold", "this document",
)


def is_end(text: str) -> bool:
    return any(w in text for w in END_WORDS)


def wants_scan(text: str) -> bool:
    return any(w in text for w in SCAN_WORDS)

# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------

def run_conversation(convo_id: str):
    speak("Hi! I'm Lily. How can I help you today?")

    while True:
        user_text = listen()

        if user_text is None:
            speak("I'm still here whenever you're ready.")
            continue

        if is_end(user_text):
            speak("Goodbye! Take care.")
            break

        if wants_scan(user_text):
            speak("Hold the document up to the camera and stay still.")
            time.sleep(1.5)
            photo_path = take_photo()

            if not photo_path:
                speak("I couldn't get a clear photo. Can you try again?")
                continue

            speak("Got it — let me read that for you.")
            result = api_upload_document(convo_id, photo_path)

            if result and result.get("overview"):
                speak(result["overview"])
            else:
                speak("I had trouble reading that. Can you hold it a bit closer?")
            continue

        reply = api_send_message(convo_id, user_text)
        if reply:
            speak(reply)
        else:
            speak("Sorry, I missed that. Could you say it again?")


# ---------------------------------------------------------------------------
# Main idle → active loop
# ---------------------------------------------------------------------------

def main():
    if not NEEDER_ID:
        raise EnvironmentError(
            "NEEDER_ID not set — add it to microcontroller/.env"
        )

    print("=== LILY ready (fully offline STT) ===")

    while True:
        print("[idle] waiting for wake word…")
        listen_for_wake()           # blocks until "hey lily"

        convo_id = api_create_convo()
        if not convo_id:
            speak("I'm having trouble connecting to the server.")
            time.sleep(5)
            continue

        print(f"[session] convo_id={convo_id}")
        try:
            run_conversation(convo_id)
        except Exception as e:
            print(f"[error] {e}")
            speak("Something went wrong. I'll restart.")

        print("[session] ended")


if __name__ == "__main__":
    main()