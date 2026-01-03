/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - CONVERSATION HISTORY
 * ================================================
 */

const History = {
  // DOM Elements
  elements: {
    sidebar: null,
    list: null,
    menuBtn: null,
    closeHistoryBtn: null,
    closeBtn: null,
    newChatBtn: null
  },

  // Cache for conversations from API
  conversationsCache: null,

  /**
   * Initialize history functionality
   */
  init() {
    this.cacheElements();
    this.bindEvents();
  },

  /**
   * Cache DOM elements for better performance
   */
  cacheElements() {
    this.elements.sidebar = document.getElementById("history-sidebar");
    this.elements.list = document.getElementById("history-list");
    this.elements.menuBtn = document.getElementById("menu-btn");
    this.elements.closeHistoryBtn = document.getElementById("close-history");
    this.elements.closeBtn = document.getElementById("close-btn");
    this.elements.newChatBtn = document.getElementById("new-chat-btn");
  },

  /**
   * Bind event listeners
   */
  bindEvents() {
    if (this.elements.menuBtn) {
      this.elements.menuBtn.onclick = () => this.openSidebar();
    }

    if (this.elements.closeHistoryBtn) {
      this.elements.closeHistoryBtn.onclick = () => this.closeSidebar();
    }

    if (this.elements.closeBtn) {
      this.elements.closeBtn.onclick = () => Chat.closeWindow();
    }

    if (this.elements.newChatBtn) {
      this.elements.newChatBtn.onclick = () => {
        Chat.resetToNewChat();
        // Open chat window if not already open
        if (Chat.elements.window && !Chat.elements.window.classList.contains("open")) {
          Chat.elements.window.classList.add("open");
        }
        this.closeSidebar();
      };
    }
  },

  /**
   * Open history sidebar
   */
  async openSidebar() {
    if (!this.elements.sidebar) return;

    // Show loading state
    this.showLoading();

    // Fetch conversations from API
    await this.fetchConversations();

    this.elements.sidebar.classList.add("open");
  },

  /**
   * Show loading state in history list
   */
  showLoading() {
    if (!this.elements.list) return;
    this.elements.list.innerHTML = '<div class="history-loading">Loading conversations...</div>';
  },

  /**
   * Fetch conversations from API
   */
  async fetchConversations() {
    try {
      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.CONVERSATIONS}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch conversations");
      }

      const data = await response.json();
      this.conversationsCache = data.conversations || [];
      this.renderSidebar();
    } catch (error) {
      console.error("Error fetching conversations:", error);
      this.renderError();
    }
  },

  /**
   * Render error state
   */
  renderError() {
    if (!this.elements.list) return;
    this.elements.list.innerHTML =
      '<div class="history-error">Failed to load conversations</div>';
  },

  /**
   * Close history sidebar
   */
  closeSidebar() {
    if (!this.elements.sidebar) return;
    this.elements.sidebar.classList.remove("open");
  },

  /**
   * Render history sidebar content
   */
  renderSidebar() {
    if (!this.elements.list) return;

    this.elements.list.innerHTML = "";

    const conversations = this.conversationsCache || [];

    if (conversations.length === 0) {
      this.elements.list.innerHTML =
        '<div class="history-empty">No conversations yet</div>';
      return;
    }

    // Sort by created_at descending (newest first)
    conversations.sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return dateB - dateA;
    });

    conversations.forEach((conversation) => {
      const item = this.createHistoryItem(conversation);
      this.elements.list.appendChild(item);
    });
  },

  /**
   * Create a history item element
   * @param {Object} conversation - Conversation object from API
   * @returns {HTMLElement} History item element
   */
  createHistoryItem(conversation) {
    const item = document.createElement("div");
    item.className = "history-item";
    item.dataset.id = conversation.id;

    // Create content wrapper
    const content = document.createElement("div");
    content.className = "history-item-content";

    // Create title element
    const title = document.createElement("div");
    title.className = "history-item-title";
    title.textContent = conversation.title || "Untitled Conversation";
    content.appendChild(title);

    // Create date element
    const date = document.createElement("div");
    date.className = "history-item-date";
    date.textContent = this.formatDate(conversation.created_at);
    content.appendChild(date);

    item.appendChild(content);

    // Create delete button
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "history-item-delete";
    deleteBtn.textContent = "✕";
    deleteBtn.setAttribute("aria-label", "Delete conversation");
    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      this.deleteConversation(conversation.id);
    };
    item.appendChild(deleteBtn);

    // Highlight active conversation
    if (conversation.id === State.activeConversationId) {
      item.classList.add("active");
    }

    // Click handler for loading conversation
    content.onclick = () => {
      this.loadConversation(conversation.id);
      this.closeSidebar();
    };

    return item;
  },

  /**
   * Format date string to readable format
   * @param {string} dateString - ISO date string
   * @returns {string} Formatted date
   */
  formatDate(dateString) {
    if (!dateString) return "";

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return "Today";
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  },

  /**
   * Load a conversation and its messages
   * @param {number} id - Conversation ID
   */
  async loadConversation(id) {
    try {
      // Show loading state
      Chat.clearChat();
      Chat.addMessage("ai", "Loading conversation...");

      // Fetch messages from API
      const messages = await this.fetchConversationMessages(id);

      if (!messages || messages.length === 0) {
        Chat.addMessage("ai", "No messages in this conversation.");
        return;
      }

      // Clear loading message
      Chat.clearChat();

      // Update state - sync both IDs
      State.activeConversationId = id;
      State.conversationId = id;
      State.greetingRendered = true;
      State.exitGuidedFlow();
      State.guidedStep = "chat";

      // Save to localStorage
      localStorage.setItem(Config.STORAGE.ACTIVE_CONVERSATION_ID, id);
      localStorage.setItem(Config.STORAGE.CONVERSATION_ID, id);

      // Load and display messages
      messages.forEach((msg) => {
        Chat.addMessage(msg.role, msg.content);
      });
    } catch (error) {
      console.error("Error loading conversation:", error);
      Chat.clearChat();
      Chat.addMessage("ai", "Failed to load conversation. Please try again.");
    }
  },

  /**
   * Fetch messages for a conversation from API
   * @param {number} conversationId - Conversation ID
   * @returns {Array} Array of messages
   */
  async fetchConversationMessages(conversationId) {
    const endpoint = Config.API.ENDPOINTS.CONVERSATION_MESSAGES.replace(
      "{id}",
      conversationId
    );

    const response = await fetch(
      `${Config.API.BASE_URL}${endpoint}`
    );

    if (!response.ok) {
      throw new Error("Failed to fetch conversation messages");
    }

    const data = await response.json();
    // Handle both array response and wrapped response
    return Array.isArray(data) ? data : (data.messages || []);
  },

  /**
   * Delete a conversation
   * @param {string} id - Conversation ID
   */
  async deleteConversation(id) {
    if (!confirm("Are you sure you want to delete this conversation?")) {
      return;
    }

    try {
      // Call delete endpoint on backend
      const endpoint = Config.API.ENDPOINTS.CONVERSATION_DELETE.replace("{id}", id);
      const response = await fetch(`${Config.API.BASE_URL}${endpoint}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete conversation");
      }

      // If the deleted conversation was active, redirect to new chat
      if (id === State.activeConversationId) {
        State.activeConversationId = null;
        Chat.resetToNewChat();
      }

      // Refresh the conversations list
      await this.fetchConversations();
      this.renderSidebar();
    } catch (error) {
      console.error("Error deleting conversation:", error);
      alert("Failed to delete conversation. Please try again.");
    }
  },

  /**
   * Clear all conversations (optional - if backend supports it)
   */
  clearAll() {
    // Note: This would need a DELETE endpoint on the backend
    console.warn("Clear all not implemented - backend endpoint needed");
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = History;
}

