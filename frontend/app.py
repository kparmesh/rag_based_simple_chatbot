import streamlit as st

from config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
    DEFAULT_GUIDED_STEP,
    DEFAULT_CONVERSATION_MODE,
    RECENT_CONVERSATIONS_LIMIT,
)
from api.client import ChatClient
from ui.guided_flow import render_guided_flow
from utils.helpers import (
    generate_title_from_message,
    init_guided_greeting,
    reset_conversation,
)


def initialize_session_state():
    """Initialize all session state variables."""
    if "client" not in st.session_state:
        st.session_state.client = ChatClient()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "guided_flow_active" not in st.session_state:
        st.session_state.guided_flow_active = True

    if "guided_step" not in st.session_state:
        st.session_state.guided_step = DEFAULT_GUIDED_STEP

    if "conversation_mode" not in st.session_state:
        st.session_state.conversation_mode = DEFAULT_CONVERSATION_MODE


def render_sidebar():
    """Render the sidebar with conversation management."""
    with st.sidebar:
        st.title("🤖 Powered by Toolboxx Chat Bot")
        st.markdown("---")
        
        # Conversation management
        st.subheader("Conversations")
        
        if st.button("➕ New Chat", use_container_width=True):
            try:
                reset_conversation()
                st.rerun()
            except Exception as e:
                st.error(f"Error creating conversation: {e}")
        
        # List conversations
        try:
            conversations = st.session_state.client.list_conversations()
            if conversations["conversations"]:
                st.markdown("**Recent Chats:**")
                for conv in conversations["conversations"][:RECENT_CONVERSATIONS_LIMIT]:
                    if st.button(
                        f"💬 {conv['title']}",
                        key=f"conv_{conv['id']}",
                        use_container_width=True
                    ):
                        st.session_state.conversation_id = conv["id"]
                        st.session_state.messages = st.session_state.client.get_messages(conv["id"])
                        st.session_state.conversation_mode = "chat"
                        st.session_state.guided_flow_active = False
                        st.rerun()
        except Exception as e:
            st.warning("Could not load conversations")
        
        st.markdown("---")


def render_chat_messages():
    """Render all chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_chat_input(prompt: str):
    """Handle user chat input and get assistant response."""
    st.session_state.conversation_mode = "chat"
    st.session_state.guided_flow_active = False
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Create conversation on first message
                if st.session_state.conversation_id is None:
                    title = generate_title_from_message(prompt)
                    conversation = st.session_state.client.create_conversation(title=title)
                    st.session_state.conversation_id = conversation["id"]
                    
                response = st.session_state.client.chat(
                    message=prompt,
                    conversation_id=st.session_state.conversation_id
                )
                
                answer = response["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.markdown(answer)
                
                # Update conversation ID
                st.session_state.conversation_id = response["conversation_id"]
                
            except Exception as e:
                st.error(f"Error: {e}")


def main():
    """Main function to run the Streamlit app."""
    
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE
    )

    # Initialize session state
    initialize_session_state()

    # Ensure greeting on refresh (safe now)
    if (
        st.session_state.conversation_mode == "guided"
        and not st.session_state.messages
    ):
        init_guided_greeting()
    
    # Render sidebar
    render_sidebar()
    
    # Main chat area
    st.title("💬 Trust Inheritence Legal AI Assistant")
    
    # Display messages
    render_chat_messages()

    # Render guided flow
    st.session_state.client = ChatClient()  # Ensure client is available
    render_guided_flow()

    # Chat input
    if prompt := st.chat_input("Write your Query here..."):
        handle_chat_input(prompt)


if __name__ == "__main__":
    main()

