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

    def render_guided_flow(self):
        if not st.session_state.guided_flow_active:
            return

        # ---- ROOT OPTIONS ----
        if st.session_state.guided_step == "root":
            st.markdown("<br>", unsafe_allow_html=True)

            # Centered horizontal buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Legal Document Support", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "Legal Document Support"
                    })
                    st.session_state.guided_step = "legal"
                    st.rerun()

            with col2:
                if st.button("Bereavement Support", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "Bereavement Support"
                    })
                    st.session_state.guided_step = "breavement"
                    st.rerun()

            with col3:
                if st.button("Final Wishes Support", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "Final Wishes Support"
                    })
                    st.session_state.guided_step = "final_wishes"
                    st.rerun()

        # ---- Final Wishes OPTIONS ----
        elif st.session_state.guided_step == "final_wishes":
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5, col6 = st.columns(6, gap="large")

            with col1:
                if st.button("My Documents", use_container_width=True, key="final_wishes_my_documents"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check Your Documents]"
                            "(https://trustinheritance.toolboxx.co.uk/mydigifile)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col2:
                if st.button("Personal Messages", use_container_width=True, key="final_wishes_personal_messages"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check your Personal Messages]"
                            "(https://trustinheritance.toolboxx.co.uk/payment/personal-message)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col3:
                if st.button("Funeral Wishes", use_container_width=True, key="final_wishes_funeral_wishes"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check your Funeral Wishes]"
                            "(https://trustinheritance.toolboxx.co.uk/payment/what-to-do-when-planning-your-funeral)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col4:
                if st.button("My Digital Legacy", use_container_width=True, key="final_wishes_digital_legacy"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here for Full Estate Administration]"
                            "(https://trustinheritance.toolboxx.co.uk/payment/digital-assets)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col5:
                if st.button("Trusted People", use_container_width=True, key="final_wishes_trusted_people"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to add your Trusted People]"
                            "(https://trustinheritance.toolboxx.co.uk/profile#tab-trusted)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()
            
            with col6:
                if st.button("Nags", use_container_width=True, key="final_wishes_nags"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check your Nags]"
                            "(https://trustinheritance.toolboxx.co.uk/nags)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

        # ---- Bereavement OPTIONS ----
        elif st.session_state.guided_step == "breavement":
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3, col4, col5 = st.columns(5, gap="large")

            with col1:
                if st.button("A Little Help", use_container_width=True, key="bereavement_little_help"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check Bereavement Guide]"
                            "(https://trustinheritance.toolboxx.co.uk/holder/10-steps)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col2:
                if st.button("A Little More Help", use_container_width=True, key="bereavement_more_help"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check our Executor Toolkit]"
                            "(https://trustinheritance.toolboxx.co.uk/"
                            "what-to-do-when-someone-dies/2808/questionnaire/step/11)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col3:
                if st.button("Lots of Help", use_container_width=True, key="bereavement_lots_help"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to check Executor Toolkit Plus]"
                            "(https://trustinheritance.toolboxx.co.uk/"
                            "payment/executor-toolkit-plus/5175)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col4:
                if st.button("Hand It All Over", use_container_width=True, key="bereavement_hand_over"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here for Full Estate Administration]"
                            "(https://trustinheritance.toolboxx.co.uk/estate-administration)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col5:
                if st.button("Online Grief Support", use_container_width=True, key="bereavement_grief_support"):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here for Online Grief Support]"
                            "(https://trustinheritance.toolboxx.co.uk/grief-support)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

        # ---- LEGAL OPTIONS ----
        elif st.session_state.guided_step == "legal":
            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                if st.button("Will Writing", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "Will Writing"
                    })
                    st.session_state.guided_step = "will_mode"
                    st.rerun()

            with col2:
                if st.button("Living Will", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to start your Living Will]"
                            "(https://trustinheritance.toolboxx.co.uk/"
                            "living-will/5999/questionnaire/step/2)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col3:
                if st.button("Lasting Power of Attorney (LPA)", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "Lasting Power of Attorney (LPA)"
                    })
                    st.session_state.guided_step = "lpa_mode"
                    st.rerun()
        
        # ---- LPA MODE ----
        elif st.session_state.guided_step == "lpa_mode":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### LPA Options")

            col1, col2, col3 = st.columns(3, gap="large")

            with col1:
                if st.button("Online", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "👉 [Click here to start writing your LPA]"
                            "(https://trustinheritance.toolboxx.co.uk/select-lpa)"
                        )
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col2:
                if st.button("Telephone", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Telephone-based LPA support is available."
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()

            with col3:
                if st.button("Video", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Video-based LPA support is available."
                    })
                    st.session_state.guided_flow_active = False
                    st.session_state.conversation_mode = "chat"
                    st.rerun()


        # ---- WILL MODE ----
        elif st.session_state.guided_step == "will_mode":
            st.markdown("### Will Writing Options")
            col1, col2, col3 = st.columns(3)

            if col1.button("Online"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "👉 [Click here to start writing your will](https://trustinheritance.toolboxx.co.uk/select-will)"
                })
                st.session_state.guided_flow_active = False
                st.rerun()

            if col2.button("Telephone"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Telephone-based will writing support is available."
                })
                st.session_state.guided_flow_active = False
                st.rerun()

            if col3.button("Video"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Video-based will writing support is available."
                })
                st.session_state.guided_flow_active = False
                st.rerun()

def main():
    """Main function to run the Streamlit app."""
    
    st.set_page_config(
        page_title="Toolboxx Chat Bot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # -------------------------------------------------
    # 1️⃣ INITIALIZE SESSION STATE
    # -------------------------------------------------
    if "client" not in st.session_state:
        st.session_state.client = ChatClient()

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "guided_flow_active" not in st.session_state:
        st.session_state.guided_flow_active = True

    if "guided_step" not in st.session_state:
        st.session_state.guided_step = "root"  # root | legal | will_mode

    if "conversation_mode" not in st.session_state:
        st.session_state.conversation_mode = "guided"  # guided | chat

    # -------------------------------------------------
    # 2️⃣ HELPER FUNCTIONS
    # -------------------------------------------------
    def init_guided_greeting():
        if not st.session_state.messages:
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "Hello! I am your Trust Inheritance Legal AI Assistant, "
                    "How can I help you today!"
                )
            })

    # -------------------------------------------------
    # 3️⃣ ENSURE GREETING ON REFRESH (SAFE NOW)
    # -------------------------------------------------
    if (
        st.session_state.conversation_mode == "guided"
        and not st.session_state.messages
    ):
        init_guided_greeting()
    
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
                st.session_state.guided_flow_active = True
                st.session_state.guided_step = "root"
                st.session_state.conversation_mode = "guided"
                init_guided_greeting()
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
                        st.session_state.conversation_mode = "chat"
                        st.session_state.guided_flow_active = False
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

    st.session_state.client.render_guided_flow()

    # Chat input
    if prompt := st.chat_input("Write your Query here..."):
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

