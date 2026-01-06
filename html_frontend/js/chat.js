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
    this.elements.window = document.getElementById("chat-window");
    this.elements.body = document.getElementById("chat-body");
    this.elements.input = document.getElementById("chat-input");
    this.elements.sendBtn = document.getElementById("send-btn");
    this.elements.launcher = document.getElementById("chat-launcher");
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
          this.addMessage("ai", "Your session has expired. Please login again to view your submissions.");
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

    // Add loading indicator
    const container = document.createElement("div");
    container.className = "submissions-container";
    container.innerHTML = `
      <div class="submissions-loading">Loading your submissions...</div>
    `;

    this.elements.body.appendChild(container);
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

    // Add error message
    const container = document.createElement("div");
    container.className = "submissions-container";
    container.innerHTML = `
      <div class="submissions-error">${this.escapeHtml(message)}</div>
    `;

    this.elements.body.appendChild(container);
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

    const container = document.createElement("div");
    container.className = "submissions-container";

    if (!submissions || submissions.length === 0) {
      container.innerHTML = `
        <div class="submissions-header">Your Submissions</div>
        <div class="submissions-empty">You haven't started any questionnaires yet.</div>
      `;
    } else {
      let submissionsHtml = `
        <div class="submissions-header">Your Submissions</div>
        <div class="submissions-list">
      `;

      submissions.forEach(submission => {
        const statusClass = submission.is_complete ? 'completed' : 'in-progress';
        const statusIcon = submission.is_complete ? '✓' : '⏳';
        const statusText = submission.is_complete ? 'Completed' : 'In Progress';
        const stepText = submission.is_complete 
          ? '' 
          : `<span class="submission-step">Step ${submission.step}</span>`;

        submissionsHtml += `
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

      submissionsHtml += '</div>';
      container.innerHTML = submissionsHtml;
    }

    this.elements.body.appendChild(container);
    this.scrollToBottom();
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

    this.elements.window.classList.toggle("open");

    // Window is opening
    if (this.elements.window.classList.contains("open")) {
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
    this.elements.window.classList.remove("open");
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
    if (this.elements.window && this.elements.window.classList.contains("open")) {
      GuidedFlow.showGreeting();
    }
  },

  /**
   * Add a message to the chat
   * @param {string} role - Message role ('user' or 'ai')
   * @param {string} text - Message text (HTML allowed)
   */
  addMessage(role, text) {
    if (!this.elements.body) return;

    if (DEBUG) console.log(`[Chat] Adding ${role} message:`, (typeof text === 'string' ? text.substring(0, 50) : String(text)).replace(/\n/g, ' '));

    const div = document.createElement("div");
    div.className = `msg ${role}`;

    // For AI messages, apply direct styles as fallback and sanitize HTML
    if (role === "ai") {
      // Apply inline styles directly to ensure visibility
      div.style.background = "#e0e0e0";
      div.style.color = "#000000";
      div.style.display = "block";
      div.style.visibility = "visible";
      div.style.opacity = "1";

      // Create a temporary container to parse the HTML
      const temp = document.createElement("div");
      temp.innerHTML = text || "";

      // Sanitize nodes: remove dangerous tags, strip attributes, and force visible colors
      const sanitizeNode = (el) => {
        if (el.nodeType === 1) { // Element node
          const tag = el.tagName.toLowerCase();

          // Remove potentially dangerous / styling tags by replacing with their text content
          const blacklist = [
            'script', 'style', 'link', 'iframe', 'object', 'embed', 'svg', 'video', 'audio', 'form', 'input', 'button'
          ];
          if (blacklist.includes(tag)) {
            const txt = document.createTextNode(el.textContent || '');
            if (el.parentNode) el.parentNode.replaceChild(txt, el);
            return;
          }

          // Remove all attributes except safe href on anchors
          Array.from(el.attributes).forEach(attr => {
            const name = attr.name.toLowerCase();
            if (tag === 'a' && name === 'href') {
              const val = el.getAttribute('href') || '';
              // Block javascript: URIs
              if (/^\s*javascript:/i.test(val)) {
                el.removeAttribute('href');
              }
              // otherwise keep href
            } else {
              try { el.removeAttribute(attr.name); } catch (e) { /* ignore */ }
            }
          });

          // Force inline visible text colors
          try {
            el.style.setProperty('color', '#000000', 'important');
            el.style.setProperty('background', 'transparent', 'important');
          } catch (e) { /* ignore */ }

          // Recursively sanitize children (clone list because we may replace nodes)
          Array.from(el.childNodes).forEach(child => sanitizeNode(child));
        }
      };

      sanitizeNode(temp);
      div.innerHTML = temp.innerHTML;
      if (DEBUG) console.log(`[Chat] AI message sanitized and styles forced`);
    } else {
      // For user messages, use CSS classes
      div.innerHTML = text;
    }

    // Verify the div has the correct classes and computed styles
    try {
      if (DEBUG) console.log(`[Chat] Message div classes:`, div.className);
      if (DEBUG) console.log(`[Chat] Message div computed style - background:`, window.getComputedStyle(div).backgroundColor);
      if (DEBUG) console.log(`[Chat] Message div computed style - color:`, window.getComputedStyle(div).color);
    } catch (e) {
      // window might not be available in some contexts
    }

    this.elements.body.appendChild(div);
    this.scrollToBottom();
  },

  /**
   * Add thinking indicator
   */
  showThinking() {
    if (!this.elements.body) return;

    const div = document.createElement("div");
    div.className = "msg ai thinking-indicator";
    div.id = "thinking-indicator";
    div.textContent = "Thinking...";

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

      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.CHAT}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message,
            conversation_id: conversationId ? Number(conversationId) : null,
            use_history: true
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

      this.addMessage("ai", data.answer);

      // Persist message
      if (State.activeConversationId) {
        State.addMessageToConversation("ai", data.answer);
      }

      return data;
    } catch (err) {
      this.hideThinking();
      this.addMessage("ai", "⚠️ Sorry, I couldn't reach the server. Please try again.");
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
