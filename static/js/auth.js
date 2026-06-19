// ===== AUTH HELPERS =====

const TOKEN_KEY = 'access_token';

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
function removeToken() { localStorage.removeItem(TOKEN_KEY); }

function isLoggedIn() { return !!getToken(); }

function authHeaders() {
    const t = getToken();
    return t ? { 'Authorization': `Bearer ${t}` } : {};
}

async function apiFetch(url, options = {}) {
    const headers = { 'Content-Type': 'application/json', ...authHeaders(), ...(options.headers || {}) };
    const res = await fetch(url, { ...options, headers });
    return res;
}

// ===== NAV STATE =====
function updateNav() {
    const loggedIn = isLoggedIn();
    const navLogin    = document.getElementById('navLogin');
    const navRegister = document.getElementById('navRegister');
    const navAccount  = document.getElementById('navAccount');
    const navLogout   = document.getElementById('navLogout');
    if (!navLogin) return;
    navLogin.style.display    = loggedIn ? 'none' : '';
    navRegister.style.display = loggedIn ? 'none' : '';
    navAccount.style.display  = loggedIn ? '' : 'none';
    navLogout.style.display   = loggedIn ? '' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    const logoutBtn = document.getElementById('navLogout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            removeToken();
            window.location.href = '/';
        });
    }
});

// ===== ALERT HELPER =====
function showAlert(msg, type = 'error') {
    const box = document.getElementById('alertBox');
    if (!box) return;
    box.textContent = msg;
    box.className = `alert alert-${type}`;
    box.style.display = 'block';
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert() {
    const box = document.getElementById('alertBox');
    if (box) box.style.display = 'none';
}
