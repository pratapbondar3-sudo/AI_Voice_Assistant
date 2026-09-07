import streamlit as st
import pandas as pd
import pickle
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="AI Assistant Console & Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .response-card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        color: #f8fafc;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.12);
        border: 1px solid #334155;
        margin-top: 15px;
    }
    .badge {
        font-family: monospace;
        background-color: #334155;
        color: #38bdf8;
        padding: 3px 8px;
        border-radius: 6px;
    }
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.55rem 1.75rem;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #1d4ed8, #1e40af);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load Pickle Data
@st.cache_data
def load_assistant_data(file_path="assistant_data.pkl"):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

data = load_assistant_data()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/bot.png", width=95)
    st.title("Assistant Hub")
    effect_style = st.selectbox(
        "Simulation Effect",
        ["Balloons 🎉", "Snow ❄️", "Toast Notification ⚡"],
        index=0,
    )
    st.markdown("---")
    
    if data:
        st.markdown(f"**Assigned User:** `{data.get('user_name') or 'Anonymous'}`")
        st.markdown(f"**Recorded Total:** `{data.get('total_commands', 0)} commands`")
        if "created_at" in data:
            st.markdown(f"**Created At:** `{data.get('created_at')}`")
    else:
        st.info("No pickle data loaded yet.")

# Main View
st.title("🤖 AI Voice Assistant Console")
st.caption("Inspect logged interactions, review execution history, and test assistant command responses.")
st.markdown("---")

if not data:
    st.warning("`assistant_data.pkl` was not found. Please place the file in the project root directory and refresh.")
else:
    history_entries = data.get("history", [])

    # Overview Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Logged Query Events", value=len(history_entries))
    with m2:
        last_event = history_entries[-1]["time"] if history_entries else "None"
        st.metric(label="Latest Event Timestamp", value=last_event)
    with m3:
        st.metric(label="Status", value="Ready / Synchronized")

    st.markdown("---")

    # Command Execution Simulator
    st.subheader("⚡ Command Simulator")
    
    known_commands = list({entry.get("command") for entry in history_entries if "command" in entry})
    history_map = {entry["command"].lower(): entry["response"] for entry in history_entries if "command" in entry}

    col_input, col_action = st.columns([3, 1])
    with col_input:
        selected_command = st.selectbox("Choose past command:", options=known_commands if known_commands else ["open YouTube"])
        custom_input = st.text_input("Or test a custom query:", placeholder="e.g., date, time, open YouTube...")
        query = custom_input.strip() if custom_input.strip() else selected_command

    with col_action:
        st.write("")
        st.write("")
        run_btn = st.button("Simulate 🚀", use_container_width=True)

    if run_btn and query:
        with st.spinner("Resolving response..."):
            time.sleep(0.3)

        clean_q = query.lower()
        if clean_q in history_map:
            response_text = history_map[clean_q]
        elif "time" in clean_q:
            response_text = f"The current time is {datetime.now().strftime('%I:%M %p')}"
        elif "date" in clean_q:
            response_text = f"Today's date is {datetime.now().strftime('%A, %B %d, %Y')}"
        elif "exit" in clean_q or "quit" in clean_q:
            response_text = "Session closed. See you next time!"
        else:
            response_text = f"Command '{query}' acknowledged. No registered automation handler."

        # Trigger effect
        if effect_style == "Balloons 🎉":
            st.balloons()
        elif effect_style == "Snow ❄️":
            st.snow()
        st.toast("Executed successfully!", icon="✅")

        # Response Banner
        st.markdown(
            f"""
            <div class="response-card">
                <span style="font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; color: #94a3b8;">Output Response</span>
                <h3 style="margin: 8px 0; color: #38bdf8;">"{response_text}"</h3>
                <p style="margin: 0; color: #cbd5e1; font-size: 0.9rem;">Triggered by: <span class="badge">{query}</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Interactive Data Table
    st.subheader("📜 Interaction History Log")
    if history_entries:
        df = pd.DataFrame(history_entries)
        
        search_filter = st.text_input("Filter records:", placeholder="Search by query, timestamp, or reply...")
        if search_filter:
            mask = df.apply(lambda row: row.astype(str).str.contains(search_filter, case=False).any(), axis=1)
            df = df[mask]

        st.dataframe(
            df,
            column_config={
                "time": st.column_config.TextColumn("Timestamp"),
                "command": st.column_config.TextColumn("Command"),
                "response": st.column_config.TextColumn("Assistant Response"),
            },
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No query logs available in the provided pickle structure.")
