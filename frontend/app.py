"""
Frontend application for the RAG Chat Bot.
"""
import streamlit as st
import requests


# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"


class ChatClient:
    """Client for interacting with the chat API."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def chat(self, message: str, conversation_id: int = None, use_history: bool = True):
        """Send a chat message."""
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "message": message,
                "conversation_id": conversation_id,
                "use_history": use_history
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_messages(self, conversation_id: int):
        """Get messages for a conversation."""
        response = requests.get(f"{self.base_url}/chat/{conversation_id}/messages")
        response.raise_for_status()
        return response.json()
    
    def create_conversation(self, title: str = None):
        """Create a new conversation."""
        response = requests.post(
            f"{self.base_url}/conversations",
            json={"title": title} if title else None
        )
        response.raise_for_status()
        return response.json()
    
    def list_conversations(self):
        """List all conversations."""
        response = requests.get(f"{self.base_url}/conversations")
        response.raise_for_status()
        return response.json()
    
    def delete_conversation(self, conversation_id: int):
        """Delete a conversation."""
        response = requests.delete(f"{self.base_url}/conversations/{conversation_id}")
        response.raise_for_status()
        return response.json()
    
    def upload_document(self, file):
        """Upload a document."""
        response = requests.post(
            f"{self.base_url}/documents/upload",
            files={"file": file}
        )
        response.raise_for_status()
        return response.json()
    
    def index_documents(self):
        """Index all uploaded documents."""
        response = requests.post(f"{self.base_url}/documents/index")
        response.raise_for_status()
        return response.json()
    
    def list_documents(self):
        """List all documents."""
        response = requests.get(f"{self.base_url}/documents")
        response.raise_for_status()
        return response.json()
    
    def generate_title_from_message(self, message: str) -> str:
        words = message.strip().split()
        title = " ".join(words[:8])
        return title + "..." if len(words) > 8 else title


def main():
    """Main function to run the Streamlit app."""
    
    st.set_page_config(
        page_title="Toolboxx Chat Bot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "client" not in st.session_state:
        st.session_state.client = ChatClient()
    
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 Powered by Toolboxx Chat Bot")
        st.markdown("---")
        
        # Conversation management
        st.subheader("Conversations")
        
        if st.button("➕ New Chat", use_container_width=True):
            try:
                st.session_state.conversation_id = None
                st.session_state.messages = []
                st.rerun()
            except Exception as e:
                st.error(f"Error creating conversation: {e}")
        
        # List conversations
        try:
            conversations = st.session_state.client.list_conversations()
            if conversations["conversations"]:
                st.markdown("**Recent Chats:**")
                for conv in conversations["conversations"][:5]:
                    if st.button(
                        f"💬 {conv['title']}",
                        key=f"conv_{conv['id']}",
                        use_container_width=True
                    ):
                        st.session_state.conversation_id = conv["id"]
                        st.session_state.messages = st.session_state.client.get_messages(conv["id"])
                        st.rerun()
        except Exception as e:
            st.warning("Could not load conversations")
        
        st.markdown("---")
    
    # Main chat area
    st.title("💬 Trust Inheritence Legal AI Assistant")
    
    # Display messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Hello! I am your Trust Inheritance Legal AI Assistant. How can I assist you today?"):
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
                        title = st.session_state.client.generate_title_from_message(prompt)
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


if __name__ == "__main__":
    main()

