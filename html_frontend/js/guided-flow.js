/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - GUIDED FLOW
 * ================================================
 */

const GuidedFlow = {
  /**
   * Clear all option buttons
   */
  clearOptions() {
    const options = document.querySelectorAll(".options");
    options.forEach((o) => o.remove());
  },

  /**
   * Show greeting and initial options
   */
  showGreeting() {
    if (State.greetingRendered) return;

    Chat.addMessage("ai", Config.GREETING.MESSAGE);
    this.showOptions(Config.GREETING.OPTIONS);
    State.greetingRendered = true;
  },

  /**
   * Show option buttons
   * @param {string[]} opts - Array of option labels
   */
  showOptions(opts) {
    this.clearOptions();

    if (!Chat.elements.body) return;

    const wrap = document.createElement("div");
    wrap.className = "options";

    opts.forEach((opt) => {
      const btn = document.createElement("div");
      btn.className = "option-btn";
      btn.textContent = opt;
      btn.onclick = () => this.handleOption(opt);
      wrap.appendChild(btn);
    });

    Chat.elements.body.appendChild(wrap);
    Chat.scrollToBottom();
  },

  /**
   * Handle option selection
   * @param {string} opt - Selected option
   */
  handleOption(opt) {
    this.clearOptions();
    Chat.addMessage("user", opt);

    // Root level options
    if (State.guidedStep === "root") {
      this.handleRootOption(opt);
      return;
    }

    // Legal flow options
    if (State.guidedStep === "legal") {
      this.handleLegalOption(opt);
      return;
    }

    // Will flow options
    if (State.guidedStep === "will") {
      this.handleWillOption(opt);
      return;
    }

    // LPA flow options
    if (State.guidedStep === "lpa") {
      this.handleLPAOption(opt);
      return;
    }

    // Bereavement options
    if (State.guidedStep === "bereavement") {
      this.handleBereavementOption(opt);
      return;
    }

    // Final wishes options
    if (State.guidedStep === "final") {
      this.handleFinalOption(opt);
      return;
    }
  },

  /**
   * Handle root level options
   * @param {string} opt - Selected option
   */
  handleRootOption(opt) {
    if (opt === "Legal Document Support") {
      State.guidedStep = "legal";
      this.showOptions(["Will Writing", "Living Will", "Lasting Power of Attorney (LPA)"]);
      return;
    }

    if (opt === "Bereavement Support") {
      State.guidedStep = "bereavement";
      this.showOptions([
        "A Little Help",
        "A Little More Help",
        "Lots of Help",
        "Hand It All Over",
        "Online Grief Support"
      ]);
      return;
    }

    if (opt === "Final Wishes Support") {
      State.guidedStep = "final";
      this.showOptions([
        "My Documents",
        "Personal Messages",
        "Funeral Wishes",
        "Digital Legacy",
        "Trusted People",
        "Nags"
      ]);
      return;
    }
  },

  /**
   * Handle legal document support options
   * @param {string} opt - Selected option
   */
  handleLegalOption(opt) {
    if (opt === "Will Writing") {
      State.guidedStep = "will";
      this.showOptions(["Online", "Telephone", "Video"]);
      return;
    }

    if (opt === "Living Will") {
      Chat.addMessage(
        "ai",
        "👉 <a href='https://trustinheritance.toolboxx.co.uk/living-will/5999/questionnaire/step/2' target='_blank'>Click here to start your Living Will</a>"
      );
      State.exitGuidedFlow();
      return;
    }

    if (opt === "Lasting Power of Attorney (LPA)") {
      State.guidedStep = "lpa";
      this.showOptions(["Online", "Telephone", "Video"]);
      return;
    }
  },

  /**
   * Handle will writing options
   * @param {string} opt - Selected option
   */
  handleWillOption(opt) {
    if (opt === "Online") {
      Chat.addMessage(
        "ai",
        "👉 <a href='https://trustinheritance.toolboxx.co.uk/select-will' target='_blank'>Click here to start writing your will</a>"
      );
      State.exitGuidedFlow();
      return;
    }

    // For Telephone and Video, show same link with additional info
    if (opt === "Telephone" || opt === "Video") {
      Chat.addMessage(
        "ai",
        `👉 <a href='https://trustinheritance.toolboxx.co.uk/select-will' target='_blank'>Click here to start writing your will</a><br><br>For ${opt} assistance, please call our team.`
      );
      State.exitGuidedFlow();
      return;
    }
  },

  /**
   * Handle LPA options
   * @param {string} opt - Selected option
   */
  handleLPAOption(opt) {
    if (opt === "Online") {
      Chat.addMessage(
        "ai",
        "👉 <a href='https://trustinheritance.toolboxx.co.uk/select-lpa' target='_blank'>Click here to start writing your LPA</a>"
      );
      State.exitGuidedFlow();
      return;
    }

    // For Telephone and Video, show same link with additional info
    if (opt === "Telephone" || opt === "Video") {
      Chat.addMessage(
        "ai",
        `👉 <a href='https://trustinheritance.toolboxx.co.uk/select-lpa' target='_blank'>Click here to start writing your LPA</a><br><br>For ${opt} assistance, please call our team.`
      );
      State.exitGuidedFlow();
      return;
    }
  },

  /**
   * Handle bereavement support options
   * @param {string} opt - Selected option
   */
  handleBereavementOption(opt) {
    const links = {
      "A Little Help": "https://trustinheritance.toolboxx.co.uk/holder/10-steps",
      "A Little More Help":
        "https://trustinheritance.toolboxx.co.uk/what-to-do-when-someone-dies/2808/questionnaire/step/11",
      "Lots of Help":
        "https://trustinheritance.toolboxx.co.uk/payment/executor-toolkit-plus/5175",
      "Hand It All Over":
        "https://trustinheritance.toolboxx.co.uk/estate-administration",
      "Online Grief Support":
        "https://trustinheritance.toolboxx.co.uk/grief-support"
    };

    if (links[opt]) {
      Chat.addMessage(
        "ai",
        `👉 <a href='${links[opt]}' target='_blank'>Click here to check ${opt} support</a>`
      );
      State.exitGuidedFlow();
    }
  },

  /**
   * Handle final wishes options
   * @param {string} opt - Selected option
   */
  handleFinalOption(opt) {
    const links = {
      "My Documents": "https://trustinheritance.toolboxx.co.uk/mydigifile",
      "Personal Messages":
        "https://trustinheritance.toolboxx.co.uk/payment/personal-message",
      "Funeral Wishes":
        "https://trustinheritance.toolboxx.co.uk/payment/what-to-do-when-planning-your-funeral",
      "Digital Legacy":
        "https://trustinheritance.toolboxx.co.uk/payment/digital-assets",
      "Trusted People":
        "https://trustinheritance.toolboxx.co.uk/profile#tab-trusted",
      Nags: "https://trustinheritance.toolboxx.co.uk/nags"
    };

    if (links[opt]) {
      Chat.addMessage(
        "ai",
        `👉 <a href='${links[opt]}' target='_blank'>Click here to check ${opt} support</a>`
      );
      State.exitGuidedFlow();
    }
  },

  /**
   * Reset guided flow to root
   */
  reset() {
    State.guidedStep = "root";
    State.guidedFlowActive = true;
    State.greetingRendered = false;
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GuidedFlow;
}

