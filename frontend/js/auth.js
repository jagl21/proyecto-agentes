/**
 * Authentication Module
 * Handles JWT tokens, login/logout, and user state
 */

const API_URL = 'http://localhost:5000/api';
const TOKEN_KEY = 'jwt_token';
const USER_KEY = 'current_user';

/**
 * Save JWT token to localStorage
 * @param {string} token - JWT token
 */
function saveToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get JWT token from localStorage
 * @returns {string|null} Token if exists, null otherwise
 */
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Remove JWT token from localStorage
 */
function removeToken() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}

/**
 * Save user data to localStorage
 * @param {object} user - User object
 */
function saveUser(user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
}

/**
 * Get user data from localStorage
 * @returns {object|null} User object if exists, null otherwise
 */
function getUser() {
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Parse JWT token to extract payload
 * @param {string} token - JWT token
 * @returns {object|null} Decoded payload or null if invalid
 */
function parseJWT(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));

        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

/**
 * Check if token is expired
 * @param {string} token - JWT token
 * @returns {boolean} True if expired
 */
function isTokenExpired(token) {
    const payload = parseJWT(token);

    if (!payload || !payload.exp) {
        return true;
    }

    // exp is in seconds, Date.now() is in milliseconds
    return payload.exp * 1000 < Date.now();
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if authenticated
 */
function isAuthenticated() {
    const token = getToken();

    if (!token) {
        return false;
    }

    if (isTokenExpired(token)) {
        // Token expired - clear it
        removeToken();
        return false;
    }

    return true;
}

/**
 * Check if current user is admin
 * @returns {boolean} True if admin
 */
function isAdmin() {
    const user = getUser();
    return user && user.role === 'admin';
}

/**
 * Get authorization header for API requests
 * @returns {object} Headers object with Authorization
 */
function getAuthHeaders() {
    const token = getToken();

    if (!token) {
        return {};
    }

    return {
        'Authorization': `Bearer ${token}`
    };
}

/**
 * Login user
 * @param {string} username - Username
 * @param {string} password - Password
 * @returns {Promise<object>} Result object {success, user, error}
 */
async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            // Save token and user data
            saveToken(data.token);
            saveUser(data.user);

            // Notify auth change
            notifyAuthChange();

            return { success: true, user: data.user };
        } else {
            return { success: false, error: data.error || 'Login failed' };
        }

    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error - please try again' };
    }
}

/**
 * Notify that authentication state changed
 */
function notifyAuthChange() {
    window.dispatchEvent(new Event('authchange'));
}

/**
 * Logout user
 */
function logout() {
    removeToken();

    // Notify auth change
    notifyAuthChange();

    // Redirect to home page
    navigate('/');

    // Show notification
    showNotification('Sesión Cerrada', 'Has cerrado sesión correctamente', 'success');
}

/**
 * Fetch with authentication
 * Automatically adds Authorization header
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 */
async function authFetch(url, options = {}) {
    // Add authorization header
    const headers = {
        ...options.headers,
        ...getAuthHeaders()
    };

    return fetch(url, { ...options, headers });
}

/**
 * Verify current token with backend
 * @returns {Promise<boolean>} True if token is valid
 */
async function verifyToken() {
    try {
        const response = await authFetch(`${API_URL}/auth/verify`);

        if (response.ok) {
            const data = await response.json();
            return data.success;
        }

        return false;

    } catch (error) {
        console.error('Token verification error:', error);
        return false;
    }
}
