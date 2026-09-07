import os
import pickle
from datetime import datetime
import io
import re

import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
from gtts import gTTS

PKL_FILE = "assistant_data.pkl"

# --- State Management ---
def load_data():
    if os.path.exists(PKL_FILE):
        try:
            with open(PKL_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass
    return {"user_name": None, "history": [], "total_commands": 0}

def save_data(data):
    with open(PKL_FILE, "wb") as f:
        pickle.dump(data, f)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- Helpers ---
def open_url_in_browser(url: str):
    """Automatically triggers browser to open the URL in a new tab via JavaScript."""
    js = f"<script>window.open('{url}', '_blank');</script>"
    components.html(js, height=0, width=0)

def process_command(text: str):
    cmd = text.lower().strip()
    url_to_open = None
    
    # Check for direct URL mentions or common sites
    if "youtube" in cmd:
        url_to_open = "https://www.youtube.com"
        response = "Opening YouTube."
    elif "google" in cmd and "open" in cmd:
        url_to_open = "https://www.google.com"
        response = "Opening Google."
    elif "github" in cmd:
        url_to_open = "https://www.github.com"
        response = "Opening GitHub."
    elif "open" in cmd:
        # Extract domain/URL pattern (e.g., "open reddit.com" or "open https://...")
        match = re.search(r"open\s+(https?://\S+|\S+\.(?:com|org|net|io|co|in))", cmd)
        if match:
            target = match.group(1)
            if not target.startswith("http"):
                target = "https://" + target
            url_to_open = target
            response = f"Opening {target}."
        else:
            response = f"I heard '{text}', but could not detect a valid URL to open."
    elif "time" in cmd:
        response = f"The current time is {datetime.now().strftime('%I:%M %p')}."
    elif "date" in cmd:
        response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    elif "hello" in cmd or "hi" in cmd:
        name = st.session_state.data.get("user_name") or "there"
        response = f"Hello {name}! How can I assist you today?"
    else:
        response = f"Received: '{text}'."

    return response, url_to_open

def text_to_speech(response_text: str) -> io.BytesIO:
    tts = gTTS(text=response_text, lang="en")
    sound_file = io.BytesIO()
    tts.write_to_fp(sound_file)
    sound_file.seek(0)
    return sound_file

# --- Page Setup & Styling ---
st.set_page_config(page_title="AI Voice Assistant", page_icon="🎙️", layout="centered")

# Custom CSS for the microphone section
st.markdown("""
    <style>
    div[data-testid="stAudioInput"] {
        border: 2px dashed #4CAF50;
        border-radius: 12px;
        padding: 10px;
        background-color: rgba(76, 175, 80, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎙️ AI Voice Assistant")

user = st.session_state.data.get("user_name") or "Guest"
st.caption(f"User: **{user}** | Total Commands Processed: **{st.session_state.data.get('total_commands', 0)}**")

# Microphone Input
audio_value = st.audio_input("Tap to record your voice command:")

if audio_value is not None:
    audio_bytes = audio_value.getvalue()
    if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
        st.session_state.last_audio = audio_bytes

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_value) as source:
            audio_data = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data)
                st.success(f"🗣️ **Heard:** {transcription}")

                # Process command
                response, url = process_command(transcription)
                st.info(f"🤖 **Assistant:** {response}")

                # Auto-open URL in browser if applicable
                if url:
                    open_url_in_browser(url)

                # Play voice reply
                audio_stream = text_to_speech(response)
                st.audio(audio_stream, format="audio/mp3", autoplay=True)

                # Save interaction
                st.session_state.data["history"].append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "command": transcription,
                    "response": response
                })
                st.session_state.data["total_commands"] += 1
                save_data(st.session_state.data)

            except sr.UnknownValueError:
                st.error("Could not understand audio. Please speak clearly.")
            except sr.RequestError as e:
                st.error(f"Speech service error: {e}")

# History
with st.expander("📜 Interaction History", expanded=False):
    history = st.session_state.data.get("history", [])
    if history:
        for item in reversed(history[-10:]):
            st.markdown(f"**[{item['time']}]** `{item['command']}` ➔ {item['response']}")
    else:
        st.write("No interactions recorded yet.")
