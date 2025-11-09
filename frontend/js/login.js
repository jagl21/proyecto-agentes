/**
 * Login Page
 * Renders and handles the login form
 */

/**
 * Render the login page
 */
async function renderLoginPage() {
    // If already authenticated, redirect to home
    if (isAuthenticated()) {
        navigate('/');
        return;
    }

    const appContainer = document.getElementById('app');

    appContainer.innerHTML = `
        <div class="login-container">
            <div class="login-card">
                <div class="login-header">
                    <h1>🔒 Login</h1>
                    <p>Accede al panel de administración</p>
                </div>

                <form id="login-form" class="login-form">
                    <div class="form-group">
                        <label for="username">Usuario</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            required
                            autofocus
                            placeholder="Ingresa tu usuario"
                        />
                    </div>

                    <div class="form-group">
                        <label for="password">Contraseña</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            required
                            placeholder="Ingresa tu contraseña"
                        />
                    </div>

                    <div id="login-error" class="error-message" style="display: none;"></div>

                    <button type="submit" id="login-button" class="btn btn-primary">
                        Iniciar Sesión
                    </button>
                </form>

                <div class="login-footer">
                    <p>¿No tienes cuenta? Contacta al administrador</p>
                    <a href="/" data-link class="link">← Volver a noticias</a>
                </div>
            </div>
        </div>
    `;

    // Attach event listeners
    setupLoginForm();
}

/**
 * Setup login form event listeners
 */
function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    const loginButton = document.getElementById('login-button');
    const errorDiv = document.getElementById('login-error');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Get form data
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        // Validate
        if (!username || !password) {
            showLoginError('Por favor ingresa usuario y contraseña');
            return;
        }

        // Disable button and show loading
        loginButton.disabled = true;
        loginButton.textContent = 'Iniciando sesión...';
        hideLoginError();

        try {
            // Attempt login
            const result = await login(username, password);

            if (result.success) {
                // Success - show message and redirect
                showNotification(
                    '¡Bienvenido!',
                    `Sesión iniciada como ${result.user.username}`,
                    'success'
                );

                // Redirect based on role
                if (result.user.role === 'admin') {
                    navigate('/admin');
                } else {
                    navigate('/');
                }
            } else {
                // Failed - show error
                showLoginError(result.error || 'Credenciales inválidas');
                loginButton.disabled = false;
                loginButton.textContent = 'Iniciar Sesión';
            }

        } catch (error) {
            console.error('Login error:', error);
            showLoginError('Error de conexión - intenta nuevamente');
            loginButton.disabled = false;
            loginButton.textContent = 'Iniciar Sesión';
        }
    });
}

/**
 * Show login error message
 * @param {string} message - Error message
 */
function showLoginError(message) {
    const errorDiv = document.getElementById('login-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

/**
 * Hide login error message
 */
function hideLoginError() {
    const errorDiv = document.getElementById('login-error');
    errorDiv.style.display = 'none';
}
