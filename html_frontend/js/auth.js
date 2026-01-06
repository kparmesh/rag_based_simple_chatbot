/**
 * ================================================
 * TOOLBOXX FLOATING CHAT - AUTHENTICATION MODULE
 * ================================================
 */

const Auth = {
  // Auth state
  isAuthenticated: false,
  currentUser: null,
  token: null,

  /**
   * Initialize authentication state
   */
  init() {
    // Load token and user from localStorage
    this.token = localStorage.getItem(Config.STORAGE.AUTH_TOKEN);
    this.currentUser = this.loadUser();
    this.isAuthenticated = !!this.token && !!this.currentUser;
    
    if (DEBUG) console.log("[Auth] Initialized:", { isAuthenticated: this.isAuthenticated });
    
    return this.isAuthenticated;
  },

  /**
   * Load user from localStorage
   * @returns {Object|null} User object or null
   */
  loadUser() {
    try {
      const userStr = localStorage.getItem(Config.STORAGE.CURRENT_USER);
      return userStr ? JSON.parse(userStr) : null;
    } catch (e) {
      console.error("Error loading user:", e);
      return null;
    }
  },

  /**
   * Save user to localStorage
   * @param {Object} user - User object
   */
  saveUser(user) {
    try {
      localStorage.setItem(Config.STORAGE.CURRENT_USER, JSON.stringify(user));
      this.currentUser = user;
    } catch (e) {
      console.error("Error saving user:", e);
    }
  },

  /**
   * Login user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Login response
   */
  async login(email, password) {
    try {
      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.AUTH.LOGIN}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();
      
      // Save auth data
      this.token = data.access_token;
      this.currentUser = data.user;
      this.isAuthenticated = true;
      
      // Persist to localStorage
      localStorage.setItem(Config.STORAGE.AUTH_TOKEN, this.token);
      this.saveUser(data.user);

      if (DEBUG) console.log("[Auth] Login successful:", { user: data.user });

      return data;
    } catch (err) {
      console.error("[Auth] Login error:", err);
      throw err;
    }
  },

  /**
   * Register new user
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Register response
   */
  async register(email, password) {
    try {
      const response = await fetch(
        `${Config.API.BASE_URL}${Config.API.ENDPOINTS.AUTH.REGISTER}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password })
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Registration failed");
      }

      const data = await response.json();
      
      // Auto-login after registration
      this.token = data.access_token;
      this.currentUser = data.user;
      this.isAuthenticated = true;
      
      localStorage.setItem(Config.STORAGE.AUTH_TOKEN, this.token);
      this.saveUser(data.user);

      if (DEBUG) console.log("[Auth] Registration successful:", { user: data.user });

      return data;
    } catch (err) {
      console.error("[Auth] Registration error:", err);
      throw err;
    }
  },

  /**
   * Logout user
   */
  logout() {
    this.token = null;
    this.currentUser = null;
    this.isAuthenticated = false;
    
    localStorage.removeItem(Config.STORAGE.AUTH_TOKEN);
    localStorage.removeItem(Config.STORAGE.CURRENT_USER);

    if (DEBUG) console.log("[Auth] Logged out");
  },

  /**
   * Get authorization header
   * @returns {Object} Headers object with Authorization
   */
  getAuthHeaders() {
    return this.token ? { "Authorization": `Bearer ${this.token}` } : {};
  },

  /**
   * Check if user is logged in
   * @returns {boolean}
   */
  isLoggedIn() {
    return this.isAuthenticated;
  },

  /**
   * Get current user
   * @returns {Object|null}
   */
  getCurrentUser() {
    return this.currentUser;
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Auth;
}

