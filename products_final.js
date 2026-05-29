/* FitAI — Products Page JS */

const EMOJI_MAP = {
  casual: '👕', formal: '👔', streetwear: '🧥', athletic: '🏃',
  evening: '✨', minimalist: '⬜'
};
const BADGE_CLASS = { 'AI Pick': 'badge-ai', New: 'badge-new', Bestseller: 'badge-best', Limited: 'badge-limited' };

let allProducts = [];
let filteredProducts = [];
let currentModal = null;
let currentCategory = 'all';
let favorites = new Set();

// ── Fetch products ─────────────────────────────────────────────────────────
async function fetchProducts(category = 'all') {
  const grid = document.getElementById('productsGrid');
  grid.innerHTML = `<div class="loading-products"><div class="loader-ring"></div><p>Loading AI-curated products...</p></div>`;

  try {
    const res  = await fetch(`/api/products?category=${category}`);
    const data = await res.json();
    allProducts = data.products || [];
    applyFilters();
  } catch (err) {
    grid.innerHTML = `<div class="loading-products"><p style="color:var(--text-2)">Failed to load products. Please refresh.</p></div>`;
  }
}

function applyFilters() {
  const search = document.getElementById('productSearch')?.value.toLowerCase() || '';
  const sort   = document.getElementById('sortSelect')?.value || 'default';

  filteredProducts = allProducts.filter(p =>
    p.name.toLowerCase().includes(search) ||
    p.description.toLowerCase().includes(search) ||
    p.category.toLowerCase().includes(search)
  );

  if (sort === 'price-asc')  filteredProducts.sort((a, b) => a.price - b.price);
  if (sort === 'price-desc') filteredProducts.sort((a, b) => b.price - a.price);
  if (sort === 'rating')     filteredProducts.sort((a, b) => b.rating - a.rating);

  renderProducts(filteredProducts);
}

function renderProducts(products) {
  const grid = document.getElementById('productsGrid');
  if (products.length === 0) {
    grid.innerHTML = `<div class="loading-products"><p style="color:var(--text-2)">No products found. Try a different filter.</p></div>`;
    return;
  }
  grid.innerHTML = products.map((p, i) => productCard(p, i)).join('');

  // Stagger animation
  grid.querySelectorAll('.product-card').forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    setTimeout(() => {
      card.style.transition = 'opacity .4s, transform .4s';
      card.style.opacity = '1';
      card.style.transform = 'none';
    }, i * 40);
  });
}

function productCard(p, i) {
  const isFav = favorites.has(p.id);
  const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
  const badgeCls = BADGE_CLASS[p.badge] || '';
  const aiBadge  = p.ai_recommended ? `<div class="product-badge badge-ai">✦ AI Pick</div>` : '';
  const badge    = (!p.ai_recommended && p.badge) ? `<div class="product-badge ${badgeCls}">${p.badge}</div>` : '';

  return `
    <div class="product-card" onclick="openModal(${i})">
      <div class="product-img" style="background:${p.color}22">
        ${aiBadge}${badge}
        <div class="product-img-inner">
          <span class="product-emoji">${EMOJI_MAP[p.category] || '👗'}</span>
        </div>
        <button class="fav-btn ${isFav ? 'active' : ''}"
                onclick="event.stopPropagation(); handleFav(${p.id}, this)"
                aria-label="Favorite">
          ${isFav ? '♥' : '♡'}
        </button>
      </div>
      <div class="product-info">
        <div class="product-cat">${p.category}</div>
        <div class="product-name">${p.name}</div>
        <div class="product-desc">${p.description}</div>
        <div class="product-footer">
          <span class="product-price">$${p.price}</span>
          <span class="product-rating">
            <span class="star">${stars.slice(0,5)}</span>
            ${p.rating} (${p.reviews})
          </span>
        </div>
      </div>
    </div>`;
}

// ── Modal ──────────────────────────────────────────────────────────────────
window.openModal = function (index) {
  const p = filteredProducts[index];
  if (!p) return;
  currentModal = p;

  const modal = document.getElementById('productModal');
  document.getElementById('modalVisual').style.background = p.color + '33';
  document.getElementById('modalVisual').innerHTML = `<span style="font-size:80px">${EMOJI_MAP[p.category] || '👗'}</span>`;

  const badges = [];
  if (p.ai_recommended) badges.push('<span class="product-badge badge-ai" style="position:static;display:inline-block">✦ AI Recommended</span>');
  if (p.badge && !p.ai_recommended) badges.push(`<span class="product-badge ${BADGE_CLASS[p.badge] || ''}" style="position:static;display:inline-block">${p.badge}</span>`);
  document.getElementById('modalBadges').innerHTML = badges.join('');

  document.getElementById('modalName').textContent  = p.name;
  document.getElementById('modalPrice').textContent = '$' + p.price;
  document.getElementById('modalDesc').textContent  = p.description;
  document.getElementById('modalRating').textContent = '★'.repeat(Math.round(p.rating)) + ` ${p.rating}`;
  document.getElementById('modalReviews').textContent = `(${p.reviews} reviews)`;

  const sizesEl = document.getElementById('modalSizes');
  sizesEl.innerHTML = (p.sizes || ['S','M','L','XL'])
    .map((s, i) => `<div class="size-chip ${i===1?'active':''}" onclick="selectSize(this)">${s}</div>`).join('');

  const favBtn = document.getElementById('modalFavBtn');
  favBtn.innerHTML = favorites.has(p.id) ? '♥ Favorited' : '♡ Favorite';

  modal.classList.add('open');
};

window.closeProductModal = function () {
  document.getElementById('productModal').classList.remove('open');
};
window.closeModal = function (e) {
  if (e.target === document.getElementById('productModal')) closeProductModal();
};

window.selectSize = function (el) {
  document.querySelectorAll('.size-chip').forEach(c => c.classList.remove('active'));
  el.classList.add('active');
};

window.addToCart = function () {
  showToast(`${currentModal?.name} added to cart! 🛒`, 'success');
};

window.toggleFav = async function () {
  if (!currentModal) return;
  await handleFav(currentModal.id, null);
  const favBtn = document.getElementById('modalFavBtn');
  favBtn.innerHTML = favorites.has(currentModal.id) ? '♥ Favorited' : '♡ Favorite';
};

async function handleFav(productId, btnEl) {
  try {
    const res  = await fetch('/api/favorites/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId }),
    });
    const data = await res.json();
    if (data.favorited) {
      favorites.add(productId);
      if (btnEl) { btnEl.innerHTML = '♥'; btnEl.classList.add('active'); }
      showToast('Added to favorites ♥', 'success');
    } else {
      favorites.delete(productId);
      if (btnEl) { btnEl.innerHTML = '♡'; btnEl.classList.remove('active'); }
      showToast('Removed from favorites', 'info');
    }
  } catch {
    showToast('Sign in to save favorites', 'info');
  }
}

// ── Filters & Search ───────────────────────────────────────────────────────
document.querySelectorAll('.filter-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentCategory = tab.dataset.cat;
    fetchProducts(currentCategory);
  });
});

let searchTimeout;
document.getElementById('productSearch')?.addEventListener('input', () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(applyFilters, 300);
});
document.getElementById('sortSelect')?.addEventListener('change', applyFilters);

// ── Keyboard close ─────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeProductModal();
});

// ── Init ───────────────────────────────────────────────────────────────────
fetchProducts();
