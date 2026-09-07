import streamlit as st
import pandas as pd
import pickle
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Assistant Analytics & Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .metric-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 22px;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 12px;
    }
    .response-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: #f8fafc;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
        border: 1px solid #334155;
        margin-top: 15px;
    }
    .command-badge {
        font-family: monospace;
        background-color: #334155;
        color: #38bdf8;
        padding: 4px 8px;
        border-radius: 6px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load pickle file
@st.cache_data
def load_assistant_data():
    try:
        with open("assistant_data.pkl", "rb") as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading assistant_data.pkl: {e}")
        return None

data = load_assistant_data()

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/bot.png", width=110)
    st.title("Assistant Hub")
    
    celebration_fx = st.selectbox(
        "Simulation Effect",
        ["Balloons 🎉", "Snow ❄️", "Toast Notification ⚡"],
        index=0,
    )
    
    st.markdown("---")
    if data:
        st.markdown(f"**Session Created:** `{data.get('created_at', 'N/A')}`")
        user = data.get('user_name')
        st.markdown(f"**Assigned User:** `{user if user else 'Anonymous'}`")
        st.markdown(f"**Logged Commands:** `{data.get('total_commands', 0)}`")

# Main Header
st.title("🤖 Voice Assistant Console & Query Engine")
st.write("Browse recorded command logs and simulate real-time assistant responses.")
st.markdown("---")

if not data:
    st.warning("Please ensure `assistant_data.pkl` is located in the application directory.")
else:
    # Summary Metrics Row
    m1, m2, m3 = st.columns(3)
    history_entries = data.get("history", [])
    
    with m1:
        st.metric(label="Total Logged Queries", value=len(history_entries))
    with m2:
        last_log_time = history_entries[-1]["time"] if history_entries else "None"
        st.metric(label="Latest Interaction", value=last_log_time)
    with m3:
        st.metric(label="Session Status", value="Archived / Loaded")

    st.markdown("---")

    # Command Execution Simulator
    st.subheader("⚡ Assistant Query Simulator")
    st.caption("Select an existing recorded prompt or type a custom command to simulate assistant resolution.")

    # Collect known commands from session history
    known_commands = list({entry.get("command") for entry in history_entries if "command" in entry})
    history_lookup = {entry["command"].lower(): entry["response"] for entry in history_entries}

    col_input, col_action = st.columns([3, 1])
    with col_input:
        selected_command = st.selectbox("Choose a known command from history:", options=known_commands)
        custom_command = st.text_input("Or enter a custom command (overrides dropdown if populated):", placeholder="e.g., date, open YouTube, time...")
    
    query = custom_command.strip() if custom_command.strip() else selected_command

    with col_action:
        st.write("")
        st.write("")
        trigger_btn = st.button("Simulate Execution 🚀", use_container_width=True)

    if trigger_btn:
        with st.spinner("Processing command intent..."):
            time.sleep(0.4)
            
            # Match response from log or generate dynamic fallback
            clean_q = query.lower()
            if clean_q in history_lookup:
                generated_response = history_lookup[clean_q]
            elif "time" in clean_q:
                generated_response = f"The current time is {datetime.now().strftime('%I:%M %p')}"
            elif "date" in clean_q:
                generated_response = f"Today's date is {datetime.now().strftime('%A, %B %d, %Y')}"
            elif "exit" in clean_q:
                generated_response = "Goodbye! Have a great day."
            else:
                generated_response = f"Command '{query}' recognized. No automated action assigned."

            # Trigger chosen visual celebration
            if celebration_fx == "Balloons 🎉":
                st.balloons()
            elif celebration_fx == "Snow ❄️":
                st.snow()
            st.toast("Command executed successfully!", icon="✅")

            # Attractive Response Card
            st.markdown(
                f"""
                <div class="response-card">
                    <span style="font-size: 0.85rem; letter-spacing: 0.08em; text-transform: uppercase; color: #94a3b8;">
                        Assistant Response
                    </span>
                    <h2 style="margin: 10px 0; color: #38bdf8;">"{generated_response}"</h2>
                    <p style="margin: 0; color: #cbd5e1; font-size: 0.95rem;">
                        Input Query: <span class="command-badge">{query}</span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Command History Log
    st.subheader("📜 Recorded Interaction Log")
    if history_entries:
        df_history = pd.DataFrame(history_entries)
        
        # Search & Filter
        search_query = st.text_input("Filter logged interactions:", placeholder="Search by keyword, response, or timestamp...")
        if search_query:
            mask = df_history.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
            df_history = df_history[mask]

        st.dataframe(
            df_history,
            column_config={
                "time": st.column_config.TextColumn("Timestamp"),
                "command": st.column_config.TextColumn("User Command"),
                "response": st.column_config.TextColumn("Assistant Reply"),
            },
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No recorded history entries found in the file.")
