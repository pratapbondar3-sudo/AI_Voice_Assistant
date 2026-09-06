import os
import pickle
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Voice Assistant Dashboard",
    page_icon="🎙️",
    layout="wide"
)

PKL_FILE_PATH = "assistant_data.pkl"

@st.cache_data
def load_assistant_data(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        return pickle.load(f)

data = load_assistant_data(PKL_FILE_PATH)

st.title("🎙️ AI Voice Assistant Dashboard")
st.caption("Inspect session metrics, saved preferences, and interaction logs.")

if data is None:
    st.error(f"File `{PKL_FILE_PATH}` not found. Ensure the file is in the application root directory.")
else:
    # Key Metric Cards
    col1, col2, col3 = st.columns(3)
    user_name = data.get("user_name") or "Guest / Unknown"
    total_commands = data.get("total_commands", 0)
    created_at = data.get("created_at", "N/A")

    col1.metric("Registered User", user_name)
    col2.metric("Total Commands Logged", total_commands)
    col3.metric("Session Created At", created_at)

    st.divider()

    # Interaction History Table
    st.subheader("Interactive Session History")
    history = data.get("history", [])

    if history:
        df = pd.DataFrame(history)
        df.columns = [col.capitalize() for col in df.columns]
        
        # Display formatted table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # Chat Bubble Transcript View
        with st.expander("💬 View as Chat Transcript", expanded=False):
            for entry in history:
                with st.chat_message("user"):
                    st.markdown(f"**{entry.get('command', '')}**")
                    st.caption(f"Time: {entry.get('time', '')}")
                with st.chat_message("assistant"):
                    st.markdown(entry.get("response", ""))
    else:
        st.info("No interactions recorded in this state file.")

    # Raw Pickle Inspection
    with st.expander("🛠️ View Raw Stored Dictionary"):
        st.json(data)
