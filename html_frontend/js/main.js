/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - MAIN INITIALIZATION
 * ================================================
 */

(function () {
  "use strict";

  /**
   * Initialize all modules
   */
  function init() {
    try {
      // Initialize modules in order
      History.init();
      Chat.init();

      if (typeof DEBUG !== 'undefined' && DEBUG) console.log("Toolboxx Floating Chat initialized successfully");
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

