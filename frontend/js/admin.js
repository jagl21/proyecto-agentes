/**
 * Admin Panel - JavaScript
 * Handles pending posts review, approval, rejection, and editing
 */

// Configuration
const API_URL = 'http://localhost:5000/api/pending-posts';
const REFRESH_INTERVAL = 30000; // 30 seconds
let refreshTimer = null;
let currentFilter = 'pending';
let currentActionCallback = null;

// DOM Elements
const pendingPostsContainer = document.getElementById('pending-posts-container');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error');
const errorMessage = document.getElementById('error-message');
const retryButton = document.getElementById('retry-button');
const emptyState = document.getElementById('empty-state');
const statsBar = document.getElementById('stats-bar');
const lastUpdated = document.getElementById('last-updated');

// Filter tabs
const tabButtons = document.querySelectorAll('.tab-button');
const totalPending = document.getElementById('total-pending');
const pendingCount = document.getElementById('pending-count');

// Badges
const badgePending = document.getElementById('badge-pending');
const badgeAll = document.getElementById('badge-all');
const badgeApproved = document.getElementById('badge-approved');
const badgeRejected = document.getElementById('badge-rejected');

// Edit Modal
const editModal = document.getElementById('edit-modal');
const closeModalBtn = document.getElementById('close-modal');
const cancelEditBtn = document.getElementById('cancel-edit');
const editForm = document.getElementById('edit-form');
const editPostId = document.getElementById('edit-post-id');
const editTitle = document.getElementById('edit-title');
const editSummary = document.getElementById('edit-summary');
const editProvider = document.getElementById('edit-provider');
const editType = document.getElementById('edit-type');
const editImageUrl = document.getElementById('edit-image-url');

// Confirm Modal
const confirmModal = document.getElementById('confirm-modal');
const confirmTitle = document.getElementById('confirm-title');
const confirmMessage = document.getElementById('confirm-message');
const cancelConfirmBtn = document.getElementById('cancel-confirm');
const confirmActionBtn = document.getElementById('confirm-action');

/**
 * Initialize the application
 */
function init() {
    console.log('Initializing Admin Panel...');
    fetchPendingPosts();
    setupEventListeners();
    startAutoRefresh();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Retry button
    retryButton.addEventListener('click', () => {
        hideError();
        fetchPendingPosts();
    });

    // Filter tabs
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const status = button.dataset.status;
            setActiveTab(status);
            currentFilter = status;
            fetchPendingPosts();
        });
    });

    // Edit modal
    closeModalBtn.addEventListener('click', closeEditModal);
    cancelEditBtn.addEventListener('click', closeEditModal);
    editModal.querySelector('.modal-overlay').addEventListener('click', closeEditModal);
    editForm.addEventListener('submit', handleEditSubmit);

    // Confirm modal
    cancelConfirmBtn.addEventListener('click', closeConfirmModal);
    confirmModal.querySelector('.modal-overlay').addEventListener('click', closeConfirmModal);
    confirmActionBtn.addEventListener('click', handleConfirmAction);
}

/**
 * Set active tab
 */
function setActiveTab(status) {
    tabButtons.forEach(button => {
        if (button.dataset.status === status) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

/**
 * Fetch pending posts from API
 */
async function fetchPendingPosts() {
    try {
        showLoading();
        hideError();
        hideEmptyState();

        // Build URL with status filter
        let url = API_URL;
        if (currentFilter !== 'all') {
            url += `?status=${currentFilter}`;
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
            renderPendingPosts(result.data);
            updateStats(result.data);
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error fetching pending posts:', error);
        showError(`Error al cargar los posts pendientes: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * Render pending posts to the DOM
 */
function renderPendingPosts(posts) {
    pendingPostsContainer.innerHTML = '';

    if (!posts || posts.length === 0) {
        showEmptyState();
        return;
    }

    posts.forEach(post => {
        const postCard = createPendingPostCard(post);
        pendingPostsContainer.appendChild(postCard);
    });
}

/**
 * Create a pending post card element
 */
function createPendingPostCard(post) {
    const card = document.createElement('article');
    card.className = `post-card admin-post-card status-${post.status}`;
    card.setAttribute('data-post-id', post.id);

    // Image section
    const imageContainer = document.createElement('div');
    imageContainer.className = 'post-image-container';
    imageContainer.style.position = 'relative';

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

    // Status badge
    const statusBadge = document.createElement('span');
    statusBadge.className = `post-status-badge ${post.status}`;
    statusBadge.textContent = post.status === 'pending' ? 'Pendiente' :
                              post.status === 'approved' ? 'Aprobado' : 'Rechazado';
    imageContainer.appendChild(statusBadge);

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
    date.textContent = `📅 ${formatDate(post.release_date)}`;

    // Source link
    const link = document.createElement('a');
    link.className = 'post-link';
    link.href = post.source_url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'Ver fuente original →';

    // Admin actions
    const actions = document.createElement('div');
    actions.className = 'admin-actions';

    // Edit button
    const editBtn = document.createElement('button');
    editBtn.className = 'btn-edit';
    editBtn.textContent = 'Editar';
    editBtn.onclick = () => openEditModal(post);

    // Approve button
    const approveBtn = document.createElement('button');
    approveBtn.className = 'btn-approve';
    approveBtn.textContent = 'Aprobar';
    approveBtn.onclick = () => showConfirmModal(
        'Aprobar Post',
        '¿Estás seguro de que deseas aprobar y publicar este post?',
        () => approvePost(post.id)
    );
    approveBtn.disabled = post.status === 'approved';

    // Reject button
    const rejectBtn = document.createElement('button');
    rejectBtn.className = 'btn-reject';
    rejectBtn.textContent = 'Rechazar';
    rejectBtn.onclick = () => showConfirmModal(
        'Rechazar Post',
        '¿Estás seguro de que deseas rechazar este post?',
        () => rejectPost(post.id)
    );
    rejectBtn.disabled = post.status === 'rejected';

    actions.appendChild(editBtn);
    actions.appendChild(approveBtn);
    actions.appendChild(rejectBtn);

    // Assemble card
    content.appendChild(title);
    content.appendChild(summary);
    if (meta.children.length > 0) {
        content.appendChild(meta);
    }
    content.appendChild(date);
    content.appendChild(link);

    card.appendChild(imageContainer);
    card.appendChild(content);
    card.appendChild(actions);

    return card;
}

/**
 * Update statistics
 */
async function updateStats(currentPosts) {
    try {
        // Fetch all posts to get accurate counts
        const response = await fetch(API_URL);
        const result = await response.json();

        if (result.success) {
            const allPosts = result.data;
            const pending = allPosts.filter(p => p.status === 'pending').length;
            const approved = allPosts.filter(p => p.status === 'approved').length;
            const rejected = allPosts.filter(p => p.status === 'rejected').length;

            totalPending.textContent = allPosts.length;
            pendingCount.textContent = pending;
            lastUpdated.textContent = new Date().toLocaleTimeString('es-ES');

            // Update badges
            badgePending.textContent = pending;
            badgeAll.textContent = allPosts.length;
            badgeApproved.textContent = approved;
            badgeRejected.textContent = rejected;

            showStatsBar();
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Open edit modal with post data
 */
function openEditModal(post) {
    editPostId.value = post.id;
    editTitle.value = post.title;
    editSummary.value = post.summary;
    editProvider.value = post.provider || '';
    editType.value = post.type || '';
    editImageUrl.value = post.image_url || '';

    editModal.classList.remove('hidden');
}

/**
 * Close edit modal
 */
function closeEditModal() {
    editModal.classList.add('hidden');
    editForm.reset();
}

/**
 * Handle edit form submission
 */
async function handleEditSubmit(e) {
    e.preventDefault();

    const postId = editPostId.value;
    const updateData = {
        title: editTitle.value,
        summary: editSummary.value,
        provider: editProvider.value || null,
        type: editType.value || null,
        image_url: editImageUrl.value || null
    };

    try {
        const response = await fetch(`${API_URL}/${postId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Éxito', 'Post actualizado correctamente', 'success');
            closeEditModal();
            fetchPendingPosts();
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error updating post:', error);
        showNotification('Error', `No se pudo actualizar el post: ${error.message}`, 'error');
    }
}

/**
 * Show confirmation modal
 */
function showConfirmModal(title, message, callback) {
    confirmTitle.textContent = title;
    confirmMessage.textContent = message;
    currentActionCallback = callback;
    confirmModal.classList.remove('hidden');
}

/**
 * Close confirmation modal
 */
function closeConfirmModal() {
    confirmModal.classList.add('hidden');
    currentActionCallback = null;
}

/**
 * Handle confirmed action
 */
function handleConfirmAction() {
    if (currentActionCallback) {
        currentActionCallback();
    }
    closeConfirmModal();
}

/**
 * Approve a post
 */
async function approvePost(postId) {
    try {
        const response = await fetch(`${API_URL}/${postId}/approve`, {
            method: 'PUT'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Aprobado', 'Post aprobado y publicado correctamente', 'success');
            fetchPendingPosts();
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error approving post:', error);
        showNotification('Error', `No se pudo aprobar el post: ${error.message}`, 'error');
    }
}

/**
 * Reject a post
 */
async function rejectPost(postId) {
    try {
        const response = await fetch(`${API_URL}/${postId}/reject`, {
            method: 'PUT'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Rechazado', 'Post rechazado correctamente', 'success');
            fetchPendingPosts();
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error rejecting post:', error);
        showNotification('Error', `No se pudo rechazar el post: ${error.message}`, 'error');
    }
}

/**
 * Show notification
 */
function showNotification(title, message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    const icon = document.createElement('div');
    icon.className = 'notification-icon';
    icon.textContent = type === 'success' ? '✓' : '✕';

    const content = document.createElement('div');
    content.className = 'notification-content';

    const titleEl = document.createElement('div');
    titleEl.className = 'notification-title';
    titleEl.textContent = title;

    const messageEl = document.createElement('div');
    messageEl.className = 'notification-message';
    messageEl.textContent = message;

    content.appendChild(titleEl);
    content.appendChild(messageEl);

    notification.appendChild(icon);
    notification.appendChild(content);

    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Format date string
 */
function formatDate(dateString) {
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
 * Start automatic refresh
 */
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }

    refreshTimer = setInterval(() => {
        console.log('Auto-refreshing pending posts...');
        fetchPendingPosts();
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
// UI State Management
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

function showStatsBar() {
    statsBar.classList.remove('hidden');
}

function hideStatsBar() {
    statsBar.classList.add('hidden');
}

// ============================================
// Page Lifecycle Events
// ============================================

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        fetchPendingPosts();
    }
});

window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
});

// ============================================
// Initialize Application
// ============================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
