import streamlit as st
import time
import json
from datetime import datetime
import models

@st.cache_resource
def load_master():
    return models.Master()

MasterModel = load_master()

st.markdown("""
<style>
.fixed-header {
    position: fixed;
    top: 20px; /* push header down from top */
    left: 0;
    right: 0;
    background-color: dark blue;
    padding: 20px 0;  /* vertical padding */
    z-index: 9999;
    border-bottom: 1px solid #ddd;

    /* horizontal centering */
    text-align: center;
}
.chat-wrapper {
    margin-top: 100px; /* space for fixed header */
}
.chat-box {
    height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
</style>
""", unsafe_allow_html=True)



st.set_page_config(page_title="DAI Chatbot", page_icon="💬", layout="centered")

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
    """ Chatbot UI """

    # Set state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "awaiting_answer" not in st.session_state:
        st.session_state.awaiting_answer = False
    if "started" not in st.session_state:
        st.session_state.started = False

    # Set header
    st.markdown("""
        <div class="fixed-header">
            <h1>ML Knowledge Evaluator Chatbot</h1>
        </div>
    """, unsafe_allow_html=True)

    # Set chat in its own wrapper
    st.markdown('<div class="chat-wrapper">', unsafe_allow_html=True)

    # Scrollable chat area
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)

    # Ask question
    if not st.session_state.started:
        q = MasterModel.choose_question()
        st.session_state.messages.append({
            "role": "assistant",
            "content": q,
            "time": datetime.utcnow().isoformat(),
        })
        st.session_state.started = True
        st.session_state.awaiting_answer = True
        st.rerun()

    # User input
    user_msg = st.chat_input("Your answer...")

    # Chat loop
    if user_msg:
        st.session_state.messages.append({
            "role": "user",
            "content": user_msg,
            "time": datetime.utcnow().isoformat(),
        })
        st.session_state.just_got_user = user_msg
        st.rerun()

    if "just_got_user" in st.session_state:
        answer = st.session_state.just_got_user
        del st.session_state["just_got_user"]

        reply = MasterModel.evaluate_answer(answer)
        st.session_state.messages.append({
            "role": "assistant",
            "content": reply,
            "time": datetime.utcnow().isoformat(),
        })

        next_q = MasterModel.choose_question()
        st.session_state.messages.append({
            "role": "assistant",
            "content": next_q,
            "time": datetime.utcnow().isoformat(),
        })

        st.session_state.awaiting_answer = True
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)



# Show history
def render_history():
    """Render a simple history page with download option."""
    st.header("Chat History")
    msgs = st.session_state.messages
    if not msgs:
        st.info("No messages yet. Start a conversation in the Chatbot view.")
        return

    # Order 
    for msg in msgs:
        ts = msg.get("time")
        t = ts if ts else "-"
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        st.markdown(f"**{role.title()}** — _{t}_  \: {content}")
        st.markdown("---")

    # Let download as Json
    json_str = json.dumps(msgs, indent=2)
    st.download_button("Download History (JSON)", json_str, file_name="chat_history.json")


if view == "Chatbot":
    render_chat()
else:
    render_history()
