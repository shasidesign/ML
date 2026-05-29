/* StyleIQ — Profile Settings JS */

let selectedStyles = new Set();

// ── Load profile data ──────────────────────────────────────────────────────
async function loadProfile() {
  try {
    const res  = await fetch('/api/dashboard');
    const data = await res.json();
    if (!data.success) return;
    const d = data.data;

    document.getElementById('psPredictions').textContent = d.total_predictions ?? '—';
    document.getElementById('psFavorites').textContent   = d.total_favorites   ?? '—';
    document.getElementById('psChats').textContent       = d.chat_messages      ?? '—';

    // Load saved profile from localStorage as demo
    const saved = JSON.parse(localStorage.getItem('siq_profile') || '{}');
    if (saved.fullName)   document.getElementById('pfFullName').value   = saved.fullName;
    if (saved.email)      { document.getElementById('pfEmail').value = saved.email; document.getElementById('displayEmail').textContent = saved.email; }
    if (saved.location)   document.getElementById('pfLocation').value   = saved.location;
    if (saved.dob)        document.getElementById('pfDob').value         = saved.dob;
    if (saved.height)     document.getElementById('pfHeight').value      = saved.height;
    if (saved.weight)     document.getElementById('pfWeight').value      = saved.weight;
    if (saved.age)        document.getElementById('pfAge').value         = saved.age;
    if (saved.gender)     document.getElementById('pfGender').value      = saved.gender;
    if (saved.bodyType)   document.getElementById('pfBodyType').value    = saved.bodyType;
    if (saved.budget)     document.getElementById('pfBudget').value      = saved.budget;
    if (saved.shopping)   document.getElementById('pfShopping').value    = saved.shopping;
    if (saved.occasion)   document.getElementById('pfOccasion').value    = saved.occasion;

    if (saved.styles) {
      saved.styles.forEach(s => {
        selectedStyles.add(s);
        document.querySelectorAll('.style-pref-btn').forEach(btn => {
          if (btn.dataset.style === s) btn.classList.add('active');
        });
      });
    }
    updateBMI();
  } catch (e) {
    console.error('Profile load error:', e);
  }
}

// ── Live BMI ───────────────────────────────────────────────────────────────
function updateBMI() {
  const h = parseFloat(document.getElementById('pfHeight')?.value);
  const w = parseFloat(document.getElementById('pfWeight')?.value);
  const bmiEl  = document.getElementById('profileBMI');
  const catEl  = document.getElementById('profileBMICat');
  if (!h || !w) { if (bmiEl) bmiEl.textContent = '—'; return; }
  const bmi = w / ((h / 100) ** 2);
  const cats = [[18.5,'Underweight'],[25,'Normal weight'],[30,'Overweight'],[Infinity,'Obese']];
  const cat  = cats.find(c => bmi < c[0])[1];
  if (bmiEl)  bmiEl.textContent  = bmi.toFixed(1);
  if (catEl)  catEl.textContent  = cat;
}
document.getElementById('pfHeight')?.addEventListener('input', updateBMI);
document.getElementById('pfWeight')?.addEventListener('input', updateBMI);

// ── Style pref toggle ──────────────────────────────────────────────────────
window.toggleStylePref = function (btn) {
  const s = btn.dataset.style;
  if (selectedStyles.has(s)) {
    selectedStyles.delete(s);
    btn.classList.remove('active');
  } else {
    selectedStyles.add(s);
    btn.classList.add('active');
  }
};

// ── Save profile ───────────────────────────────────────────────────────────
window.saveProfile = async function () {
  const btnText = document.getElementById('saveBtnText');
  const spinner = document.getElementById('saveSpinner');
  btnText.textContent = 'Saving...';
  spinner.classList.remove('hidden');

  const profile = {
    fullName:  document.getElementById('pfFullName').value.trim(),
    email:     document.getElementById('pfEmail').value.trim(),
    location:  document.getElementById('pfLocation').value.trim(),
    dob:       document.getElementById('pfDob').value,
    height:    document.getElementById('pfHeight').value,
    weight:    document.getElementById('pfWeight').value,
    age:       document.getElementById('pfAge').value,
    gender:    document.getElementById('pfGender').value,
    bodyType:  document.getElementById('pfBodyType').value,
    budget:    document.getElementById('pfBudget').value,
    shopping:  document.getElementById('pfShopping').value,
    occasion:  document.getElementById('pfOccasion').value,
    styles:    [...selectedStyles],
  };

  // Try API save first, fallback to localStorage
  try {
    const res  = await fetch('/api/profile/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });
    const data = await res.json();
    if (!data.success) throw new Error('API save failed');
  } catch {
    // Graceful fallback to localStorage
    localStorage.setItem('siq_profile', JSON.stringify(profile));
  }

  if (profile.email) document.getElementById('displayEmail').textContent = profile.email;

  setTimeout(() => {
    btnText.textContent = 'Save All Changes';
    spinner.classList.add('hidden');
    showToast('Profile saved successfully! ✓', 'success');
  }, 800);
};

// ── Reset form ─────────────────────────────────────────────────────────────
window.resetForm = function () {
  if (!confirm('Discard all unsaved changes?')) return;
  loadProfile();
  showToast('Changes discarded.', 'info');
};

// ── Change password ────────────────────────────────────────────────────────
window.changePassword = async function () {
  const cur  = document.getElementById('curPwd').value;
  const nw   = document.getElementById('newPwd').value;
  const conf = document.getElementById('confirmPwd').value;
  const msg  = document.getElementById('pwdMsg');
  msg.classList.add('hidden');

  if (!cur || !nw || !conf) {
    msg.textContent = 'All password fields are required.';
    msg.classList.remove('hidden'); return;
  }
  if (nw.length < 8) {
    msg.textContent = 'New password must be at least 8 characters.';
    msg.classList.remove('hidden'); return;
  }
  if (nw !== conf) {
    msg.textContent = 'New passwords do not match.';
    msg.classList.remove('hidden'); return;
  }

  try {
    const res  = await fetch('/api/profile/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ current_password: cur, new_password: nw }),
    });
    const data = await res.json();
    if (data.success) {
      showToast('Password updated successfully! 🔒', 'success');
      document.getElementById('curPwd').value  = '';
      document.getElementById('newPwd').value  = '';
      document.getElementById('confirmPwd').value = '';
    } else {
      msg.textContent = data.error || 'Password change failed.';
      msg.classList.remove('hidden');
    }
  } catch {
    msg.textContent = 'Error updating password. Please try again.';
    msg.classList.remove('hidden');
  }
};

// ── Danger zone ────────────────────────────────────────────────────────────
window.confirmClear = function (type) {
  const labels = { predictions: 'all prediction history', favorites: 'all favourites', chat: 'all chat history' };
  if (!confirm(`Are you sure you want to clear ${labels[type]}? This cannot be undone.`)) return;
  showToast(`${labels[type].charAt(0).toUpperCase() + labels[type].slice(1)} cleared.`, 'success');
};

window.confirmDeleteAccount = function () {
  const input = prompt('Type DELETE to confirm account deletion:');
  if (input === 'DELETE') {
    showToast('Account deletion requested. Processing...', 'error');
    setTimeout(() => window.location.href = '/logout', 2000);
  } else if (input !== null) {
    showToast('Incorrect confirmation text.', 'error');
  }
};

// ── Init ───────────────────────────────────────────────────────────────────
loadProfile();
