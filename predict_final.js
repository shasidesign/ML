/* FitAI — AI Predict Page JS */

const STYLE_ICONS = {
  Minimalist: '⬜', Streetwear: '🔥', 'Casual Chic': '👟',
  Athletic: '💪', Formal: '👔', Bohemian: '🌿', Elegant: '✨'
};

// ── Body Type selector ─────────────────────────────────────────────────────
let selectedBodyType = 'average';
document.querySelectorAll('.body-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.body-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    selectedBodyType = btn.dataset.val;
  });
});

// ── Live BMI calculator ────────────────────────────────────────────────────
function updateBMI() {
  const h = parseFloat(document.getElementById('height')?.value) || 170;
  const w = parseFloat(document.getElementById('weight')?.value) || 65;
  const bmi = w / ((h / 100) ** 2);
  const cats = [[18.5, 'Underweight'], [25, 'Normal weight'], [30, 'Overweight'], [Infinity, 'Obese']];
  const cat = cats.find(c => bmi < c[0])[1];
  const el = document.getElementById('liveBMI');
  const catEl = document.getElementById('liveBMICat');
  if (el) el.textContent = bmi.toFixed(1);
  if (catEl) catEl.textContent = cat;
}
['height', 'weight'].forEach(id => {
  document.getElementById(id)?.addEventListener('input', updateBMI);
});
updateBMI();

// ── Run Prediction ─────────────────────────────────────────────────────────
window.runPrediction = async function () {
  const btn      = document.getElementById('predictBtn');
  const btnText  = document.getElementById('predictBtnText');
  const spinner  = document.getElementById('predictSpinner');
  const placeholder = document.getElementById('resultPlaceholder');
  const content  = document.getElementById('resultContent');

  const payload = {
    height:    parseFloat(document.getElementById('height').value) || 170,
    weight:    parseFloat(document.getElementById('weight').value) || 65,
    age:       parseInt(document.getElementById('age').value)      || 25,
    gender:    document.getElementById('gender').value,
    body_type: selectedBodyType,
  };

  // Loading state
  btnText.textContent = 'Analyzing...';
  spinner.classList.remove('hidden');
  btn.disabled = true;

  try {
    const res  = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!data.success) throw new Error(data.error || 'Prediction failed');

    renderResult(data.prediction);
    if (document.getElementById('historyGrid')) loadHistory();

  } catch (err) {
    showToast('Prediction error: ' + err.message, 'error');
  } finally {
    btnText.textContent = '✦ Run AI Prediction';
    spinner.classList.add('hidden');
    btn.disabled = false;
  }
};

function renderResult(p) {
  const placeholder = document.getElementById('resultPlaceholder');
  const content     = document.getElementById('resultContent');

  placeholder.classList.add('hidden');
  content.classList.remove('hidden');

  // Style
  document.getElementById('resultStyleIcon').textContent = STYLE_ICONS[p.style] || '👗';
  document.getElementById('resultStyleName').textContent = p.style;

  // Alt styles
  const altsEl = document.getElementById('resultAlts');
  altsEl.innerHTML = (p.alt_styles || [])
    .map(s => `<span class="alt-tag">${STYLE_ICONS[s] || ''} ${s}</span>`).join('');

  // Confidence ring animation
  const circle = document.getElementById('confRingCircle');
  const confVal = document.getElementById('confValue');
  const circumference = 201;
  const offset = circumference - (p.confidence / 100) * circumference;
  circle.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)';
  setTimeout(() => { circle.style.strokeDashoffset = offset; }, 50);

  let count = 0;
  const timer = setInterval(() => {
    count = Math.min(count + 2, p.confidence);
    confVal.textContent = count + '%';
    if (count >= p.confidence) clearInterval(timer);
  }, 20);

  // Stats
  document.getElementById('resBMI').textContent     = p.bmi;
  document.getElementById('resBMICat').textContent  = p.bmi_category;
  document.getElementById('resSize').textContent    = p.size;
  document.getElementById('resSizeConf').textContent = p.size_confidence + '%';

  // Outfits
  const outfitsEl = document.getElementById('outfitsList');
  outfitsEl.innerHTML = (p.outfits || [])
    .map(o => `<div class="outfit-item">${o}</div>`).join('');

  // Color palette
  const paletteEl = document.getElementById('paletteSwatch');
  paletteEl.innerHTML = (p.color_palette || [])
    .map(c => `<div class="swatch" style="background:${c}" title="${c}"></div>`).join('');

  // Tip
  document.getElementById('resultTip').textContent = '💡 ' + (p.season_tip || '');

  // Scroll into view
  content.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ── Load History ───────────────────────────────────────────────────────────
async function loadHistory() {
  const grid = document.getElementById('historyGrid');
  if (!grid) return;

  try {
    const res  = await fetch('/api/dashboard');
    const data = await res.json();
    if (!data.success) return;

    const preds = data.data.recent_predictions || [];
    if (preds.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-2);font-size:14px">No predictions yet. Run your first one above!</p>';
      return;
    }
    grid.innerHTML = preds.map(p => {
      const r = p.result || {};
      const inputs = p.inputs || {};
      const date = p.timestamp ? new Date(p.timestamp).toLocaleDateString() : 'Recent';
      return `
        <div class="history-card">
          <div class="hc-style">${STYLE_ICONS[r.style] || '👗'} ${r.style || '—'}</div>
          <div class="hc-meta">${date} · ${inputs.gender || ''} · ${inputs.body_type || ''}</div>
          <div class="hc-tags">
            <span class="hc-tag">Size: ${r.size || '—'}</span>
            <span class="hc-tag">${r.confidence || '—'}% conf.</span>
            <span class="hc-tag">BMI ${r.bmi || '—'}</span>
          </div>
        </div>`;
    }).join('');
  } catch { /* silently fail */ }
}
loadHistory();
