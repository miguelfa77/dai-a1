import streamlit as st
import time
import json
from datetime import datetime
import evaluate
import models

@st.cache_resource
def load_master():
    return models.Master()

MasterModel = load_master()

st.markdown("""
<style>
:root {
    --chat-width: min(720px, 90vw);
    --chat-offset: calc((100vw - var(--chat-width))/2);
    --button-gap: 160px;
}
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
    margin-top: 120px; /* space for fixed header */
}
.chat-box {
    height: 500px;
    overflow-y: auto;
    padding-right: 10px;
}
.exam-button-container {
    position: fixed;
    bottom: 28px;
    right: calc(var(--chat-offset) + 12px);
    z-index: 10000;
}
div[data-testid="stChatInput"] {
    width: var(--chat-width);
    margin-left: auto;
    margin-right: auto;
    padding-right: var(--button-gap);
}
@media (max-width: 900px) {
    :root {
        --button-gap: 110px;
    }
}
@media (min-width: 901px) {
    :root {
        --button-gap: 190px;
    }
}
</style>
""", unsafe_allow_html=True)



st.set_page_config(page_title="DAI Chatbot", page_icon="💬", layout="centered")

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
    if "exam_mode" not in st.session_state:
        st.session_state.exam_mode = False
    if "awaiting_answer" not in st.session_state:
        st.session_state.awaiting_answer = False
    if "awaiting_feedback" not in st.session_state:
        st.session_state.awaiting_feedback = False

    # Queue new exam mode question when needed
    if (
        st.session_state.exam_mode
        and not st.session_state.awaiting_answer
        and not st.session_state.awaiting_feedback
    ):
        question = MasterModel.choose_question()
        st.session_state.messages.append({
            "role": "assistant",
            "content": question,
            "time": datetime.utcnow().isoformat(),
        })
        st.session_state.awaiting_answer = True
        st.rerun()

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

    user_msg = st.chat_input("Type your message...")

    # Static exam mode button
    st.markdown('<div class="exam-button-container">', unsafe_allow_html=True)
    button_label = "Exam mode: ON" if st.session_state.exam_mode else "Exam mode: OFF"
    button_clicked = st.button(button_label, key="exam_toggle")
    st.markdown('</div>', unsafe_allow_html=True)

    if button_clicked:
        st.session_state.exam_mode = not st.session_state.exam_mode
        if st.session_state.exam_mode:
            st.session_state.awaiting_answer = False
            st.session_state.awaiting_feedback = False
            toggle_msg = "Exam mode activated. I will start asking questions."
        else:
            st.session_state.awaiting_answer = False
            st.session_state.awaiting_feedback = False
            toggle_msg = "Exam mode deactivated. Returning to conversational mode."

        st.session_state.messages.append({
            "role": "assistant",
            "content": toggle_msg,
            "time": datetime.utcnow().isoformat(),
        })
        st.rerun()

    if user_msg:
        content = user_msg
        if st.session_state.exam_mode and st.session_state.awaiting_feedback:
            content = f"(Feedback) {user_msg}"

        st.session_state.messages.append({
            "role": "user",
            "content": content,
            "time": datetime.utcnow().isoformat(),
        })

        if st.session_state.exam_mode:
            if st.session_state.awaiting_feedback:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Thanks for the feedback! Here's the next question.",
                    "time": datetime.utcnow().isoformat(),
                })
                st.session_state.awaiting_feedback = False
                st.session_state.awaiting_answer = False
            else:
                reply = MasterModel.evaluate_answer(user_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": type(reply),
                    "time": datetime.utcnow().isoformat(),
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Let me know what you thought of that feedback.",
                    "time": datetime.utcnow().isoformat(),
                })
                st.session_state.awaiting_answer = False
                st.session_state.awaiting_feedback = True
        else:
            reply = MasterModel.normal_answer(user_msg, st.session_state.messages)
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "time": datetime.utcnow().isoformat(),
            })

        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)



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
        st.markdown(f"**{role.title()}** — _{t}_  \:{content}")
        st.markdown("---")

    # Let download as Json
    json_str = json.dumps(msgs, indent=2)
    st.download_button("Download History (JSON)", json_str, file_name="chat_history.json")


if view == "Chatbot":
    render_chat()
else:
    render_history()
