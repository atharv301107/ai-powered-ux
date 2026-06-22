/* ══════════════════════════════════════════════════
   MEDICARE — app.js
   Dark mode | Global Search | Notifications | Ripple
   Scroll animations | Counters | FAB | Sidebar mini
   ══════════════════════════════════════════════════ */

'use strict';

// ── Boot ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSidebar();
  initTopbarScroll();
  initSearch();
  initNotifications();
  initModals();
  initRipple();
  initScrollAnimations();
  initCounters();
  initAlerts();
  initClock();
  initToggleSwitches();
  initPageLoader();
});

// ─────────────────────────────────────────────────
// THEME (Dark Mode)
// ─────────────────────────────────────────────────
function initTheme() {
  const stored = localStorage.getItem('medicare-theme') || 'light';
  applyTheme(stored);
}
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('medicare-theme', theme);
  document.querySelectorAll('.dark-mode-toggle').forEach(btn => {
    btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    btn.title = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
  });
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}
window.toggleTheme = toggleTheme;

// ─────────────────────────────────────────────────
// SIDEBAR
// ─────────────────────────────────────────────────
function initSidebar() {
  const wrapper   = document.getElementById('app-wrapper');
  const sidebar   = document.getElementById('app-sidebar');
  const miniBtn   = document.getElementById('sidebar-mini-btn');
  const mobileBtn = document.getElementById('mobile-menu-btn');

  // Restore mini state
  if (localStorage.getItem('sidebar-mini') === 'true' && wrapper) {
    wrapper.classList.add('sidebar-mini');
  }

  // Desktop mini toggle
  miniBtn?.addEventListener('click', () => {
    wrapper?.classList.toggle('sidebar-mini');
    localStorage.setItem('sidebar-mini', wrapper?.classList.contains('sidebar-mini') ? 'true' : 'false');
  });

  // Mobile toggle
  mobileBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    sidebar?.classList.toggle('mobile-open');
  });
  document.addEventListener('click', (e) => {
    if (sidebar?.classList.contains('mobile-open') && !sidebar.contains(e.target) && e.target !== mobileBtn) {
      sidebar.classList.remove('mobile-open');
    }
  });

  // Active nav link
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) link.classList.add('active');
    else if (href === '/' && path === '/') link.classList.add('active');
  });
}

// ─────────────────────────────────────────────────
// TOPBAR SCROLL EFFECT
// ─────────────────────────────────────────────────
function initTopbarScroll() {
  const topbar = document.querySelector('.topbar');
  if (!topbar) return;
  window.addEventListener('scroll', () => {
    topbar.classList.toggle('scrolled', window.scrollY > 10);
  }, { passive: true });
}

// ─────────────────────────────────────────────────
// GLOBAL SEARCH
// ─────────────────────────────────────────────────
const SEARCH_LINKS = [
  { icon:'🏠', title:'Hub Dashboard',    sub:'Main overview',          url:'/home' },
  { icon:'📊', title:'Admin Dashboard',  sub:'Analytics & management', url:'/admin' },
  { icon:'👥', title:'User Management',  sub:'Add, edit, delete users',url:'/admin/users' },
  { icon:'📅', title:'Appointments',     sub:'Manage all appointments',url:'/admin/appointments' },
  { icon:'📈', title:'Health Stats',     sub:'Healthcare statistics',  url:'/admin/health-stats' },
  { icon:'🩺', title:'Patient Portal',   sub:'Patient dashboard',      url:'/patient' },
  { icon:'💊', title:'Reminders',        sub:'Medicine reminders',     url:'/patient/reminders' },
  { icon:'👨‍⚕️', title:'Doctor Portal',    sub:'Doctor dashboard',       url:'/doctor' },
  { icon:'🤖', title:'AI Chatbot',       sub:'Healthcare assistant',   url:'/chatbot' },
  { icon:'📷', title:'Prescription OCR', sub:'Scan prescriptions',     url:'/ocr' },
  { icon:'🔮', title:'Health Analytics', sub:'Risk prediction',        url:'/analytics' },
  { icon:'👤', title:'My Profile',       sub:'Account settings',       url:'/profile' },
];

function initSearch() {
  const overlay  = document.getElementById('search-overlay');
  const input    = document.getElementById('global-search-input');
  const results  = document.getElementById('search-results');
  const triggers = document.querySelectorAll('[data-search-open]');

  if (!overlay || !input) return;

  // Open
  triggers.forEach(t => t.addEventListener('click', openSearch));
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
    if (e.key === 'Escape') closeSearch();
  });
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeSearch(); });
  document.querySelector('.search-close-key')?.addEventListener('click', closeSearch);

  // Filter
  input.addEventListener('input', () => renderResults(input.value.trim()));

  function openSearch() {
    overlay.classList.add('open');
    input.value = '';
    renderResults('');
    setTimeout(() => input.focus(), 50);
  }
  function closeSearch() { overlay.classList.remove('open'); }

  function renderResults(q) {
    const filtered = q
      ? SEARCH_LINKS.filter(l => l.title.toLowerCase().includes(q.toLowerCase()) || l.sub.toLowerCase().includes(q.toLowerCase()))
      : SEARCH_LINKS;

    if (!filtered.length) {
      results.innerHTML = `<div class="search-empty">No results for "<strong>${q}</strong>"</div>`;
      return;
    }
    results.innerHTML = filtered.map(l => `
      <a href="${l.url}" class="search-result-item" style="text-decoration:none;">
        <span class="search-result-icon">${l.icon}</span>
        <div>
          <div class="search-result-title">${l.title}</div>
          <div class="search-result-sub">${l.sub}</div>
        </div>
      </a>`).join('');
  }
}
window.openSearch  = () => document.getElementById('search-overlay')?.classList.add('open');
window.closeSearch = () => document.getElementById('search-overlay')?.classList.remove('open');

// ─────────────────────────────────────────────────
// NOTIFICATIONS
// ─────────────────────────────────────────────────
function initNotifications() {
  const panel   = document.getElementById('notif-panel');
  const openBtn = document.getElementById('notif-btn');
  const closeBtn= document.getElementById('notif-close');

  openBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    panel?.classList.toggle('open');
  });
  closeBtn?.addEventListener('click', () => panel?.classList.remove('open'));
  document.addEventListener('click', (e) => {
    if (panel?.classList.contains('open') && !panel.contains(e.target) && e.target !== openBtn) {
      panel.classList.remove('open');
    }
  });
}

// ─────────────────────────────────────────────────
// MODALS
// ─────────────────────────────────────────────────
function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => openModal(btn.dataset.modalOpen));
  });
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const overlay = btn.closest('.modal-overlay');
      if (overlay) overlay.classList.remove('open');
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(o => {
    o.addEventListener('click', (e) => { if (e.target === o) o.classList.remove('open'); });
  });
}
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
window.openModal  = openModal;
window.closeModal = closeModal;

// ─────────────────────────────────────────────────
// RIPPLE EFFECTS
// ─────────────────────────────────────────────────
function initRipple() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;
    const rect   = btn.getBoundingClientRect();
    const size   = Math.max(rect.width, rect.height) * 2;
    const x      = e.clientX - rect.left - size / 2;
    const y      = e.clientY - rect.top  - size / 2;
    const ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    Object.assign(ripple.style, { width: size+'px', height: size+'px', left: x+'px', top: y+'px' });
    btn.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  });
}

// ─────────────────────────────────────────────────
// SCROLL ANIMATIONS
// ─────────────────────────────────────────────────
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => observer.observe(el));
}

// ─────────────────────────────────────────────────
// COUNTER ANIMATIONS
// ─────────────────────────────────────────────────
function initCounters() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('[data-count]').forEach(el => observer.observe(el));
}
function animateCount(el) {
  const target   = parseInt(el.dataset.count || el.textContent) || 0;
  const suffix   = el.dataset.suffix || '';
  const duration = 1200;
  let start      = null;
  const easeOut  = t => 1 - Math.pow(1 - t, 3);
  const step     = (ts) => {
    if (!start) start = ts;
    const p = Math.min((ts - start) / duration, 1);
    el.textContent = Math.floor(easeOut(p) * target) + suffix;
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = target + suffix;
  };
  requestAnimationFrame(step);
}
window.animateCount = animateCount;

// ─────────────────────────────────────────────────
// ALERTS
// ─────────────────────────────────────────────────
function initAlerts() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const el = btn.closest('.alert');
      el.style.transition = 'all .3s'; el.style.opacity = '0'; el.style.transform = 'translateY(-8px)';
      setTimeout(() => el?.remove(), 300);
    });
  });
  document.querySelectorAll('.alert').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'all .4s'; el.style.opacity = '0'; el.style.transform = 'translateY(-8px)';
      setTimeout(() => el?.remove(), 400);
    }, 4500);
  });
}

// ─────────────────────────────────────────────────
// LIVE CLOCK
// ─────────────────────────────────────────────────
function initClock() {
  const el = document.getElementById('live-clock');
  if (!el) return;
  const tick = () => el.textContent = new Date().toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit', hour12:true });
  tick();
  setInterval(tick, 1000);
}

// ─────────────────────────────────────────────────
// TOGGLE SWITCHES (reminders)
// ─────────────────────────────────────────────────
function initToggleSwitches() {
  document.querySelectorAll('.reminder-toggle').forEach(input => {
    input.addEventListener('change', async function() {
      const id = this.dataset.id;
      const active = this.checked;
      try {
        const res  = await fetch(`/api/reminders/${id}/toggle`, { method:'POST' });
        const data = await res.json();
        if (data.success) showToast(active ? 'Reminder activated 🔔' : 'Reminder paused ⏸️', active ? 'success' : 'info');
      } catch { showToast('Connection error', 'error'); this.checked = !active; }
    });
  });
}

// ─────────────────────────────────────────────────
// PAGE LOADER
// ─────────────────────────────────────────────────
function initPageLoader() {
  const loader = document.getElementById('page-loader');
  if (!loader) return;
  window.addEventListener('load', () => {
    setTimeout(() => { loader.classList.add('hidden'); setTimeout(() => loader?.remove(), 500); }, 400);
  });
}

// ─────────────────────────────────────────────────
// TOAST NOTIFICATIONS
// ─────────────────────────────────────────────────
function showToast(msg, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = Object.assign(document.createElement('div'), { className:'toast-container' });
    document.body.appendChild(container);
  }
  const icons = { success:'✅', error:'❌', info:'ℹ️', warning:'⚠️' };
  const toast  = Object.assign(document.createElement('div'), { className:`toast ${type}` });
  toast.innerHTML = `<span>${icons[type] || '✅'}</span><span>${msg}</span>`;
  container.appendChild(toast);
  toast.addEventListener('click', () => toast.remove());
  setTimeout(() => {
    toast.style.transition = 'all .35s'; toast.style.opacity = '0'; toast.style.transform = 'translateY(10px) scale(.95)';
    setTimeout(() => toast?.remove(), 350);
  }, 3200);
}
window.showToast = showToast;

// ─────────────────────────────────────────────────
// TABLE SEARCH FILTER
// ─────────────────────────────────────────────────
function filterTableRows(inputId, tableId) {
  const q    = document.getElementById(inputId)?.value.toLowerCase() || '';
  const rows = document.querySelectorAll(`#${tableId} tbody tr`);
  rows.forEach(row => { row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none'; });
}
window.filterTableRows = filterTableRows;

// ─────────────────────────────────────────────────
// APPOINTMENT BOOKING
// ─────────────────────────────────────────────────
function initAppointmentForm() {
  const form      = document.getElementById('appt-form');
  const doctorSel = form?.querySelector('#doctor-select');
  const specInput = form?.querySelector('#specialty-input');
  const dateInput = form?.querySelector('#appt-date');

  if (dateInput) dateInput.min = new Date().toISOString().split('T')[0];

  const specs = {
    'Dr. Sneha Patil':'Cardiology', 'Dr. Ravi Desai':'General Medicine',
    'Dr. Meena Joshi':'Dermatology', 'Dr. Amit Shah':'Orthopedics',
  };
  doctorSel?.addEventListener('change', () => { specInput.value = specs[doctorSel.value] || ''; });

  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.textContent = 'Booking…'; btn.disabled = true;
    try {
      const res  = await fetch('/api/appointments', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          doctor:    doctorSel?.value,
          specialty: specInput?.value,
          date:      dateInput?.value,
          time:      form.querySelector('#appt-time')?.value,
        }),
      });
      if ((await res.json()).success) {
        showToast('Appointment booked! 🗓️');
        closeModal('appt-modal');
        form.reset();
        setTimeout(() => location.reload(), 1400);
      }
    } catch { showToast('Something went wrong.', 'error'); }
    finally { btn.textContent = 'Book Appointment'; btn.disabled = false; }
  });
}
window.initAppointmentForm = initAppointmentForm;

// ─────────────────────────────────────────────────
// REMINDER FORM
// ─────────────────────────────────────────────────
function initReminderForm() {
  const form = document.getElementById('reminder-form');
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.textContent = 'Saving…'; btn.disabled = true;
    try {
      const res = await fetch('/api/reminders', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({
          medicine:  form.querySelector('#medicine-name')?.value,
          time:      form.querySelector('#reminder-time')?.value,
          frequency: form.querySelector('#reminder-freq')?.value,
        }),
      });
      if ((await res.json()).success) {
        showToast('Reminder added! 💊');
        closeModal('reminder-modal');
        form.reset();
        setTimeout(() => location.reload(), 1400);
      }
    } catch { showToast('Something went wrong.', 'error'); }
    finally { btn.textContent = 'Add Reminder'; btn.disabled = false; }
  });
}
window.initReminderForm = initReminderForm;

// ─────────────────────────────────────────────────
// DOCTOR: APPOINTMENT STATUS
// ─────────────────────────────────────────────────
async function updateApptStatus(id, status, btn) {
  try {
    const res  = await fetch(`/api/appointments/${id}/status`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ status }),
    });
    if ((await res.json()).success) {
      showToast(`Appointment ${status.toLowerCase()}!`, status==='Confirmed' ? 'success' : 'info');
      const row  = btn?.closest('tr');
      const cell = row?.querySelector('.status-cell');
      if (cell) cell.innerHTML = `<span class="status-badge status-${status.toLowerCase()}">${status}</span>`;
      row?.querySelectorAll('.action-btn').forEach(b => b.closest('div')?.remove());
    }
  } catch { showToast('Error updating status', 'error'); }
}
window.updateApptStatus = updateApptStatus;

// ─────────────────────────────────────────────────
// HEALTH RING ANIMATION
// ─────────────────────────────────────────────────
function animateRing(svgId, score, color) {
  const circle = document.querySelector(`#${svgId} .ring-progress`);
  if (!circle) return;
  const radius = circle.r.baseVal.value;
  const circ   = 2 * Math.PI * radius;
  circle.style.strokeDasharray  = circ;
  circle.style.strokeDashoffset = circ;
  circle.style.stroke = color;
  setTimeout(() => {
    circle.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(.4,0,.2,1)';
    circle.style.strokeDashoffset = circ - (score / 100) * circ;
  }, 200);
}
window.animateRing = animateRing;
