/**
 * News Portal - Frontend JavaScript (SPA Version)
 * Renders the public news page
 */

// Configuration
const NEWS_API_URL = 'http://localhost:5000/api/posts';
const NEWS_REFRESH_INTERVAL = 30000; // 30 seconds
let newsRefreshTimer = null;

/**
 * Render the news page (called by router)
 */
async function renderNewsPage() {
    const appContainer = document.getElementById('app');

    // Create news page HTML
    appContainer.innerHTML = `
        <header class="header">
            <div class="container">
                <h1 class="logo">News Portal</h1>
                <p class="tagline">Mantente informado con las últimas noticias</p>
            </div>
        </header>

        <main class="main-content">
            <div class="container">
                <!-- Loading indicator -->
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p>Cargando noticias...</p>
                </div>

                <!-- Error message -->
                <div id="error" class="error hidden">
                    <p id="error-message"></p>
                    <button id="retry-button" class="btn-retry">Reintentar</button>
                </div>

                <!-- Posts counter -->
                <div id="posts-info" class="posts-info hidden">
                    <p>Mostrando <strong id="posts-count">0</strong> noticias</p>
                    <div class="last-updated">
                        Última actualización: <span id="last-updated"></span>
                    </div>
                </div>

                <!-- Posts grid -->
                <div id="posts-container" class="posts-grid">
                    <!-- Posts will be dynamically inserted here -->
                </div>

                <!-- Empty state -->
                <div id="empty-state" class="empty-state hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                    <h2>No hay noticias disponibles</h2>
                    <p>Aún no se han publicado noticias. Vuelve a revisar más tarde.</p>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 News Portal. Todos los derechos reservados.</p>
                <p class="footer-note">Las noticias se actualizan automáticamente cada 30 segundos</p>
            </div>
        </footer>
    `;

    // Setup event listeners
    setupNewsEventListeners();

    // Fetch and display posts
    await fetchNewsPosts();

    // Start auto-refresh
    startNewsAutoRefresh();
}

/**
 * Setup event listeners for news page
 */
function setupNewsEventListeners() {
    const retryButton = document.getElementById('retry-button');
    if (retryButton) {
        retryButton.addEventListener('click', () => {
            hideNewsError();
            fetchNewsPosts();
        });
    }
}

/**
 * Fetch posts from the API
 */
async function fetchNewsPosts() {
    try {
        showNewsLoading();
        hideNewsError();
        hideNewsEmptyState();
        hideNewsPostsInfo();

        const response = await fetch(NEWS_API_URL);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
            renderNewsPosts(result.data);
            updateNewsPostsInfo(result.count || result.data.length);
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error fetching posts:', error);
        showNewsError(`Error al cargar las noticias: ${error.message}`);
    } finally {
        hideNewsLoading();
    }
}

/**
 * Render posts to the DOM
 * @param {Array} posts - Array of post objects
 */
function renderNewsPosts(posts) {
    const postsContainer = document.getElementById('posts-container');

    if (!postsContainer) return;

    // Clear existing posts
    postsContainer.innerHTML = '';

    if (!posts || posts.length === 0) {
        showNewsEmptyState();
        return;
    }

    // Create and append post cards
    posts.forEach(post => {
        const postCard = createNewsPostCard(post);
        postsContainer.appendChild(postCard);
    });
}

/**
 * Create a post card element
 * @param {Object} post - Post data
 * @returns {HTMLElement} Post card element
 */
function createNewsPostCard(post) {
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

    // Meta information
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
    date.textContent = `📅 ${formatNewsDate(post.release_date)}`;

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
 * Format date string
 * @param {string} dateString - Date string
 * @returns {string} Formatted date
 */
function formatNewsDate(dateString) {
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return dateString;
        }

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
function updateNewsPostsInfo(count) {
    const postsCount = document.getElementById('posts-count');
    const lastUpdated = document.getElementById('last-updated');

    if (postsCount) postsCount.textContent = count;
    if (lastUpdated) lastUpdated.textContent = new Date().toLocaleTimeString('es-ES');

    showNewsPostsInfo();
}

/**
 * Start automatic refresh
 */
function startNewsAutoRefresh() {
    // Clear existing timer
    if (newsRefreshTimer) {
        clearInterval(newsRefreshTimer);
    }

    // Only auto-refresh if we're on the news page
    newsRefreshTimer = setInterval(() => {
        if (getCurrentRoute() === '/') {
            console.log('Auto-refreshing news...');
            fetchNewsPosts();
        }
    }, NEWS_REFRESH_INTERVAL);
}

/**
 * Stop automatic refresh
 */
function stopNewsAutoRefresh() {
    if (newsRefreshTimer) {
        clearInterval(newsRefreshTimer);
        newsRefreshTimer = null;
    }
}

// ============================================
// UI State Management
// ============================================

function showNewsLoading() {
    const el = document.getElementById('loading');
    if (el) el.classList.remove('hidden');
}

function hideNewsLoading() {
    const el = document.getElementById('loading');
    if (el) el.classList.add('hidden');
}

function showNewsError(message) {
    const errorEl = document.getElementById('error');
    const errorMsg = document.getElementById('error-message');
    if (errorEl) errorEl.classList.remove('hidden');
    if (errorMsg) errorMsg.textContent = message;
}

function hideNewsError() {
    const el = document.getElementById('error');
    if (el) el.classList.add('hidden');
}

function showNewsEmptyState() {
    const el = document.getElementById('empty-state');
    if (el) el.classList.remove('hidden');
}

function hideNewsEmptyState() {
    const el = document.getElementById('empty-state');
    if (el) el.classList.add('hidden');
}

function showNewsPostsInfo() {
    const el = document.getElementById('posts-info');
    if (el) el.classList.remove('hidden');
}

function hideNewsPostsInfo() {
    const el = document.getElementById('posts-info');
    if (el) el.classList.add('hidden');
}
