/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - CONFIGURATION
 * ================================================
 */

const Config = {
  // API Configuration
  API: {
    BASE_URL: "http://localhost:8000/api/v1",
    ENDPOINTS: {
      CHAT: "/chat",
      CONVERSATIONS: "/conversations",
      CONVERSATION_MESSAGES: "/conversations/{id}/messages",
      CONVERSATION_DELETE: "/conversations/{id}"
    }
  },

  // UI Configuration
  UI: {
    LAUNCHER_POSITION: {
      BOTTOM: "20px",
      RIGHT: "20px"
    },
    WINDOW_POSITION: {
      BOTTOM: "90px",
      RIGHT: "20px"
    },
    WINDOW_SIZE: {
      WIDTH: "380px",
      HEIGHT: "560px"
    },
    LAUNCHER_SIZE: {
      WIDTH: "60px",
      HEIGHT: "60px"
    }
  },

  // Storage Keys
  STORAGE: {
    CONVERSATION_ID: "conversation_id",
    ACTIVE_CONVERSATION_ID: "activeConversationId",
    CONVERSATIONS: "conversations"
  },

  // Title Generation
  TITLE: {
    MAX_WORDS: 8
  },

  // Default Greeting
  GREETING: {
    MESSAGE: "Hello! I am your Trust Inheritance Legal AI Assistant, How can I help you today!",
    OPTIONS: [
      "Legal Document Support",
      "Bereavement Support",
      "Final Wishes Support"
    ]
  },

  // Guided Flow Steps
  GUIDED_FLOW: {
    STEPS: {
      ROOT: "root",
      CHAT: "chat",
      LEGAL: "legal",
      WILL: "will",
      LIVING_WILL: "living_will",
      LPA: "lpa",
      BEREAVEMENT: "bereavement",
      FINAL: "final"
    }
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Config;
}

