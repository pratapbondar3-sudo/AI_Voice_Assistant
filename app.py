import os
import pickle
from datetime import datetime
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io

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

# --- Core Assistant Logic ---
def process_command(text: str) -> str:
    cmd = text.lower().strip()
    if "youtube" in cmd:
        return "Opening YouTube: https://youtube.com"
    elif "time" in cmd:
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    elif "date" in cmd:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
    elif "hello" in cmd or "hi" in cmd:
        name = st.session_state.data.get("user_name") or "there"
        return f"Hello {name}! How can I assist you today?"
    elif "my name is" in cmd:
        name = cmd.split("my name is")[-1].strip().title()
        st.session_state.data["user_name"] = name
        return f"Nice to meet you, {name}!"
    else:
        return f"Received command: '{text}'. No specific action mapped yet."

def text_to_speech(response_text: str) -> io.BytesIO:
    tts = gTTS(text=response_text, lang="en")
    sound_file = io.BytesIO()
    tts.write_to_fp(sound_file)
    sound_file.seek(0)
    return sound_file

# --- UI Layout ---
st.set_page_config(page_title="Voice Assistant", page_icon="🎙️", layout="centered")
st.title("🎙️ Voice Agent Assistant")

user = st.session_state.data.get("user_name") or "Guest"
st.caption(f"User: **{user}** | Total Commands Processed: **{st.session_state.data.get('total_commands', 0)}**")

# Browser Microphone Input
audio_value = st.audio_input("Speak a command:")

if audio_value is not None:
    # Avoid re-processing the exact same audio clip across reruns
    audio_bytes = audio_value.getvalue()
    if "last_audio" not in st.session_state or st.session_state.last_audio != audio_bytes:
        st.session_state.last_audio = audio_bytes
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_value) as source:
            audio_data = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data)
                st.success(f"🗣️ **Heard:** {transcription}")

                # Process command & update state
                response = process_command(transcription)
                st.info(f"🤖 **Assistant:** {response}")

                # Play voice response
                audio_stream = text_to_speech(response)
                st.audio(audio_stream, format="audio/mp3", autoplay=True)

                # Persist to pkl
                st.session_state.data["history"].append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "command": transcription,
                    "response": response
                })
                st.session_state.data["total_commands"] += 1
                save_data(st.session_state.data)

            except sr.UnknownValueError:
                st.error("Could not understand the audio. Please speak clearly.")
            except sr.RequestError as e:
                st.error(f"Speech service error: {e}")

# --- Command History ---
with st.expander("📜 Interaction History", expanded=False):
    history = st.session_state.data.get("history", [])
    if history:
        for item in reversed(history[-10:]):
            st.markdown(f"**[{item['time']}]** `{item['command']}` ➔ {item['response']}")
    else:
        st.write("No interactions recorded yet.")
