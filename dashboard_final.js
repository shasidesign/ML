/* FitAI — Dashboard JS */

const STYLE_ICONS = {
  Minimalist: '⬜', Streetwear: '🔥', 'Casual Chic': '👟',
  Athletic: '💪', Formal: '👔', Bohemian: '🌿', Elegant: '✨'
};

let chartInstance = null;

// ── Load Dashboard Data ────────────────────────────────────────────────────
async function loadDashboard() {
  try {
    const res  = await fetch('/api/dashboard');
    const data = await res.json();
    if (!data.success) return;

    const d = data.data;

    // Stats cards
    animateNumber('statPredictions', d.total_predictions || 0);
    animateNumber('statFavorites',   d.total_favorites   || 0);
    animateNumber('statChats',       d.chat_messages     || 0);

    // Top style
    const topStyle = getTopStyle(d.style_distribution || {});
    const topEl = document.getElementById('statTopStyle');
    if (topEl) topEl.textContent = (STYLE_ICONS[topStyle] || '') + ' ' + (topStyle || '—');

    // Chart
    renderStyleChart(d.style_distribution || {});

    // Recent predictions
    renderPredictions(d.recent_predictions || []);

  } catch (err) {
    console.error('Dashboard error:', err);
  }
}

// ── Animated number counter ────────────────────────────────────────────────
function animateNumber(elId, target) {
  const el = document.getElementById(elId);
  if (!el) return;
  let current = 0;
  const step  = Math.ceil(target / 30);
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current;
    if (current >= target) clearInterval(timer);
  }, 40);
}

function getTopStyle(dist) {
  return Object.entries(dist).sort((a, b) => b[1] - a[1])[0]?.[0] || '—';
}

// ── Donut Chart ────────────────────────────────────────────────────────────
function renderStyleChart(distribution) {
  const canvas = document.getElementById('styleChart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (chartInstance) chartInstance.destroy();

  const labels  = Object.keys(distribution);
  const values  = Object.values(distribution);
  const colors  = ['#00d4ff','#7b2ff7','#00c864','#ff6b6b','#ffb400','#a855f7','#ec4899'];

  if (labels.length === 0) {
    canvas.parentElement.innerHTML = '<p style="color:var(--text-2);font-size:14px;text-align:center;padding:60px 0">No prediction data yet.<br>Run your first AI prediction!</p>';
    return;
  }

  chartInstance = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors.slice(0, labels.length).map(c => c + 'cc'),
        borderColor:     colors.slice(0, labels.length),
        borderWidth: 2,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'right',
          labels: {
            color: 'rgba(240,244,255,.6)',
            font: { family: 'Space Grotesk', size: 12 },
            padding: 16,
            usePointStyle: true,
          }
        },
        tooltip: {
          backgroundColor: 'rgba(8,15,30,.95)',
          borderColor: 'rgba(0,212,255,.3)',
          borderWidth: 1,
          titleColor: '#f0f4ff',
          bodyColor: 'rgba(240,244,255,.7)',
          padding: 12,
          callbacks: {
            label: ctx => ` ${ctx.label}: ${ctx.parsed} predictions`
          }
        }
      },
      animation: { animateRotate: true, duration: 1000, easing: 'easeOutQuart' }
    }
  });
}

// ── Recent Predictions List ────────────────────────────────────────────────
function renderPredictions(predictions) {
  const el = document.getElementById('predictionsList');
  if (!el) return;

  if (predictions.length === 0) {
    el.innerHTML = `
      <div style="text-align:center;padding:32px;color:var(--text-2);font-size:14px">
        No predictions yet.<br>
        <a href="/predict-page" style="color:var(--blue);font-weight:600">Run your first →</a>
      </div>`;
    return;
  }

  el.innerHTML = predictions.map(p => {
    const r = p.result || {};
    const inputs = p.inputs || {};
    return `
      <div class="pred-item">
        <span class="pred-item-style">${STYLE_ICONS[r.style] || '👗'} ${r.style || '—'}</span>
        <div class="pred-item-tags">
          <span class="pred-tag">${inputs.gender || ''}</span>
          <span class="pred-tag">${inputs.body_type || ''}</span>
          <span class="pred-tag">Size ${r.size || '—'}</span>
        </div>
        <span class="pred-item-conf">${r.confidence || '—'}%</span>
      </div>`;
  }).join('');
}

// ── Init ───────────────────────────────────────────────────────────────────
loadDashboard();
