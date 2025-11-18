import streamlit as st
import time
import json
from datetime import datetime

from models import Master
Master = Master()


st.set_page_config(page_title="DAI Chatbot", page_icon="💬", layout="centered")

st.title("DAI — Simple Chatbot Demo")
st.caption("Local demo UI that can optionally call a model hook from `models` if provided.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Navigation")
    view = st.radio("Go to", ["Chatbot", "History"], index=0)
    st.markdown("---")
    if st.button("Clear All History"):
        st.session_state.messages = []
        st.success("Chat history cleared")
    st.markdown("---")
    st.caption("Use the assistant reply box to post model-generated or manual replies.")


def render_chat():
    """Render the chat UI and handle input/response."""
    # Display existing messages
    for msg in st.session_state.messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    # Accept user input
    user_prompt = st.chat_input("Send a message...")
    if user_prompt:
        # Append user message and display immediately
        user_entry = {
            "role": "user",
            "content": user_prompt,
            "time": datetime.utcnow().isoformat(),
        }
        st.session_state.messages.append(user_entry)
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Attempt to generate an assistant reply via a model hook if available.
        assistant_posted = False
        if Master is not None:
            try:
                assistant_text = Master.choose_question()
                if assistant_text:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "time": datetime.utcnow().isoformat(),
                    })
                    with st.chat_message("assistant"):
                        st.markdown(assistant_text)
                    assistant_posted = True
            except Exception as e:
                st.warning(f"Model reply hook raised an exception: {e}")

        # If no model hook produced a reply, show a manual assistant reply box
        if not assistant_posted:
            st.markdown("---")
            st.subheader("Assistant reply (manual)")
            if "assistant_draft" not in st.session_state:
                st.session_state.assistant_draft = ""
            assistant_input = st.text_area("Assistant reply", value=st.session_state.assistant_draft, key="assistant_draft")
            if st.button("Post assistant reply"):
                content = assistant_input.strip()
                if content:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content,
                        "time": datetime.utcnow().isoformat(),
                    })
                    st.session_state.assistant_draft = ""
                    st.experimental_rerun()


def render_history():
    """Render a simple history page with download option."""
    st.header("Chat History")
    msgs = st.session_state.messages
    if not msgs:
        st.info("No messages yet. Start a conversation in the Chatbot view.")
        return

    # Show messages in reverse chronological order (newest last in chat style)
    for msg in msgs:
        ts = msg.get("time")
        t = ts if ts else "-"
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        st.markdown(f"**{role.title()}** — _{t}_  \\n+{content}")
        st.markdown("---")

    # Provide a download of the raw history as JSON
    json_str = json.dumps(msgs, indent=2)
    st.download_button("Download History (JSON)", json_str, file_name="chat_history.json")


if view == "Chatbot":
    render_chat()
else:
    render_history()
