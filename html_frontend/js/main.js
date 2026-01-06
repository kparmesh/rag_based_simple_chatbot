/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - MAIN INITIALIZATION
 * ================================================
 */

// Toggle debug logs during development. Set to `true` to enable verbose logs.
const DEBUG = false;

(function () {
  "use strict";

  /**
   * Initialize all modules
   */
  function init() {
    try {
      // Initialize modules in order
      Auth.init();
      AuthUI.init();
      History.init();
      Chat.init();

      if (DEBUG) console.log("Toolboxx Floating Chat initialized successfully");
    } catch (error) {
      console.error("Error initializing chat:", error);
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Expose global functions for backward compatibility
  window.ToolboxxChat = {
    Config: Config,
    State: State,
    Chat: Chat,
    GuidedFlow: GuidedFlow,
    History: History,

    // Convenience methods
    open: () => Chat.toggleWindow(),
    close: () => Chat.closeWindow(),
    send: (message) => Chat.sendMessageToBackend(message),
    reset: () => {
      State.clear();
      Chat.clearChat();
      GuidedFlow.reset();
    }
  };
})();

