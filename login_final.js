/* FitAI — Login Page JS: Lamp Animation + Auth */

const lampPanel     = document.getElementById('lampPanel');
const lampCord      = document.getElementById('lampCord');
const lampStatus    = document.getElementById('lampStatus');
const statusText    = document.getElementById('statusText');
const statusDot     = lampStatus?.querySelector('.status-dot');
const formsContainer = document.getElementById('formsContainer');
const lampQuote     = document.getElementById('lampQuote');
const quoteOff      = lampQuote?.querySelector('.quote-off');
const quoteOn       = lampQuote?.querySelector('.quote-on');

let lampOn = false;

// ── Lamp Toggle ────────────────────────────────────────────────────────────
function toggleLamp() {
  lampOn = !lampOn;

  // Pulling animation
  lampCord.classList.add('pulling');
  setTimeout(() => lampCord.classList.remove('pulling'), 600);

  if (lampOn) {
    lampPanel.classList.add('lit');
    statusDot.className  = 'status-dot on';
    statusText.textContent = 'Lamp is on — welcome to FitAI!';
    formsContainer.classList.add('visible');
    quoteOff.classList.add('hidden');
    quoteOn.classList.remove('hidden');
  } else {
    lampPanel.classList.remove('lit');
    statusDot.className  = 'status-dot off';
    statusText.textContent = 'Lamp is off — pull cord to reveal form';
    formsContainer.classList.remove('visible');
    quoteOff.classList.remove('hidden');
    quoteOn.classList.add('hidden');
  }
}

lampCord?.addEventListener('click', toggleLamp);

// ── Tab Switch ─────────────────────────────────────────────────────────────
function switchTab(tab) {
  const loginForm    = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const loginTab     = document.getElementById('loginTab');
  const registerTab  = document.getElementById('registerTab');
  const tabSlider    = document.getElementById('tabSlider');

  if (tab === 'login') {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
    tabSlider.classList.remove('right');
  } else {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
    tabSlider.classList.add('right');
  }
}
window.switchTab = switchTab;

// ── Password Toggle ────────────────────────────────────────────────────────
window.togglePwd = function (id) {
  const input = document.getElementById(id);
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
};

// ── Login ──────────────────────────────────────────────────────────────────
window.doLogin = async function () {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl    = document.getElementById('loginError');
  const btnText  = document.getElementById('loginBtnText');
  const spinner  = document.getElementById('loginSpinner');

  errEl.classList.add('hidden');
  if (!username || !password) {
    errEl.textContent = 'Please fill in all fields.';
    errEl.classList.remove('hidden');
    return;
  }

  btnText.textContent = 'Signing in...';
  spinner.classList.remove('hidden');

  try {
    const res  = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = '/dashboard';
    } else {
      errEl.textContent = data.error || 'Invalid credentials.';
      errEl.classList.remove('hidden');
    }
  } catch {
    errEl.textContent = 'Network error. Please try again.';
    errEl.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Sign In';
    spinner.classList.add('hidden');
  }
};

// ── Register ───────────────────────────────────────────────────────────────
window.doRegister = async function () {
  const username = document.getElementById('regUsername').value.trim();
  const email    = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  const errEl    = document.getElementById('registerError');
  const btnText  = document.getElementById('regBtnText');
  const spinner  = document.getElementById('regSpinner');

  errEl.classList.add('hidden');
  if (!username || !email || !password) {
    errEl.textContent = 'Please fill in all fields.';
    errEl.classList.remove('hidden');
    return;
  }
  if (password.length < 6) {
    errEl.textContent = 'Password must be at least 6 characters.';
    errEl.classList.remove('hidden');
    return;
  }

  btnText.textContent = 'Creating account...';
  spinner.classList.remove('hidden');

  try {
    const res  = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    const data = await res.json();
    if (data.success) {
      window.location.href = '/dashboard';
    } else {
      errEl.textContent = data.error || 'Registration failed.';
      errEl.classList.remove('hidden');
    }
  } catch {
    errEl.textContent = 'Network error. Please try again.';
    errEl.classList.remove('hidden');
  } finally {
    btnText.textContent = 'Create Account';
    spinner.classList.add('hidden');
  }
};

// ── Enter key support ──────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const active = document.getElementById('loginForm');
  if (active && !active.classList.contains('hidden')) doLogin();
  else doRegister();
});

// ── Auto-open lamp on mobile (no lamp panel visible) ──────────────────────
if (window.innerWidth <= 768) {
  formsContainer?.classList.add('visible');
}
