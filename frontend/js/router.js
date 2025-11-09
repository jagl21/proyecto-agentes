/**
 * SPA Router
 * Handles client-side routing without page reloads
 */

// Route definitions
const routes = {
    '/': {
        title: 'Noticias',
        render: renderNewsPage,
        requiresAuth: false
    },
    '/login': {
        title: 'Login',
        render: renderLoginPage,
        requiresAuth: false
    },
    '/admin': {
        title: 'Admin Panel',
        render: renderAdminPage,
        requiresAuth: true,
        requiresAdmin: true
    }
};

// Current route
let currentRoute = null;

/**
 * Initialize the router
 */
function initRouter() {
    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        handleRoute(window.location.pathname);
    });

    // Intercept link clicks
    document.addEventListener('click', (e) => {
        // Find the closest anchor element
        const link = e.target.closest('[data-link]');

        if (link) {
            e.preventDefault();
            const href = link.getAttribute('href');
            navigate(href);
        }
    });

    // Load initial route
    handleRoute(window.location.pathname);
}

/**
 * Navigate to a new route
 * @param {string} path - The path to navigate to
 */
function navigate(path) {
    // Push state to browser history
    window.history.pushState({}, '', path);
    handleRoute(path);
}

/**
 * Handle a route change
 * @param {string} path - The route path
 */
async function handleRoute(path) {
    // Normalize path (remove trailing slash except for root)
    path = path === '/' ? '/' : path.replace(/\/$/, '');

    // Find matching route
    const route = routes[path];

    if (!route) {
        // Route not found - redirect to home
        navigate('/');
        return;
    }

    // Check authentication requirements
    if (route.requiresAuth) {
        if (!isAuthenticated()) {
            // Not authenticated - redirect to login
            navigate('/login');
            return;
        }

        if (route.requiresAdmin && !isAdmin()) {
            // Not admin - redirect to home with error
            showNotification('Acceso Denegado', 'No tienes permisos de administrador', 'error');
            navigate('/');
            return;
        }
    }

    // Update current route
    currentRoute = path;

    // Update page title
    document.title = `${route.title} - News Platform`;

    // Update active nav links
    updateActiveNavLinks(path);

    // Render the route
    await route.render();

    // Update navigation state (show/hide login/logout/admin buttons)
    updateNavigation();
}

/**
 * Update active state of navigation links
 * @param {string} currentPath - The current route path
 */
function updateActiveNavLinks(currentPath) {
    // Remove active class from all links
    document.querySelectorAll('[data-link]').forEach(link => {
        link.classList.remove('active');
    });

    // Add active class to current link
    document.querySelectorAll(`[data-link][href="${currentPath}"]`).forEach(link => {
        link.classList.add('active');
    });
}

/**
 * Get current route path
 * @returns {string} Current route path
 */
function getCurrentRoute() {
    return currentRoute;
}

/**
 * Check if a route is active
 * @param {string} path - Route path to check
 * @returns {boolean} True if route is active
 */
function isRouteActive(path) {
    return currentRoute === path;
}
