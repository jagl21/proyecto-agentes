/**
 * Admin Panel - JavaScript (SPA Version)
 * Handles pending posts review, approval, rejection, and editing
 */

// Configuration
const ADMIN_API_URL = 'http://localhost:5000/api/pending-posts';
const ADMIN_REFRESH_INTERVAL = 30000; // 30 seconds
let adminRefreshTimer = null;
let adminCurrentFilter = 'pending';
let adminCurrentActionCallback = null;

/**
 * Render the admin page (called by router)
 */
async function renderAdminPage() {
    const appContainer = document.getElementById('app');

    // Admin page HTML
    appContainer.innerHTML = `
        <header class="header">
            <div class="container">
                <div class="header-content">
                    <div>
                        <h1 class="logo">News Portal - Admin</h1>
                        <p class="tagline">Panel de administración y revisión de contenidos</p>
                    </div>
                </div>
            </div>
        </header>

        <main class="main-content">
            <div class="container">
                <div id="admin-stats-bar" class="stats-bar hidden">
                    <div class="stat-item">
                        <span class="stat-label">Total Pendientes:</span>
                        <span class="stat-value" id="admin-total-pending">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Para Revisar:</span>
                        <span class="stat-value pending" id="admin-pending-count">0</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-label">Última actualización:</span>
                        <span class="stat-value" id="admin-last-updated"></span>
                    </div>
                </div>

                <div class="filter-tabs">
                    <button class="tab-button active" data-status="pending">
                        Pendientes <span class="badge" id="admin-badge-pending">0</span>
                    </button>
                    <button class="tab-button" data-status="all">
                        Todos <span class="badge" id="admin-badge-all">0</span>
                    </button>
                    <button class="tab-button" data-status="approved">
                        Aprobados <span class="badge" id="admin-badge-approved">0</span>
                    </button>
                    <button class="tab-button" data-status="rejected">
                        Rechazados <span class="badge" id="admin-badge-rejected">0</span>
                    </button>
                </div>

                <div id="admin-loading" class="loading">
                    <div class="spinner"></div>
                    <p>Cargando posts pendientes...</p>
                </div>

                <div id="admin-error" class="error hidden">
                    <p id="admin-error-message"></p>
                    <button id="admin-retry-button" class="btn-retry">Reintentar</button>
                </div>

                <div id="admin-pending-posts-container" class="admin-posts-grid"></div>

                <div id="admin-empty-state" class="empty-state hidden">
                    <svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <h2>No hay posts pendientes de revisión</h2>
                    <p>Todos los posts han sido procesados. Ejecuta el agente IA para generar nuevos contenidos.</p>
                </div>
            </div>
        </main>

        <!-- Modals -->
        <div id="admin-edit-modal" class="modal hidden">
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Editar Post</h2>
                    <button id="admin-close-modal" class="btn-close">×</button>
                </div>
                <form id="admin-edit-form">
                    <input type="hidden" id="admin-edit-post-id">
                    <div class="form-group">
                        <label>Título</label>
                        <input type="text" id="admin-edit-title" required>
                    </div>
                    <div class="form-group">
                        <label>Resumen</label>
                        <textarea id="admin-edit-summary" rows="4" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Proveedor</label>
                        <input type="text" id="admin-edit-provider">
                    </div>
                    <div class="form-group">
                        <label>Tipo</label>
                        <input type="text" id="admin-edit-type">
                    </div>
                    <div class="form-group">
                        <label>URL Imagen</label>
                        <input type="url" id="admin-edit-image-url">
                    </div>
                    <div class="modal-footer">
                        <button type="button" id="admin-cancel-edit" class="btn-secondary">Cancelar</button>
                        <button type="submit" class="btn-primary">Guardar Cambios</button>
                    </div>
                </form>
            </div>
        </div>

        <div id="admin-confirm-modal" class="modal hidden">
            <div class="modal-overlay"></div>
            <div class="modal-content modal-small">
                <div class="modal-header">
                    <h2 id="admin-confirm-title">Confirmar Acción</h2>
                    <button id="admin-cancel-confirm" class="btn-close">×</button>
                </div>
                <div class="modal-body">
                    <p id="admin-confirm-message"></p>
                </div>
                <div class="modal-footer">
                    <button type="button" id="admin-cancel-confirm-btn" class="btn-secondary">Cancelar</button>
                    <button type="button" id="admin-confirm-action" class="btn-primary">Confirmar</button>
                </div>
            </div>
        </div>
    `;

    // Setup event listeners
    setupAdminEventListeners();

    // Fetch posts
    await fetchAdminPendingPosts();

    // Start auto-refresh
    startAdminAutoRefresh();
}

/**
 * Setup event listeners for admin page
 */
function setupAdminEventListeners() {
    // Retry button
    const retryBtn = document.getElementById('admin-retry-button');
    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            hideAdminError();
            fetchAdminPendingPosts();
        });
    }

    // Filter tabs
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const status = button.dataset.status;
            setAdminActiveTab(status);
            adminCurrentFilter = status;
            fetchAdminPendingPosts();
        });
    });

    // Edit modal
    const closeModalBtn = document.getElementById('admin-close-modal');
    const cancelEditBtn = document.getElementById('admin-cancel-edit');
    const editForm = document.getElementById('admin-edit-form');
    const editModal = document.getElementById('admin-edit-modal');

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeAdminEditModal);
    if (cancelEditBtn) cancelEditBtn.addEventListener('click', closeAdminEditModal);
    if (editModal) {
        const overlay = editModal.querySelector('.modal-overlay');
        if (overlay) overlay.addEventListener('click', closeAdminEditModal);
    }
    if (editForm) editForm.addEventListener('submit', handleAdminEditSubmit);

    // Confirm modal
    const cancelConfirmBtns = document.querySelectorAll('#admin-cancel-confirm, #admin-cancel-confirm-btn');
    const confirmActionBtn = document.getElementById('admin-confirm-action');
    const confirmModal = document.getElementById('admin-confirm-modal');

    cancelConfirmBtns.forEach(btn => {
        if (btn) btn.addEventListener('click', closeAdminConfirmModal);
    });

    if (confirmModal) {
        const overlay = confirmModal.querySelector('.modal-overlay');
        if (overlay) overlay.addEventListener('click', closeAdminConfirmModal);
    }

    if (confirmActionBtn) confirmActionBtn.addEventListener('click', handleAdminConfirmAction);
}

/**
 * Set active tab
 */
function setAdminActiveTab(status) {
    const tabButtons = document.querySelectorAll('.tab-button');
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
async function fetchAdminPendingPosts() {
    try {
        showAdminLoading();
        hideAdminError();
        hideAdminEmptyState();

        // Build URL with status filter
        let url = ADMIN_API_URL;
        if (adminCurrentFilter !== 'all') {
            url += `?status=${adminCurrentFilter}`;
        }

        const response = await authFetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success && result.data) {
            renderAdminPendingPosts(result.data);
            updateAdminStats(result.data);
        } else {
            throw new Error('Invalid response format');
        }

    } catch (error) {
        console.error('Error fetching pending posts:', error);
        showAdminError(`Error al cargar los posts pendientes: ${error.message}`);
    } finally {
        hideAdminLoading();
    }
}

/**
 * Render pending posts to the DOM
 */
function renderAdminPendingPosts(posts) {
    const container = document.getElementById('admin-pending-posts-container');
    container.innerHTML = '';

    if (!posts || posts.length === 0) {
        showAdminEmptyState();
        return;
    }

    posts.forEach(post => {
        const postCard = createAdminPendingPostCard(post);
        container.appendChild(postCard);
    });
}

/**
 * Create a pending post card element
 */
function createAdminPendingPostCard(post) {
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
        img.onload = () => {
            console.log('[Admin] Image loaded successfully:', post.image_url);
        };
        img.onerror = () => {
            console.error('[Admin] Error loading image:', post.image_url, 'for post:', post.title);
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
    date.textContent = `📅 ${formatAdminDate(post.release_date)}`;

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
    editBtn.onclick = () => openAdminEditModal(post);

    // Approve button
    const approveBtn = document.createElement('button');
    approveBtn.className = 'btn-approve';
    approveBtn.textContent = 'Aprobar';
    approveBtn.onclick = () => showAdminConfirmModal(
        'Aprobar Post',
        '¿Estás seguro de que deseas aprobar y publicar este post?',
        () => approveAdminPost(post.id)
    );
    approveBtn.disabled = post.status === 'approved';

    // Reject button
    const rejectBtn = document.createElement('button');
    rejectBtn.className = 'btn-reject';
    rejectBtn.textContent = 'Rechazar';
    rejectBtn.onclick = () => showAdminConfirmModal(
        'Rechazar Post',
        '¿Estás seguro de que deseas rechazar este post?',
        () => rejectAdminPost(post.id)
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
async function updateAdminStats(currentPosts) {
    try {
        // Fetch all posts to get accurate counts
        const response = await authFetch(ADMIN_API_URL);
        const result = await response.json();

        if (result.success) {
            const allPosts = result.data;
            const pending = allPosts.filter(p => p.status === 'pending').length;
            const approved = allPosts.filter(p => p.status === 'approved').length;
            const rejected = allPosts.filter(p => p.status === 'rejected').length;

            document.getElementById('admin-total-pending').textContent = allPosts.length;
            document.getElementById('admin-pending-count').textContent = pending;
            document.getElementById('admin-last-updated').textContent = new Date().toLocaleTimeString('es-ES');

            // Update badges
            document.getElementById('admin-badge-pending').textContent = pending;
            document.getElementById('admin-badge-all').textContent = allPosts.length;
            document.getElementById('admin-badge-approved').textContent = approved;
            document.getElementById('admin-badge-rejected').textContent = rejected;

            showAdminStatsBar();
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Open edit modal with post data
 */
function openAdminEditModal(post) {
    document.getElementById('admin-edit-post-id').value = post.id;
    document.getElementById('admin-edit-title').value = post.title;
    document.getElementById('admin-edit-summary').value = post.summary;
    document.getElementById('admin-edit-provider').value = post.provider || '';
    document.getElementById('admin-edit-type').value = post.type || '';
    document.getElementById('admin-edit-image-url').value = post.image_url || '';

    document.getElementById('admin-edit-modal').classList.remove('hidden');
}

/**
 * Close edit modal
 */
function closeAdminEditModal() {
    const modal = document.getElementById('admin-edit-modal');
    const form = document.getElementById('admin-edit-form');
    modal.classList.add('hidden');
    form.reset();
}

/**
 * Handle edit form submission
 */
async function handleAdminEditSubmit(e) {
    e.preventDefault();

    const postId = document.getElementById('admin-edit-post-id').value;
    const updateData = {
        title: document.getElementById('admin-edit-title').value,
        summary: document.getElementById('admin-edit-summary').value,
        provider: document.getElementById('admin-edit-provider').value || null,
        type: document.getElementById('admin-edit-type').value || null,
        image_url: document.getElementById('admin-edit-image-url').value || null
    };

    try {
        const response = await authFetch(`${ADMIN_API_URL}/${postId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updateData)
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Éxito', 'Post actualizado correctamente', 'success');
            closeAdminEditModal();
            fetchAdminPendingPosts();
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
function showAdminConfirmModal(title, message, callback) {
    document.getElementById('admin-confirm-title').textContent = title;
    document.getElementById('admin-confirm-message').textContent = message;
    adminCurrentActionCallback = callback;
    document.getElementById('admin-confirm-modal').classList.remove('hidden');
}

/**
 * Close confirmation modal
 */
function closeAdminConfirmModal() {
    document.getElementById('admin-confirm-modal').classList.add('hidden');
    adminCurrentActionCallback = null;
}

/**
 * Handle confirmed action
 */
function handleAdminConfirmAction() {
    if (adminCurrentActionCallback) {
        adminCurrentActionCallback();
    }
    closeAdminConfirmModal();
}

/**
 * Approve a post
 */
async function approveAdminPost(postId) {
    try {
        const response = await authFetch(`${ADMIN_API_URL}/${postId}/approve`, {
            method: 'PUT'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Aprobado', 'Post aprobado y publicado correctamente', 'success');
            fetchAdminPendingPosts();
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
async function rejectAdminPost(postId) {
    try {
        const response = await authFetch(`${ADMIN_API_URL}/${postId}/reject`, {
            method: 'PUT'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Rechazado', 'Post rechazado correctamente', 'success');
            fetchAdminPendingPosts();
        } else {
            throw new Error(result.error || 'Error desconocido');
        }
    } catch (error) {
        console.error('Error rejecting post:', error);
        showNotification('Error', `No se pudo rechazar el post: ${error.message}`, 'error');
    }
}

/**
 * Format date string
 */
function formatAdminDate(dateString) {
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
function startAdminAutoRefresh() {
    if (adminRefreshTimer) {
        clearInterval(adminRefreshTimer);
    }

    adminRefreshTimer = setInterval(() => {
        console.log('Auto-refreshing admin pending posts...');
        fetchAdminPendingPosts();
    }, ADMIN_REFRESH_INTERVAL);

    console.log(`Admin auto-refresh enabled (every ${ADMIN_REFRESH_INTERVAL / 1000} seconds)`);
}

/**
 * Stop automatic refresh
 */
function stopAdminAutoRefresh() {
    if (adminRefreshTimer) {
        clearInterval(adminRefreshTimer);
        adminRefreshTimer = null;
        console.log('Admin auto-refresh disabled');
    }
}

// ============================================
// UI State Management
// ============================================

function showAdminLoading() {
    const el = document.getElementById('admin-loading');
    if (el) el.classList.remove('hidden');
}

function hideAdminLoading() {
    const el = document.getElementById('admin-loading');
    if (el) el.classList.add('hidden');
}

function showAdminError(message) {
    const errorEl = document.getElementById('admin-error');
    const messageEl = document.getElementById('admin-error-message');
    if (messageEl) messageEl.textContent = message;
    if (errorEl) errorEl.classList.remove('hidden');
    stopAdminAutoRefresh();
}

function hideAdminError() {
    const el = document.getElementById('admin-error');
    if (el) el.classList.add('hidden');
    startAdminAutoRefresh();
}

function showAdminEmptyState() {
    const el = document.getElementById('admin-empty-state');
    if (el) el.classList.remove('hidden');
}

function hideAdminEmptyState() {
    const el = document.getElementById('admin-empty-state');
    if (el) el.classList.add('hidden');
}

function showAdminStatsBar() {
    const el = document.getElementById('admin-stats-bar');
    if (el) el.classList.remove('hidden');
}

function hideAdminStatsBar() {
    const el = document.getElementById('admin-stats-bar');
    if (el) el.classList.add('hidden');
}
