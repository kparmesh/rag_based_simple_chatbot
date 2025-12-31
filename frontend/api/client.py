import requests
from config import API_BASE_URL


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

