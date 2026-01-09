/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - AUTHENTICATION UI
 * ================================================
 */

const AuthUI = {
  /**
   * Initialize auth UI
   */
  init() {
    this.updateMainPageAuth();
  },

  /**
   * Update main page auth display
   */
  updateMainPageAuth() {
    const container = document.getElementById("main-page-auth");
    if (!container) return;

    if (Auth.isLoggedIn() && Auth.currentUser) {
      container.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
          <span style="color: #666;">Welcome, <strong>${this.escapeHtml(Auth.currentUser.email)}</strong></span>
          <button onclick="AuthUI.logout()" style="
            padding: 8px 16px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
          ">Logout</button>
        </div>
      `;
    } else {
      container.innerHTML = `
        <button onclick="AuthUI.openModal('login')" style="
          padding: 10px 20px;
          background: #4285F4;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
        ">LOG IN / SIGN UP</button>
      `;
    }
  },

  /**
   * Open login modal
   * @param {string} mode - 'login' or 'register'
   */
  openModal(mode = 'login') {
    const modal = document.getElementById("login-modal");
    if (!modal) return;

    modal.style.display = "flex";
    if (mode === 'register') {
      this.showRegister();
    } else {
      this.showLogin();
    }
  },

  /**
   * Close modal
   */
  closeModal() {
    const modal = document.getElementById("login-modal");
    if (!modal) return;

    modal.style.display = "none";
    this.clearForms();
  },

  /**
   * Show login form
   */
  showLogin() {
    document.getElementById("login-form").style.display = "block";
    document.getElementById("register-form").style.display = "none";
    document.getElementById("modal-title").textContent = "Login";
    this.clearErrors();
  },

  /**
   * Show register form
   */
  showRegister() {
    document.getElementById("login-form").style.display = "none";
    document.getElementById("register-form").style.display = "block";
    document.getElementById("modal-title").textContent = "Register";
    this.clearErrors();
  },

  /**
   * Clear form inputs
   */
  clearForms() {
    document.getElementById("login-email").value = "";
    document.getElementById("login-password").value = "";
    document.getElementById("register-email").value = "";
    document.getElementById("register-password").value = "";
    document.getElementById("register-confirm").value = "";
    this.clearErrors();
  },

  /**
   * Clear error messages
   */
  clearErrors() {
    document.getElementById("login-error").textContent = "";
    document.getElementById("register-error").textContent = "";
  },

  /**
   * Show login error
   * @param {string} message - Error message
   */
  showLoginError(message) {
    document.getElementById("login-error").textContent = message;
  },

  /**
   * Show register error
   * @param {string} message - Error message
   */
  showRegisterError(message) {
    document.getElementById("register-error").textContent = message;
  },

  /**
   * Handle login
   */
  async login() {
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    if (!email || !password) {
      this.showLoginError("Please fill in all fields");
      return;
    }

    try {
      await Auth.login(email, password);
      this.closeModal();
      this.updateMainPageAuth();
      State.user = Auth.getCurrentUser();
      if (DEBUG) console.log("[AuthUI] Login successful");
    } catch (err) {
      this.showLoginError(err.message || "Login failed. Please try again.");
    }
  },

  /**
   * Handle registration
   */
  async register() {
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;
    const confirm = document.getElementById("register-confirm").value;

    if (!email || !password || !confirm) {
      this.showRegisterError("Please fill in all fields");
      return;
    }

    if (password !== confirm) {
      this.showRegisterError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      this.showRegisterError("Password must be at least 6 characters");
      return;
    }

    try {
      await Auth.register(email, password);
      this.closeModal();
      this.updateMainPageAuth();
      State.user = Auth.getCurrentUser();
      if (DEBUG) console.log("[AuthUI] Registration successful");
    } catch (err) {
      this.showRegisterError(err.message || "Registration failed. Please try again.");
    }
  },

  /**
   * Handle logout
   */
  logout() {
    Auth.logout();
    State.user = null;
    this.updateMainPageAuth();
    if (DEBUG) console.log("[AuthUI] Logout successful");
  },

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
};

// Make AuthUI globally accessible for onclick handlers
window.AuthUI = AuthUI;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuthUI;
}

