/* ══════════════════════════════════════════════════
   MEDICARE — landing.js
   Scroll animations | Stats counters | Theme sync
   ══════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  // Theme Sync on load
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  // Navbar scroll background shift
  const nav = document.getElementById('landingNav');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  });

  // Scroll Reveal Animations
  const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target); // Trigger once
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  reveals.forEach(el => revealObserver.observe(el));

  // Hero Stats Counter Animations
  const stats = document.querySelectorAll('.hero-stat-num');
  const countObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const targetValue = parseInt(el.getAttribute('data-target'), 10);
        animateCounter(el, targetValue);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  stats.forEach(el => countObserver.observe(el));
});

// Counter Animation Logic
function animateCounter(el, target) {
  let current = 0;
  const duration = 1500; // 1.5s
  const stepTime = Math.max(Math.floor(duration / target), 15);
  const stepAmount = Math.ceil(target / (duration / stepTime));

  const timer = setInterval(() => {
    current += stepAmount;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    
    // Formatting numbers nicely
    if (target >= 10000) {
      el.textContent = (current / 1000).toFixed(0) + 'K+';
    } else if (target === 99) {
      el.textContent = current + '.9%';
    } else {
      el.textContent = current + '+';
    }
  }, stepTime);
}

// Toggle Theme Handler
window.toggleTheme = function() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  updateThemeIcon(newTheme);
};

// Update Theme Icon indicator on navbar
function updateThemeIcon(theme) {
  const toggleBtn = document.querySelector('.landing-nav .dark-mode-toggle');
  if (toggleBtn) {
    toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
  }
}
