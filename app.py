import io
import os
import pickle
import datetime
from zoneinfo import ZoneInfo
import streamlit as st
import pyjokes
import speech_recognition as sr
import wikipedia
from gtts import gTTS
from pydub import AudioSegment

# ----------------------------------------------------
# Configuration & Constants
# ----------------------------------------------------
LOCAL_TZ = ZoneInfo("Asia/Kolkata")
PKL_FILE_PATH = "assistant_data.pkl"

st.set_page_config(
    page_title="AI Voice Assistant",
    page_icon="🎙️",
    layout="centered"
)

# ----------------------------------------------------
# A. State & Pickle Management
# ----------------------------------------------------
def load_assistant_data():
    """Loads assistant state and history from the .pkl file."""
    if os.path.exists(PKL_FILE_PATH):
        try:
            with open(PKL_FILE_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            st.warning(f"Could not load memory file: {e}")

    return {
        "user_name": None,
        "history": [],
        "total_commands": 0,
        "created_at": datetime.datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")
    }

def save_assistant_data(data):
    """Saves updated assistant state and history to the .pkl file."""
    try:
        with open(PKL_FILE_PATH, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"Failed to save memory: {e}")

# Initialize session state from pickle once
if "assistant_state" not in st.session_state:
    st.session_state.assistant_state = load_assistant_data()

state = st.session_state.assistant_state

# ----------------------------------------------------
# B. Helper Functions
# ----------------------------------------------------
def get_time_greeting():
    """Returns an appropriate greeting based on the current IST hour."""
    current_hour = datetime.datetime.now(LOCAL_TZ).hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    elif 17 <= current_hour < 21:
        return "Good evening"
    else:
        return "Hello"

def text_to_speech_bytes(text: str) -> bytes:
    """Generates MP3 audio bytes from text using gTTS."""
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()

def trigger_url_open(url: str):
    """Injects JavaScript into the client to open the URL in a new tab."""
    st.components.v1.html(
        f"""
        <script>
            window.open("{url}", "_blank");
        </script>
        """,
        height=0,
        width=0,
    )

# ----------------------------------------------------
# C. Command Processor
# ----------------------------------------------------
def process_command(command: str):
    raw_command = command
    command = command.lower().strip()
    response_text = ""
    action = None
    url = None

    site_shortcuts = {
        "hotstar": ("Disney+ Hotstar", "https://www.hotstar.com/in/home"),
        "youtube": ("YouTube", "https://www.youtube.com/"),
        "gemini": ("Gemini AI", "https://gemini.google.com/app"),
        "github": ("GitHub", "https://github.com/"),
        "linkedin": ("LinkedIn", "https://www.linkedin.com/feed/"),
    }

    # 1. User Profile
    if "my name is" in command:
        name = command.split("my name is")[-1].strip().capitalize()
        state["user_name"] = name
        greeting = get_time_greeting()
        response_text = f"{greeting}, {name}! Nice to meet you. I have saved your name in memory."

    elif "what is my name" in command or "who am i" in command:
        if state.get("user_name"):
            response_text = f"Your name is {state['user_name']}."
        else:
            response_text = "I don't know your name yet. Say 'my name is' followed by your name to set it."

    # 2. Greetings
    elif any(greet in command for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        greeting = get_time_greeting()
        name = state.get("user_name")
        if name:
            response_text = f"{greeting}, {name}! How can I help you today?"
        else:
            response_text = f"{greeting}! How can I assist you today?"

    # 3. History
    elif "show history" in command or "read history" in command:
        history_list = state.get("history", [])
        if not history_list:
            response_text = "Your conversation history is currently empty."
        else:
            response_text = f"You have {len(history_list)} previous logs saved. Displayed in the panel."

    elif "clear history" in command or "reset memory" in command:
        state["history"] = []
        state["total_commands"] = 0
        save_assistant_data(state)
        response_text = "History and session data have been cleared from memory."

    # 4. Date & Time (IST)
    elif "date" in command and "time" in command:
        now = datetime.datetime.now(LOCAL_TZ)
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        response_text = f"Today is {date_str}, and the time is {time_str}."

    elif "time" in command:
        now = datetime.datetime.now(LOCAL_TZ)
        time_str = now.strftime("%I:%M %p")
        response_text = f"The current time is {time_str}."

    elif "date" in command or "day" in command:
        now = datetime.datetime.now(LOCAL_TZ)
        date_str = now.strftime("%A, %B %d, %Y")
        response_text = f"Today's date is {date_str}."

    # 5. Wikipedia Search
    elif "wikipedia" in command:
        query = command.replace("wikipedia", "").replace("search", "").strip() or "Artificial intelligence"
        try:
            result = wikipedia.summary(query, sentences=2)
            response_text = result
        except Exception:
            response_text = "Could not find a summary for that query."

    # 6. Navigation: Shortcuts & Dynamic Sites
    elif any(site in command for site in site_shortcuts):
        matched_key = next(site for site in site_shortcuts if site in command)
        site_name, target_url = site_shortcuts[matched_key]
        response_text = f"Opening {site_name}..."
        action = "open_url"
        url = target_url

    elif command.startswith("open ") or command.startswith("launch "):
        target = command.replace("open ", "").replace("launch ", "").strip().replace(" ", "")
        response_text = f"Opening {target}..."
        action = "open_url"
        url = f"https://www.{target}.com"

    # 7. Jokes
    elif "joke" in command:
        response_text = pyjokes.get_joke()

    # 8. Exit
    elif any(w in command for w in ["exit", "stop", "bye"]):
        response_text = "Goodbye! Have a great day."

    else:
        response_text = f"I heard '{raw_command}', but I don't have an action mapped for that yet."

    # Save to history and persist
    timestamp = datetime.datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %I:%M:%S %p")
    state["history"].append({
        "time": timestamp,
        "command": raw_command,
        "response": response_text
    })
    state["total_commands"] += 1
    save_assistant_data(state)

    return response_text, action, url

# ----------------------------------------------------
# D. Streamlit UI Layout
# ----------------------------------------------------
st.title("🎙️ AI Voice Assistant")
greeting_prefix = get_time_greeting()
user_display_name = state.get("user_name")
if user_display_name:
    st.caption(f"{greeting_prefix}, **{user_display_name}**! Voice Assistant is ready.")
else:
    st.caption(f"{greeting_prefix}! Voice Assistant is ready.")

# Sidebar: Shortcuts & Memory Controls
with st.sidebar:
    st.header("⚡ Shortcuts & Settings")
    st.markdown("""
    **Try saying:**
    - *"Open Hotstar"*
    - *"Open YouTube"*
    - *"Open Gemini"*
    - *"What is my name?"*
    - *"Tell me a joke"*
    - *"Wikipedia Quantum Computing"*
    """)

    st.markdown("---")
    st.write(f"**Saved Commands:** {state.get('total_commands', 0)}")
    if st.button("🗑️ Clear History & Memory"):
        state["history"] = []
        state["total_commands"] = 0
        state["user_name"] = None
        save_assistant_data(state)
        st.success("Memory cleared!")
        st.rerun()

# Microphone Input Widget (Built into Streamlit)
audio_input = st.audio_input("Record a voice command")

if audio_input is not None:
    # Read in-memory audio and convert to 16kHz mono WAV for SpeechRecognition
    try:
        audio_segment = AudioSegment.from_file(audio_input)
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_buffer) as source:
            recorded_audio = recognizer.record(source)
            recognized_text = recognizer.recognize_google(recorded_audio, language="en-in")

        st.info(f"🗣️ **You said:** *\"{recognized_text}\"*")

        # Process the recognized command
        response, action, url = process_command(recognized_text)

        # Display and speak assistant response
        st.success(f"🤖 **Assistant:** {response}")
        audio_bytes = text_to_speech_bytes(response)
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

        # Handle URL opening action
        if action == "open_url" and url:
            trigger_url_open(url)
            st.markdown(
                f"""
                <div style="margin-top: 10px;">
                    <a href="{url}" target="_blank" style="
                        background-color: #2563eb;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 6px;
                        text-decoration: none;
                        font-weight: 500;">
                        🔗 Launch {url}
                    </a>
                    <p style="font-size: 12px; color: gray; margin-top: 5px;">
                        (If popup was blocked by your browser, click above to open).
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    except sr.UnknownValueError:
        st.warning("⚠️ Could not understand the audio. Please speak clearly and try again.")
    except sr.RequestError as e:
        st.error(f"Speech recognition service error: {e}")
    except Exception as ex:
        st.error(f"Error processing audio: {ex}")

# History View
if state.get("history"):
    with st.expander("📜 View Conversation History", expanded=False):
        for idx, item in enumerate(reversed(state["history"][-10:]), 1):
            st.markdown(f"**[{item['time']}]**")
            st.markdown(f"- 🗣️ *Command:* {item['command']}")
            st.markdown(f"- 🤖 *Reply:* {item['response']}")
            st.divider()
