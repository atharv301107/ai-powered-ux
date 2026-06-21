// ============================================
//   PATIENT DASHBOARD - auth.js
//   Connects with: auth.html, app.py (/api/login, /api/logout)
//   Session stored in: sessionStorage
// ============================================

const AUTH_KEY          = 'medicare_auth';
const SESSION_TIMEOUT   = 30 * 60 * 1000; // 30 minutes

// ============================================================
//  1. LOGIN  —  called from auth.html form submit
// ============================================================

async function handleLogin(e) {
  e.preventDefault();

  const username  = document.getElementById('login-username').value.trim();
  const password  = document.getElementById('login-password').value.trim();
  const errorBox  = document.getElementById('login-error');
  const btn       = document.getElementById('login-btn');

  errorBox.style.display = 'none';
  errorBox.textContent   = '';

  if (!username || !password) {
    errorBox.textContent   = '⚠️  Please enter username and password.';
    errorBox.style.display = 'block';
    return;
  }

  btn.disabled      = true;
  btn.innerHTML     = '<span class="spinner"></span> Signing in…';

  // Convert username to display name — john.doe → John Doe
  const displayName = username
    .replace(/[._-]/g, ' ')
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(' ');

  // Save directly to sessionStorage — no server needed
  const sessionData = {
    userId:    Date.now(),
    username:  username,
    name:      displayName,
    role:      'patient',
    expiresAt: Date.now() + SESSION_TIMEOUT,
  };
  sessionStorage.setItem(AUTH_KEY, JSON.stringify(sessionData));

  // Also tell Flask server (best effort — ignore errors)
  try {
    await fetch('/api/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ username, password }),
    });
  } catch (_) {}

  // Redirect to dashboard
  window.location.href = '/';
}

// ============================================================
//  2. LOGOUT  —  called from any page with data-logout button
// ============================================================

async function handleLogout() {
  try {
    await fetch('/api/logout', { method: 'POST' });
  } catch (_) { /* ignore network errors on logout */ }

  sessionStorage.removeItem(AUTH_KEY);

  if (typeof showToast === 'function') {
    showToast('Logged out successfully.', 'info');
  }

  setTimeout(() => { window.location.href = '/auth'; }, 700);
}

// ============================================================
//  3. SESSION HELPERS
// ============================================================

function getSession() {
  try {
    const raw = sessionStorage.getItem(AUTH_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (Date.now() > s.expiresAt) {
      sessionStorage.removeItem(AUTH_KEY);
      return null;
    }
    return s;
  } catch {
    return null;
  }
}

function isLoggedIn()        { return getSession() !== null; }
function getCurrentUser()    { return getSession(); }
function getCurrentName()    { return getSession()?.name   ?? 'Patient'; }
function getCurrentRole()    { return getSession()?.role   ?? null; }

function refreshSession() {
  const s = getSession();
  if (!s) return;
  s.expiresAt = Date.now() + SESSION_TIMEOUT;
  sessionStorage.setItem(AUTH_KEY, JSON.stringify(s));
}

// ============================================================
//  4. ROUTE GUARDS
// ============================================================

// Call on every PROTECTED page  (dashboard, appointments, reminders)
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/auth';
  }
}

// Call on the LOGIN page — redirect away if already logged in
function requireGuest() {
  if (isLoggedIn()) {
    window.location.href = '/';
  }
}

// ============================================================
//  5. SESSION WATCHER — auto logout after 30 min idle
// ============================================================

function initSessionWatcher() {
  // Refresh timer on any user activity
  ['click', 'keydown', 'mousemove', 'touchstart'].forEach(evt =>
    document.addEventListener(evt, refreshSession, { passive: true })
  );

  // Check every 60 seconds
  setInterval(() => {
    if (sessionStorage.getItem(AUTH_KEY) && !isLoggedIn()) {
      if (typeof showToast === 'function') {
        showToast('Session expired. Please log in again.', 'warning');
      }
      setTimeout(handleLogout, 1500);
    }
  }, 60_000);
}

// ============================================================
//  6. UI HELPERS
// ============================================================

// Fill any element with [data-auth-name] with the user's name
function injectUserName() {
  const name = getCurrentName();
  document.querySelectorAll('[data-auth-name]').forEach(el => {
    el.textContent = name.split(' ')[0]; // first name only
  });
  // Also update sidebar avatar letter
  const avatar = document.getElementById('sidebar-avatar');
  if (avatar) avatar.textContent = name.charAt(0).toUpperCase();
}

// Fill any element with [data-auth-role]
function injectUserRole() {
  const role = getCurrentRole();
  document.querySelectorAll('[data-auth-role]').forEach(el => {
    el.textContent = role ? (role.charAt(0).toUpperCase() + role.slice(1)) : '';
  });
}

// ============================================================
//  7. PASSWORD TOGGLE  —  show/hide password in auth.html
// ============================================================

function initPasswordToggle() {
  const toggleBtn = document.getElementById('toggle-password');
  const pwInput   = document.getElementById('login-password');
  if (!toggleBtn || !pwInput) return;

  toggleBtn.addEventListener('click', () => {
    const isHidden = pwInput.type === 'password';
    pwInput.type        = isHidden ? 'text' : 'password';
    toggleBtn.textContent = isHidden ? '🙈' : '👁️';
  });
}

// ============================================================
//  8. AUTO-INIT on DOM Ready
// ============================================================

document.addEventListener('DOMContentLoaded', () => {

  const path = window.location.pathname;

  // --- On LOGIN page (/auth) ---
  if (path === '/auth' || path === '/auth.html') {
    requireGuest();
    initPasswordToggle();

    const form = document.getElementById('login-form');
    if (form) form.addEventListener('submit', handleLogin);
  }

  // --- On all OTHER pages (protected) ---
  else {
    requireAuth();
    injectUserName();
    injectUserRole();
    initSessionWatcher();

    // bind logout buttons
    document.querySelectorAll('[data-logout]').forEach(btn =>
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
      })
    );
  }
});