// ============================================
//   PATIENT DASHBOARD - script.js
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initToasts();
  initModals();
  initToggleSwitches();
  initAppointmentForm();
  initReminderForm();
  highlightActiveNav();
  initClock();
});

// ---- Active Nav Highlight ----
function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
}

// ---- Live Clock ----
function initClock() {
  const el = document.getElementById('live-clock');
  if (!el) return;
  const update = () => {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  };
  update();
  setInterval(update, 1000);
}

// ---- Toast Notification ----
function initToasts() { /* Container already in HTML */ }

function showToast(msg, type = 'success') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const container = document.querySelector('.toast-container') || (() => {
    const c = document.createElement('div');
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
  })();
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<span>${icons[type] || '✅'}</span><span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateY(10px)'; toast.style.transition = 'all 0.3s'; }, 2800);
  setTimeout(() => toast.remove(), 3200);
}

// ---- Modals ----
function initModals() {
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = document.getElementById(btn.dataset.modalOpen);
      if (modal) modal.classList.add('open');
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) modal.classList.remove('open');
    });
  });
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
  });
}

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add('open');
}
function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove('open');
}

// ---- Toggle Switches (Reminders) ----
function initToggleSwitches() {
  document.querySelectorAll('.reminder-toggle').forEach(input => {
    input.addEventListener('change', async function () {
      const reminderId = this.dataset.id;
      const isActive = this.checked;
      try {
        const res = await fetch(`/api/reminders/${reminderId}/toggle`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(isActive ? 'Reminder activated 🔔' : 'Reminder paused', isActive ? 'success' : 'info');
        }
      } catch (e) {
        showToast('Connection error', 'error');
        this.checked = !isActive; // revert
      }
    });
  });
}

// ---- Appointment Booking Form ----
function initAppointmentForm() {
  const form = document.getElementById('appt-form');
  if (!form) return;

  // Doctor specialty auto-fill
  const doctorSelect = form.querySelector('#doctor-select');
  const specialtyInput = form.querySelector('#specialty-input');
  const doctorSpecialties = {
    "Dr. Sneha Kulkarni": "Cardiologist",
    "Dr. Ravi Desai": "General Physician",
    "Dr. Meena Joshi": "Dermatologist",
    "Dr. Amit Shah": "Orthopedic"
  };
  if (doctorSelect && specialtyInput) {
    doctorSelect.addEventListener('change', () => {
      specialtyInput.value = doctorSpecialties[doctorSelect.value] || '';
    });
  }

  // Min date = today
  const dateInput = form.querySelector('#appt-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.textContent = 'Booking...';
    btn.disabled = true;

    const payload = {
      doctor: form.querySelector('#doctor-select').value,
      specialty: form.querySelector('#specialty-input').value,
      date: form.querySelector('#appt-date').value,
      time: form.querySelector('#appt-time').value,
    };

    try {
      const res = await fetch('/api/appointments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast('Appointment booked successfully! 🗓️');
        closeModal('appt-modal');
        form.reset();
        setTimeout(() => location.reload(), 1200);
      }
    } catch (err) {
      showToast('Something went wrong. Try again.', 'error');
    } finally {
      btn.textContent = 'Book Appointment';
      btn.disabled = false;
    }
  });
}

// ---- Reminder Form ----
function initReminderForm() {
  const form = document.getElementById('reminder-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.textContent = 'Saving...';
    btn.disabled = true;

    const payload = {
      medicine: form.querySelector('#medicine-name').value,
      time: form.querySelector('#reminder-time').value,
      frequency: form.querySelector('#reminder-freq').value,
    };

    try {
      const res = await fetch('/api/reminders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        showToast('Medicine reminder added! 💊');
        closeModal('reminder-modal');
        form.reset();
        setTimeout(() => location.reload(), 1200);
      }
    } catch (err) {
      showToast('Something went wrong. Try again.', 'error');
    } finally {
      btn.textContent = 'Add Reminder';
      btn.disabled = false;
    }
  });
}

// ---- Animate Numbers on load ----
function animateCount(el, target, duration = 800) {
  let start = 0;
  const step = target / (duration / 16);
  const update = () => {
    start = Math.min(start + step, target);
    el.textContent = Math.floor(start);
    if (start < target) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}
document.querySelectorAll('[data-count]').forEach(el => {
  animateCount(el, parseInt(el.dataset.count));
});