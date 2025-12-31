import streamlit as st
from config import MAX_TITLE_WORDS


def generate_title_from_message(message: str) -> str:
    """Generate a title from a message by taking the first N words."""
    words = message.strip().split()
    title = " ".join(words[:MAX_TITLE_WORDS])
    return title + "..." if len(words) > MAX_TITLE_WORDS else title


def init_guided_greeting():
    """Initialize the guided flow greeting message."""
    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "Hello! I am your Trust Inheritance Legal AI Assistant, "
                "How can I help you today!"
            )
        })


def reset_conversation():
    """Reset conversation state to start fresh."""
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.guided_flow_active = True
    st.session_state.guided_step = "root"
    st.session_state.conversation_mode = "guided"
    init_guided_greeting()


def exit_guided_flow():
    """Exit the guided flow and enter chat mode."""
    st.session_state.guided_flow_active = False
    st.session_state.conversation_mode = "chat"

