/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - CHAT FUNCTIONALITY
 * ================================================
 */

const Chat = {
  // DOM Elements
  elements: {
    window: null,
    body: null,
    input: null,
    sendBtn: null,
    launcher: null
  },

  /**
   * Debug helper: inject an array of messages into the chat (simulate history load)
   * Usage from browser console after page load: Chat.debugInjectMessages([{role:'ai', content:'Hello'}])
   * @param {Array<{role:string,content:string}>} messages
   */
  debugInjectMessages(messages) {
    if (!Array.isArray(messages)) return;
    this.clearChat();
    messages.forEach(m => {
      try {
        this.addMessage(m.role, m.content);
      } catch (e) {
        if (DEBUG) console.error('debugInjectMessages error', e);
      }
    });
  },

  /**
   * Initialize chat functionality
   */
  init() {
    this.cacheElements();
    this.bindEvents();
  },

  /**
   * Cache DOM elements for better performance
   */
  cacheElements() {
    this.elements.window = document.getElementById("chatWidget");
    this.elements.body = document.getElementById("chatMessages");
    this.elements.input = document.getElementById("chatInput");
    this.elements.sendBtn = document.querySelector(".send-btn");
    this.elements.launcher = document.querySelector(".chat-bubble");
  },

  /**
   * Bind event listeners
   */
  bindEvents() {
    if (this.elements.launcher) {
      this.elements.launcher.onclick = () => this.toggleWindow();
    }

    if (this.elements.sendBtn) {
      this.elements.sendBtn.onclick = () => this.sendMessage();
    }

    if (this.elements.input) {
      // Handle Enter key in textarea
      this.elements.input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });

      // Auto-resize textarea
      this.elements.input.addEventListener("input", () => {
        this.elements.input.style.height = "auto";
        this.elements.input.style.height = Math.min(
          this.elements.input.scrollHeight,
          150
        ) + "px";
      });
    }
  },

  /**
   * Handle check submissions button click
   */
  async handleCheckSubmissions() {
    // Exit guided flow
    State.exitGuidedFlow();

    // Check if user is logged in
    if (!Auth.isLoggedIn()) {
      // Close chat window
      this.closeWindow();
      // Show login modal
      AuthUI.openModal('login');
      return;
    }

    // Fetch and display submissions
    await this.fetchAndDisplaySubmissions();
  },

  /**
   * Fetch submissions from API and display them
   */
  async fetchAndDisplaySubmissions() {
    // Show loading indicator
    this.showSubmissionsLoading();

    try {
      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.SUBMISSIONS}`,
        {
          method: "GET",
          headers: {
            ...Auth.getAuthHeaders(),
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, show login modal
          Auth.logout();
          AuthUI.openModal('login');
          this.addMessage("assistant", "Your session has expired. Please login again to view your submissions.");
          return;
        }
        throw new Error("Failed to fetch submissions");
      }

      const submissions = await response.json();
      this.displaySubmissions(submissions);
    } catch (err) {
      if (DEBUG) console.error("[Chat] Error fetching submissions:", err);
      this.showSubmissionsError(err.message || "Failed to load submissions. Please try again.");
    }
  },

  /**
   * Show loading indicator for submissions
   */
  showSubmissionsLoading() {
    // Remove any existing submissions container
    const existingContainer = document.querySelector(".submissions-container");
    if (existingContainer) {
      existingContainer.remove();
    }

    // Add loading indicator as a message
    const messageDiv = document.createElement("div");
    messageDiv.className = "message assistant";
    messageDiv.innerHTML = `
      <div class="message-bubble submissions-container">
        <div class="submissions-loading">Loading your submissions...</div>
      </div>
    `;

    this.elements.body.appendChild(messageDiv);
    this.scrollToBottom();
  },

  /**
   * Show error message for submissions
   * @param {string} message - Error message
   */
  showSubmissionsError(message) {
    // Remove any existing submissions container
    const existingContainer = document.querySelector(".submissions-container");
    if (existingContainer) {
      existingContainer.remove();
    }

    // Add error message as a message bubble
    const messageDiv = document.createElement("div");
    messageDiv.className = "message assistant";
    messageDiv.innerHTML = `
      <div class="message-bubble submissions-container submissions-error">
        ${this.escapeHtml(message)}
      </div>
    `;

    this.elements.body.appendChild(messageDiv);
    this.scrollToBottom();
  },

  /**
   * Display submissions in chat
   * @param {Array} submissions - Array of submission objects
   */
  displaySubmissions(submissions) {
    // Remove any existing submissions container
    const existingContainer = document.querySelector(".submissions-container");
    if (existingContainer) {
      existingContainer.remove();
    }

    // Create message container
    const messageDiv = document.createElement("div");
    messageDiv.className = "message assistant";
    
    let containerHtml = `
      <div class="message-bubble submissions-container">
        <div class="submissions-header">Your Submissions</div>
    `;

    if (!submissions || submissions.length === 0) {
      containerHtml += `
        <div class="submissions-empty">You haven't started any questionnaires yet.</div>
      `;
    } else {
      containerHtml += `<div class="submissions-list">`;

      submissions.forEach(submission => {
        const statusClass = submission.is_complete ? 'completed' : 'in-progress';
        const statusIcon = submission.is_complete ? '✓' : '⏳';
        const statusText = submission.is_complete ? 'Completed' : 'In Progress';
        const stepText = submission.is_complete 
          ? '' 
          : `<div class="submission-step">Step ${submission.step}</div>`;

        containerHtml += `
          <div class="submission-item">
            <div class="submission-title">${this.escapeHtml(submission.questionnaire_title)}</div>
            <div class="submission-status ${statusClass}">
              <span>${statusIcon}</span>
              <span>${statusText}</span>
            </div>
            ${stepText}
          </div>
        `;
      });

      containerHtml += `</div>`;
    }

    containerHtml += `</div>`;
    messageDiv.innerHTML = containerHtml;

    this.elements.body.appendChild(messageDiv);
    this.scrollToBottom();
  },

  /**
   * Fetch user conversations from API
   * @param {number} userId - User ID
   * @param {number} skip - Number of conversations to skip (pagination)
   * @param {number} limit - Number of conversations to fetch (pagination, default 3)
   * @returns {Promise<Array>} Array of conversation objects
   */
  async fetchUserConversations(userId, skip = 0, limit = 3) {
    const endpoint = Config.API.ENDPOINTS.USER_CONVERSATIONS.replace('{user_id}', userId);
    const url = `${Config.API.BASE_URL}${endpoint}?skip=${skip}&limit=${limit}`;

    const response = await fetch(
      url,
      {
        method: "GET",
        headers: {
          ...Auth.getAuthHeaders(),
          "Content-Type": "application/json"
        }
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        Auth.logout();
        AuthUI.openModal('login');
        throw new Error("Session expired");
      }
      throw new Error("Failed to fetch conversations");
    }

    return await response.json();
  },

  /**
   * Fetch messages for a conversation from API
   * @param {number} conversationId - Conversation ID
   * @returns {Promise<Array>} Array of message objects
   */
  async fetchConversationMessages(conversationId) {
    const endpoint = Config.API.ENDPOINTS.CONVERSATION_MESSAGES.replace('{id}', conversationId);
    const url = `${Config.API.BASE_URL}${endpoint}`;

    const response = await fetch(
      url,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch conversation messages");
    }

    const data = await response.json();
    // Handle both array response and wrapped response
    return Array.isArray(data) ? data : (data.messages || []);
  },

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  },

  /**
   * Toggle chat window visibility
   */
  async toggleWindow() {
    if (!this.elements.window) return;

    this.elements.window.classList.toggle("active");

    // Window is opening
    if (this.elements.window.classList.contains("active")) {
      // Check if we have an active conversation to redirect to
      if (State.activeConversationId) {
        // Redirect to the active conversation
        await History.loadConversation(State.activeConversationId);
      } else if (!State.greetingRendered) {
        // No active conversation and greeting not shown - show greeting
        GuidedFlow.showGreeting();
      }
    }
  },

  /**
   * Close chat window and reset to new chat
   */
  closeWindow() {
    if (!this.elements.window) return;
    this.elements.window.classList.remove("active");
    this.resetToNewChat();
  },

  /**
   * Reset chat to new conversation state
   * Clears all conversation state and shows greeting
   */
  resetToNewChat() {
    // Clear all state
    State.clear();
    
    // Clear chat display
    this.clearChat();
    
    // Reset greeting rendered flag
    State.greetingRendered = false;
    
    // Show greeting if chat window is open
    if (this.elements.window && this.elements.window.classList.contains("active")) {
      GuidedFlow.showGreeting();
    }
  },

  /**
   * Add a message to the chat
   * @param {string} role - Message role ('user' or 'assistant')
   * @param {string} text - Message text (HTML allowed)
   */
  addMessage(role, text) {
    if (!this.elements.body) return;

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.innerHTML = text || "";

    messageDiv.appendChild(bubble);
    this.elements.body.appendChild(messageDiv);
    this.scrollToBottom();
  },

  /**
   * Add thinking indicator
   */
  showThinking() {
    if (!this.elements.body) return;

    const div = document.createElement("div");
    div.className = "message assistant thinking-indicator";
    div.id = "thinking-indicator";
    div.innerHTML = `
      <div class="message-bubble">
        <div class="thinking-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    `;

    this.elements.body.appendChild(div);
    this.scrollToBottom();
  },

  /**
   * Remove thinking indicator
   */
  hideThinking() {
    const el = document.getElementById("thinking-indicator");
    if (el) el.remove();
  },

  /**
   * Scroll chat to bottom
   */
  scrollToBottom() {
    if (!this.elements.body) return;
    this.elements.body.scrollTop = this.elements.body.scrollHeight;
  },

  /**
   * Clear chat body
   */
  clearChat() {
    if (!this.elements.body) return;
    this.elements.body.innerHTML = "";
  },

  /**
   * Get input value and clear it
   * @returns {string} Input value
   */
  getInputValue() {
    if (!this.elements.input) return "";
    const value = this.elements.input.value.trim();
    this.elements.input.value = "";
    this.elements.input.style.height = "auto";
    return value;
  },

  /**
   * Send message to backend
   * @param {string} message - Message to send
   */
  async sendMessageToBackend(message) {
    this.showThinking();

    try {
      // For new conversations (activeConversationId is null), send null to let backend create
      // For loaded conversations (activeConversationId is set), use that ID
      const conversationId = State.activeConversationId || null;
      const user_id = Auth.isLoggedIn() ? Auth.getCurrentUser().id : null;

      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.CHAT}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message,
            conversation_id: conversationId ? Number(conversationId) : null,
            use_history: true,
            user_id
          })
        }
      );

      if (!response.ok) {
        throw new Error("Backend error");
      }

      const data = await response.json();
      this.hideThinking();

      // Save conversation ID if first time
      if (!State.activeConversationId && !State.conversationId) {
        State.conversationId = data.conversation_id;
        localStorage.setItem(Config.STORAGE.CONVERSATION_ID, data.conversation_id);
      } else if (State.activeConversationId) {
        State.conversationId = State.activeConversationId;
      }

      this.addMessage("assistant", data.answer);

      // Persist message
      if (State.activeConversationId) {
        State.addMessageToConversation("assistant", data.answer);
      }

      return data;
    } catch (err) {
      this.hideThinking();
      this.addMessage("assistant", "Sorry, I couldn't reach the server. Please try again.");
      throw err;
    }
  },

  /**
   * Main send message handler
   */
  async sendMessage() {
    const message = this.getInputValue();
    if (!message) return;

    // Exit guided flow
    State.exitGuidedFlow();

    // Add user message
    this.addMessage("user", message);

    // Add to conversation if active
    if (State.activeConversationId) {
      State.addMessageToConversation("user", message);
    }

    // Create new conversation if none exists (only set conversationId, not activeConversationId)
    if (!State.activeConversationId) {
      const title = this.generateTitle(message);
      State.createConversation(title);
      State.addMessageToConversation("user", message);
    }

    // Call backend
    const data = await this.sendMessageToBackend(message);
    
    // After backend creates conversation, sync activeConversationId
    if (data && data.conversation_id && !State.activeConversationId) {
      State.activeConversationId = data.conversation_id;
      localStorage.setItem(Config.STORAGE.ACTIVE_CONVERSATION_ID, data.conversation_id);
    }
  },

  /**
   * Generate title from first message
   * @param {string} message - First message
   * @returns {string} Generated title
   */
  generateTitle(message) {
    const words = message.trim().split(/\s+/);
    const title = words.slice(0, Config.TITLE.MAX_WORDS).join(" ");
    return words.length > Config.TITLE.MAX_WORDS ? title + "..." : title;
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Chat;
}

