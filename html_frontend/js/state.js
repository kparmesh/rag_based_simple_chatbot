/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - STATE MANAGEMENT
 * ================================================
 */

const State = {
  // Conversation state
  greetingRendered: false,
  conversationId: null,
  activeConversationId: null,
  conversations: {},

  // Guided flow state
  guidedStep: "root",
  guidedFlowActive: true,

  // Message history (current session)
  messages: [],

  /**
   * Initialize state from localStorage
   */
  init() {
    // Only load conversationId (for continuing the last conversation)
    // Don't load activeConversationId on init - that should only be set when 
    // a conversation is actually loaded from history during the session
    this.conversationId = localStorage.getItem(Config.STORAGE.CONVERSATION_ID) || null;
    this.activeConversationId = null;
    this.conversations = this.loadConversations();
  },

  /**
   * Load conversations from localStorage
   * @returns {Object} Conversations object
   */
  loadConversations() {
    try {
      return JSON.parse(localStorage.getItem(Config.STORAGE.CONVERSATIONS) || "{}");
    } catch (e) {
      console.error("Error loading conversations:", e);
      return {};
    }
  },

  /**
   * Save conversations to localStorage
   */
  saveConversations() {
    try {
      localStorage.setItem(Config.STORAGE.CONVERSATIONS, JSON.stringify(this.conversations));
    } catch (e) {
      console.error("Error saving conversations:", e);
    }
  },

  /**
   * Get conversation by ID
   * @param {string} id - Conversation ID
   * @returns {Object|null} Conversation object or null
   */
  getConversation(id) {
    return this.conversations[id] || null;
  },

  /**
   * Create a new conversation
   * @param {string} title - Conversation title
   * @returns {string} New conversation ID
   */
  createConversation(title) {
    const id = Date.now().toString();
    this.conversations[id] = {
      title: title,
      messages: []
    };
    // Only set conversationId for local tracking
    // activeConversationId is only set when loading from history
    this.conversationId = id;
    this.saveConversations();
    localStorage.setItem(Config.STORAGE.CONVERSATION_ID, id);
    return id;
  },

  /**
   * Add message to active conversation
   * @param {string} role - Message role ('user' or 'ai')
   * @param {string} text - Message text
   */
  addMessageToConversation(role, text) {
    if (!this.activeConversationId) return;

    if (!this.conversations[this.activeConversationId]) {
      this.conversations[this.activeConversationId] = {
        title: "New Conversation",
        messages: []
      };
    }

    this.conversations[this.activeConversationId].messages.push({
      role: role,
      text: text
    });

    this.saveConversations();
  },

  /**
   * Load conversation by ID
   * @param {string} id - Conversation ID
   */
  loadConversation(id) {
    if (!this.conversations[id]) return false;

    this.activeConversationId = id;
    this.conversationId = id;
    localStorage.setItem(Config.STORAGE.ACTIVE_CONVERSATION_ID, id);
    localStorage.setItem(Config.STORAGE.CONVERSATION_ID, id);
    return true;
  },

  /**
   * Reset guided flow to root
   */
  resetGuidedFlow() {
    this.guidedStep = "root";
    this.guidedFlowActive = true;
  },

  /**
   * Exit guided flow
   */
  exitGuidedFlow() {
    this.guidedFlowActive = false;
  },

  /**
   * Clear all state
   */
  clear() {
    this.greetingRendered = false;
    this.conversationId = null;
    this.activeConversationId = null;
    this.conversations = {};
    this.guidedStep = "root";
    this.guidedFlowActive = true;
    this.messages = [];

    // Clear localStorage
    localStorage.removeItem(Config.STORAGE.CONVERSATION_ID);
    localStorage.removeItem(Config.STORAGE.ACTIVE_CONVERSATION_ID);
    localStorage.removeItem(Config.STORAGE.CONVERSATIONS);
  }
};

// Initialize state on load
State.init();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = State;
}

