/**
 * News Portal - Frontend JavaScript
 * Handles fetching posts from API and rendering them dynamically
 */

// Configuration
const API_URL = 'http://localhost:5000/api/posts';
const REFRESH_INTERVAL = 30000; // 30 seconds
let refreshTimer = null;

// DOM Elements
const postsContainer = document.getElementById('posts-container');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const retryButton = document.getElementById('retry-button');
const emptyState = document.getElementById('empty-state');
const postsInfo = document.getElementById('posts-info');
const postsCount = document.getElementById('posts-count');
const lastUpdated = document.getElementById('last-updated');

/**
 * Initialize the application
 */
function init() {
    console.log('Initializing News Portal...');
    fetchPosts();
    setupEventListeners();
    startAutoRefresh();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    retryButton.addEventListener('click', () => {
        hideError();
        fetchPosts();
    });
}

/**
 * Fetch posts from the API
 */
async function fetchPosts() {
    try {
        showLoading();
        hideError();
        hideEmptyState();
        hidePostsInfo();

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
            renderPosts(result.data);
            updatePostsInfo(result.count || result.data.length);
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error fetching posts:', error);
        showError(`Error al cargar las noticias: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Render posts to the DOM
 * @param {Array} posts - Array of post objects
 */
function renderPosts(posts) {
    // Clear existing posts
    postsContainer.innerHTML = '';

    if (!posts || posts.length === 0) {
        showEmptyState();
        return;
    }

    // Create and append post cards
    posts.forEach(post => {
        const postCard = createPostCard(post);
        postsContainer.appendChild(postCard);
    });
}

/**
 * Create a post card element
 * @param {Object} post - Post data
 * @returns {HTMLElement} Post card element
 */
function createPostCard(post) {
    const card = document.createElement('article');
    card.className = 'post-card';
    card.setAttribute('data-post-id', post.id);

    // Image section
    const imageContainer = document.createElement('div');
    imageContainer.className = 'post-image-container';

    if (post.image_url) {
        const img = document.createElement('img');
        img.className = 'post-image';
        img.src = post.image_url;
        img.alt = post.title;
        img.onerror = () => {
            // If image fails to load, show placeholder
            imageContainer.innerHTML = '<div class="post-image-placeholder">📰</div>';
        };
        imageContainer.appendChild(img);
    } else {
        imageContainer.innerHTML = '<div class="post-image-placeholder">📰</div>';
    }

    // Content section
    const content = document.createElement('div');
    content.className = 'post-content';

    // Title
    const title = document.createElement('h2');
    title.className = 'post-title';
    title.textContent = post.title;

    // Summary
    const summary = document.createElement('p');
    summary.className = 'post-summary';
    summary.textContent = post.summary;

    // Meta information (provider, type)
    const meta = document.createElement('div');
    meta.className = 'post-meta';

    if (post.provider) {
        const providerBadge = document.createElement('span');
        providerBadge.className = 'post-badge provider';
        providerBadge.textContent = post.provider;
        meta.appendChild(providerBadge);
    }

    if (post.type) {
        const typeBadge = document.createElement('span');
        typeBadge.className = 'post-badge type';
        typeBadge.textContent = post.type;
        meta.appendChild(typeBadge);
    }

    // Date
    const date = document.createElement('div');
    date.className = 'post-date';
    date.textContent = `📅 ${formatDate(post.release_date)}`;

    // Link to source
    const link = document.createElement('a');
    link.className = 'post-link';
    link.href = post.source_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Leer artículo completo →';

    // Assemble the card
    content.appendChild(title);
    content.appendChild(summary);
    if (meta.children.length > 0) {
        content.appendChild(meta);
    }
    content.appendChild(date);
    content.appendChild(link);

    card.appendChild(imageContainer);
    card.appendChild(content);

    return card;
}

/**
 * Format date string to readable format
 * @param {string} dateString - Date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    try {
        const date = new Date(dateString);

        // Check if date is valid
        if (isNaN(date.getTime())) {
            return dateString; // Return original if invalid
        }

        // Format options
        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };

        return date.toLocaleDateString('es-ES', options);
    } catch (error) {
        return dateString;
    }
}

/**
 * Update posts info display
 * @param {number} count - Number of posts
 */
function updatePostsInfo(count) {
    postsCount.textContent = count;
    lastUpdated.textContent = new Date().toLocaleTimeString('es-ES');
    showPostsInfo();
}

/**
 * Start automatic refresh
 */
function startAutoRefresh() {
    // Clear existing timer if any
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    // Set up new timer
    refreshTimer = setInterval(() => {
        console.log('Auto-refreshing posts...');
        fetchPosts();
    }, REFRESH_INTERVAL);

    console.log(`Auto-refresh enabled (every ${REFRESH_INTERVAL / 1000} seconds)`);
}

/**
 * Stop automatic refresh
 */
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
        console.log('Auto-refresh disabled');
    }
}

// ============================================
// UI State Management Functions
// ============================================

function showLoading() {
    loadingElement.classList.remove('hidden');
}

function hideLoading() {
    loadingElement.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorElement.classList.remove('hidden');
    stopAutoRefresh();
}

function hideError() {
    errorElement.classList.add('hidden');
    startAutoRefresh();
}

function showEmptyState() {
    emptyState.classList.remove('hidden');
}

function hideEmptyState() {
    emptyState.classList.add('hidden');
}

function showPostsInfo() {
    postsInfo.classList.remove('hidden');
}

function hidePostsInfo() {
    postsInfo.classList.add('hidden');
}

// ============================================
// Event Listeners for Page Lifecycle
// ============================================

// Stop refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        fetchPosts();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

// ============================================
// Initialize Application
// ============================================

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export functions for testing (optional)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        fetchPosts,
        renderPosts,
        formatDate
    };
}
