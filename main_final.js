/* FitAI — Main JavaScript */

// ── Navbar scroll effect ───────────────────────────────────────────────────
const navbar = document.getElementById('navbar');
if (navbar) {
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
}

// ── Mobile menu toggle ─────────────────────────────────────────────────────
const navToggle = document.getElementById('navToggle');
const mobileMenu = document.getElementById('mobileMenu');
if (navToggle && mobileMenu) {
  navToggle.addEventListener('click', () => {
    mobileMenu.classList.toggle('open');
    const spans = navToggle.querySelectorAll('span');
    const open = mobileMenu.classList.contains('open');
    spans[0].style.transform = open ? 'rotate(45deg) translate(5px, 5px)' : '';
    spans[1].style.opacity   = open ? '0' : '1';
    spans[2].style.transform = open ? 'rotate(-45deg) translate(5px,-5px)' : '';
  });
  document.addEventListener('click', e => {
    if (!navToggle.contains(e.target) && !mobileMenu.contains(e.target)) {
      mobileMenu.classList.remove('open');
    }
  });
}

// ── Scroll-reveal (.fade-up) ───────────────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ── Flash messages ─────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const existing = document.querySelector('.fitai-toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'fitai-toast';
  const colors = { success: '#00c864', error: '#ff5050', info: '#00d4ff' };
  toast.style.cssText = `
    position:fixed; bottom:24px; right:24px; z-index:999;
    padding:14px 20px; border-radius:12px;
    background:rgba(8,15,30,.95); border:1px solid ${colors[type] || colors.info}44;
    color:#f0f4ff; font-size:14px; font-weight:500;
    box-shadow:0 8px 32px rgba(0,0,0,.5);
    display:flex; align-items:center; gap:10px;
    animation: slideInToast .3s ease;
    max-width:340px;
  `;
  const dot = document.createElement('span');
  dot.style.cssText = `width:8px;height:8px;border-radius:50%;background:${colors[type] || colors.info};flex-shrink:0;`;
  toast.appendChild(dot);
  toast.appendChild(document.createTextNode(msg));
  document.body.appendChild(toast);

  if (!document.querySelector('#toastStyle')) {
    const s = document.createElement('style');
    s.id = 'toastStyle';
    s.textContent = '@keyframes slideInToast{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:none}}';
    document.head.appendChild(s);
  }
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 3500);
}
window.showToast = showToast;
