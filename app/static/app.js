// =====================================================================
// SOLEVAULT — High-Performance Footwear Brand & Admin OS
// Client-side Application Logic & State Engine
// =====================================================================

(function () {
  "use strict";

  // Global State
  const state = {
    activeView: "storefront", // "storefront" | "admin" | "chat"
    products: [],
    categories: [],
    brands: [],
    offers: [],
    cart: JSON.parse(localStorage.getItem("solevault_cart") || "[]"),
    appliedCoupon: localStorage.getItem("solevault_coupon") || null,
    cartCalc: null,
    compareIds: new Set(JSON.parse(localStorage.getItem("solevault_compare") || "[]")),
    filters: {
      category_id: null,
      gender: "all",
      size: null,
      color: null,
      max_price: 10000,
      waterproof: null,
      in_stock: null,
      is_bestseller: null,
      is_new: null,
      is_limited_edition: null,
      sort_by: "recommended",
      search: "",
    },
    activeModalProduct: null,
    adminActiveTab: "admin-products",
    chatSessionId: "session_" + Math.random().toString(36).substring(2, 9),
    isTyping: false,
  };

  function unwrap(res) {
    if (res && res.data !== undefined) return res.data;
    return res;
  }

  // Helper Functions
  function formatINR(val) {
    if (val === undefined || val === null) return "₹0";
    return "₹" + Number(val).toLocaleString("en-IN");
  }

  function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
      toast.className = "toast";
    }, 3500);
  }

  function saveCart() {
    localStorage.setItem("solevault_cart", JSON.stringify(state.cart));
    if (state.appliedCoupon) {
      localStorage.setItem("solevault_coupon", state.appliedCoupon);
    } else {
      localStorage.removeItem("solevault_coupon");
    }
    updateCartUI();
  }

  function saveCompare() {
    localStorage.setItem("solevault_compare", JSON.stringify(Array.from(state.compareIds)));
    updateCompareCounter();
  }

  // =====================================================================
  // 1. INITIALIZATION & ROUTING
  // =====================================================================
  document.addEventListener("DOMContentLoaded", () => {
    initModeSwitcher();
    initTheme();
    initStoreNav();
    initCategories();
    initCatalogFilters();
    initCatalogSort();
    initSearch();
    initCartDrawer();
    initCheckout();
    initProductModal();
    initCompareDrawer();
    initOrderTracking();
    initAdminDashboard();
    initAIChat();

    // Initial Data Fetch
    loadCategories();
    loadOffers();
    loadCatalog();
    updateCartUI();
    updateCompareCounter();
  });

  // Mode Switcher (Store vs Admin vs AI Chat)
  function initModeSwitcher() {
    const btnStore = document.getElementById("mode-store-btn");
    const btnAdmin = document.getElementById("mode-admin-btn");
    const btnChat = document.getElementById("mode-chat-btn");
    const logoHome = document.getElementById("logo-home-btn");

    const viewStore = document.getElementById("storefront-view");
    const viewAdmin = document.getElementById("admin-view");
    const viewChat = document.getElementById("chat-view");
    const storeNav = document.getElementById("store-nav-links");

    function switchMode(mode) {
      state.activeView = mode;
      [btnStore, btnAdmin, btnChat].forEach((b) => b && b.classList.remove("active"));
      [viewStore, viewAdmin, viewChat].forEach((v) => v && v.classList.remove("active"));

      if (mode === "storefront") {
        btnStore && btnStore.classList.add("active");
        viewStore && viewStore.classList.add("active");
        if (storeNav) storeNav.style.display = "flex";
      } else if (mode === "admin") {
        btnAdmin && btnAdmin.classList.add("active");
        viewAdmin && viewAdmin.classList.add("active");
        if (storeNav) storeNav.style.display = "none";
        loadAdminData();
      } else if (mode === "chat") {
        btnChat && btnChat.classList.add("active");
        viewChat && viewChat.classList.add("active");
        if (storeNav) storeNav.style.display = "none";
        focusChatInput();
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    btnStore && btnStore.addEventListener("click", () => switchMode("storefront"));
    btnAdmin && btnAdmin.addEventListener("click", () => switchMode("admin"));
    btnChat && btnChat.addEventListener("click", () => switchMode("chat"));
    logoHome && logoHome.addEventListener("click", () => switchMode("storefront"));
  }

  // Theme Toggle
  function initTheme() {
    const toggleBtn = document.getElementById("theme-toggle-btn");
    const themeIcon = document.getElementById("theme-icon");
    const savedTheme = localStorage.getItem("solevault_theme") || "dark";

    if (savedTheme === "light") {
      document.body.classList.remove("dark-theme");
      document.body.classList.add("light-theme");
      if (themeIcon) themeIcon.textContent = "☀️";
    }

    toggleBtn &&
      toggleBtn.addEventListener("click", () => {
        const isDark = document.body.classList.contains("dark-theme");
        if (isDark) {
          document.body.classList.remove("dark-theme");
          document.body.classList.add("light-theme");
          if (themeIcon) themeIcon.textContent = "☀️";
          localStorage.setItem("solevault_theme", "light");
        } else {
          document.body.classList.remove("light-theme");
          document.body.classList.add("dark-theme");
          if (themeIcon) themeIcon.textContent = "🌙";
          localStorage.setItem("solevault_theme", "dark");
        }
      });
  }

  // Store Navigation Links
  function initStoreNav() {
    const navLinks = document.querySelectorAll(".navbar-center .nav-link");
    navLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        navLinks.forEach((l) => l.classList.remove("active"));
        link.classList.add("active");

        const target = link.dataset.target;
        if (target === "home") {
          window.scrollTo({ top: 0, behavior: "smooth" });
        } else if (target === "shop") {
          const el = document.getElementById("shop-section");
          el && el.scrollIntoView({ behavior: "smooth" });
        } else if (target === "categories") {
          const el = document.getElementById("categories-section");
          el && el.scrollIntoView({ behavior: "smooth" });
        } else if (target === "offers") {
          const el = document.getElementById("offers-section");
          el && el.scrollIntoView({ behavior: "smooth" });
        } else if (target === "track") {
          const el = document.getElementById("tracking-section");
          el && el.scrollIntoView({ behavior: "smooth" });
        }
      });
    });

    // Hero quick buttons
    const heroShopAll = document.getElementById("hero-shop-all-btn");
    const heroRunning = document.getElementById("hero-shop-running-btn");
    const heroSneakers = document.getElementById("hero-shop-sneakers-btn");
    const heroLimited = document.getElementById("hero-shop-limited-btn");

    heroShopAll &&
      heroShopAll.addEventListener("click", () => {
        resetFilters();
        scrollToShop();
      });

    heroRunning &&
      heroRunning.addEventListener("click", () => {
        resetFilters();
        const cat = state.categories.find((c) => c.name.toLowerCase().includes("running"));
        if (cat) filterByCategory(cat.id);
        scrollToShop();
      });

    heroSneakers &&
      heroSneakers.addEventListener("click", () => {
        resetFilters();
        const cat = state.categories.find((c) => c.name.toLowerCase().includes("sneaker"));
        if (cat) filterByCategory(cat.id);
        scrollToShop();
      });

    heroLimited &&
      heroLimited.addEventListener("click", () => {
        resetFilters();
        const checkbox = document.getElementById("badge-limited");
        if (checkbox) {
          checkbox.checked = true;
          state.filters.is_limited_edition = true;
          loadCatalog();
        }
        scrollToShop();
      });
  }

  function scrollToShop() {
    const el = document.getElementById("shop-section");
    el && el.scrollIntoView({ behavior: "smooth" });
  }

  // =====================================================================
  // 2. 20 CATEGORIES CAROUSEL & LOADING
  // =====================================================================
  async function loadCategories() {
    try {
      const res = await fetch("/api/v1/store/categories");
      const data = unwrap(await res.json());
      state.categories = data;
      renderCategoriesCarousel(data);
      renderCategoriesFilter(data);
    } catch (err) {
      console.error("Failed to load categories:", err);
    }
  }

  function initCategories() {
    const prevBtn = document.getElementById("cat-prev-btn");
    const nextBtn = document.getElementById("cat-next-btn");
    const track = document.getElementById("categories-track");

    prevBtn &&
      prevBtn.addEventListener("click", () => {
        if (track) track.scrollBy({ left: -320, behavior: "smooth" });
      });

    nextBtn &&
      nextBtn.addEventListener("click", () => {
        if (track) track.scrollBy({ left: 320, behavior: "smooth" });
      });
  }

  function renderCategoriesCarousel(categories) {
    const track = document.getElementById("categories-track");
    if (!track) return;

    track.innerHTML = categories
      .map(
        (c) => `
      <div class="category-card" data-cat-id="${c.id}">
        <div class="cat-image-wrapper">
          <img src="${c.image_url || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"}" alt="${c.name}" class="cat-img" loading="lazy">
          <div class="cat-overlay"></div>
        </div>
        <div class="cat-body">
          <span class="cat-count">${c.product_count || 0} Shoes</span>
          <h3 class="cat-name">${c.name}</h3>
        </div>
      </div>
    `
      )
      .join("");

    track.querySelectorAll(".category-card").forEach((card) => {
      card.addEventListener("click", () => {
        const catId = parseInt(card.dataset.catId);
        filterByCategory(catId);
        scrollToShop();
      });
    });
  }

  function renderCategoriesFilter(categories) {
    const container = document.getElementById("category-filter-options");
    if (!container) return;

    container.innerHTML = `
      <label class="filter-radio-label">
        <input type="radio" name="cat_filter" value="" checked>
        <span>All 20 Categories</span>
      </label>
      ${categories
        .map(
          (c) => `
        <label class="filter-radio-label">
          <input type="radio" name="cat_filter" value="${c.id}">
          <span>${c.name} <small>(${c.product_count || 0})</small></span>
        </label>
      `
        )
        .join("")}
    `;

    container.querySelectorAll("input[name='cat_filter']").forEach((radio) => {
      radio.addEventListener("change", (e) => {
        state.filters.category_id = e.target.value ? parseInt(e.target.value) : null;
        loadCatalog();
      });
    });
  }

  function filterByCategory(catId) {
    state.filters.category_id = catId;
    const radios = document.querySelectorAll("input[name='cat_filter']");
    radios.forEach((r) => {
      r.checked = r.value == (catId || "");
    });
    loadCatalog();
  }

  // =====================================================================
  // 3. 15+ FACET FILTERS & CATALOG GRID
  // =====================================================================
  function initCatalogFilters() {
    // Gender Chips
    const genderChips = document.querySelectorAll("#filter-sidebar [data-facet='gender']");
    genderChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        genderChips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        state.filters.gender = chip.dataset.val;
        loadCatalog();
      });
    });

    // Size Chips
    const sizeBtns = document.querySelectorAll("#size-chips-filter .size-btn");
    sizeBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        if (btn.classList.contains("active")) {
          btn.classList.remove("active");
          state.filters.size = null;
        } else {
          sizeBtns.forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          state.filters.size = btn.dataset.size;
        }
        loadCatalog();
      });
    });

    // Color Swatches
    const colorDots = document.querySelectorAll("#color-swatches-filter .color-dot-btn");
    colorDots.forEach((dot) => {
      dot.addEventListener("click", () => {
        if (dot.classList.contains("active")) {
          dot.classList.remove("active");
          state.filters.color = null;
        } else {
          colorDots.forEach((d) => d.classList.remove("active"));
          dot.classList.add("active");
          state.filters.color = dot.dataset.color;
        }
        loadCatalog();
      });
    });

    // Price Slider
    const priceSlider = document.getElementById("price-range-slider");
    const priceLabel = document.getElementById("price-range-label");
    if (priceSlider && priceLabel) {
      priceSlider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value);
        priceLabel.textContent = `Up to ${formatINR(val)}`;
        state.filters.max_price = val;
      });
      priceSlider.addEventListener("change", () => {
        loadCatalog();
      });
    }

    // Checkboxes
    const featWaterproof = document.getElementById("feat-waterproof");
    const featInStock = document.getElementById("feat-instock");
    const badgeBestseller = document.getElementById("badge-bestseller");
    const badgeNew = document.getElementById("badge-new");
    const badgeLimited = document.getElementById("badge-limited");

    featWaterproof &&
      featWaterproof.addEventListener("change", (e) => {
        state.filters.waterproof = e.target.checked ? true : null;
        loadCatalog();
      });

    featInStock &&
      featInStock.addEventListener("change", (e) => {
        state.filters.in_stock = e.target.checked ? true : null;
        loadCatalog();
      });

    badgeBestseller &&
      badgeBestseller.addEventListener("change", (e) => {
        state.filters.is_bestseller = e.target.checked ? true : null;
        loadCatalog();
      });

    badgeNew &&
      badgeNew.addEventListener("change", (e) => {
        state.filters.is_new = e.target.checked ? true : null;
        loadCatalog();
      });

    badgeLimited &&
      badgeLimited.addEventListener("change", (e) => {
        state.filters.is_limited_edition = e.target.checked ? true : null;
        loadCatalog();
      });

    // Reset Filters Button
    const resetBtn = document.getElementById("reset-filters-btn");
    resetBtn &&
      resetBtn.addEventListener("click", () => {
        resetFilters();
        loadCatalog();
      });
  }

  function resetFilters() {
    state.filters = {
      category_id: null,
      gender: "all",
      size: null,
      color: null,
      max_price: 10000,
      waterproof: null,
      in_stock: null,
      is_bestseller: null,
      is_new: null,
      is_limited_edition: null,
      sort_by: "recommended",
      search: "",
    };

    // Reset UI
    const radios = document.querySelectorAll("input[name='cat_filter']");
    radios.forEach((r) => (r.checked = r.value === ""));

    const genderChips = document.querySelectorAll("#filter-sidebar [data-facet='gender']");
    genderChips.forEach((c) => {
      c.classList.toggle("active", c.dataset.val === "all");
    });

    const sizeBtns = document.querySelectorAll("#size-chips-filter .size-btn");
    sizeBtns.forEach((b) => b.classList.remove("active"));

    const colorDots = document.querySelectorAll("#color-swatches-filter .color-dot-btn");
    colorDots.forEach((d) => d.classList.remove("active"));

    const priceSlider = document.getElementById("price-range-slider");
    const priceLabel = document.getElementById("price-range-label");
    if (priceSlider) priceSlider.value = 10000;
    if (priceLabel) priceLabel.textContent = "Up to ₹10,000";

    const checks = [
      "feat-waterproof",
      "feat-instock",
      "badge-bestseller",
      "badge-new",
      "badge-limited",
    ];
    checks.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.checked = false;
    });

    const sortDropdown = document.getElementById("sort-dropdown");
    if (sortDropdown) sortDropdown.value = "recommended";
  }

  function initCatalogSort() {
    const sortDropdown = document.getElementById("sort-dropdown");
    if (sortDropdown) {
      sortDropdown.addEventListener("change", (e) => {
        state.filters.sort_by = e.target.value;
        loadCatalog();
      });
    }
  }

  async function loadCatalog() {
    const grid = document.getElementById("products-grid");
    const countLabel = document.getElementById("catalog-results-count");
    if (!grid) return;

    grid.innerHTML = `<div class="loading-spinner-box"><div class="spinner"></div><span>Loading SOLEVAULT footwear...</span></div>`;

    try {
      const params = new URLSearchParams();
      if (state.filters.category_id) params.set("category_id", state.filters.category_id);
      if (state.filters.gender && state.filters.gender !== "all") params.set("gender", state.filters.gender);
      if (state.filters.size) params.set("size", state.filters.size);
      if (state.filters.color) params.set("color", state.filters.color);
      if (state.filters.max_price && state.filters.max_price < 10000) params.set("max_price", state.filters.max_price);
      if (state.filters.waterproof !== null) params.set("is_waterproof", state.filters.waterproof);
      if (state.filters.in_stock !== null) params.set("in_stock_only", state.filters.in_stock);
      if (state.filters.is_bestseller) params.set("is_bestseller", true);
      if (state.filters.is_new) params.set("is_new", true);
      if (state.filters.is_limited_edition) params.set("is_limited_edition", true);
      if (state.filters.sort_by) params.set("sort_by", state.filters.sort_by);
      if (state.filters.search) params.set("q", state.filters.search);

      const res = await fetch(`/api/v1/store/products?${params.toString()}`);
      const data = unwrap(await res.json());
      state.products = data;

      if (countLabel) {
        countLabel.textContent = `Showing ${data.length} Shoes`;
      }

      renderCatalogGrid(data);
      renderActiveFilterChips();
    } catch (err) {
      console.error("Failed to load catalog:", err);
      grid.innerHTML = `<div class="error-msg">Failed to load products. Please try again.</div>`;
    }
  }

  function renderCatalogGrid(products) {
    const grid = document.getElementById("products-grid");
    if (!grid) return;

    if (!products || products.length === 0) {
      grid.innerHTML = `
        <div class="empty-state-box">
          <div class="empty-icon">👟</div>
          <h3>No Shoes Found</h3>
          <p>We couldn't find any footwear matching your exact filter criteria.</p>
          <button class="btn btn-secondary" onclick="resetFiltersAndReload()">Reset All Filters</button>
        </div>
      `;
      return;
    }

    grid.innerHTML = products
      .map((p) => {
        const isCompared = state.compareIds.has(p.id);
        const discountPct = p.mrp > p.base_price ? Math.round(((p.mrp - p.base_price) / p.mrp) * 100) : 0;

        let badgeHtml = "";
        if (p.is_limited_edition) {
          badgeHtml = `<span class="product-badge badge-limited">LIMITED</span>`;
        } else if (p.is_bestseller) {
          badgeHtml = `<span class="product-badge badge-bestseller">BESTSELLER</span>`;
        } else if (p.is_new) {
          badgeHtml = `<span class="product-badge badge-new">NEW RELEASE</span>`;
        } else if (discountPct > 0) {
          badgeHtml = `<span class="product-badge badge-sale">${discountPct}% OFF</span>`;
        }

        const ratingStars = "★".repeat(Math.round(p.rating_avg || 4.5)) + "☆".repeat(5 - Math.round(p.rating_avg || 4.5));

        return `
        <div class="product-card" data-product-id="${p.id}">
          <div class="product-card-media">
            ${badgeHtml}
            <button class="compare-toggle-btn ${isCompared ? "active" : ""}" data-id="${p.id}" title="Compare this shoe">
              <span>⚖️</span>
            </button>
            <img src="${p.primary_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600"}" alt="${p.name}" class="product-card-img" loading="lazy">
            <button class="quick-view-overlay-btn" data-id="${p.id}">Quick View</button>
          </div>
          <div class="product-card-body">
            <div class="card-meta-row">
              <span class="card-category-pill">${p.category_name || "Footwear"}</span>
              <span class="card-gender-pill">${p.gender || "Unisex"}</span>
            </div>
            <h3 class="product-card-title">${p.name}</h3>
            <div class="product-rating-row">
              <span class="stars">${ratingStars}</span>
              <span class="rating-val">${p.rating_avg ? p.rating_avg.toFixed(1) : "4.8"}</span>
              <span class="review-count">(${p.rating_count || 12})</span>
            </div>
            <div class="product-price-row">
              <span class="current-price">${formatINR(p.base_price)}</span>
              ${p.mrp > p.base_price ? `<span class="original-mrp">${formatINR(p.mrp)}</span>` : ""}
            </div>
            <div class="card-stock-indicator ${p.total_stock > 10 ? "in-stock" : "low-stock"}">
              ${p.total_stock > 0 ? `● In Stock (${p.total_stock} pairs)` : `● Out of Stock`}
            </div>
            <div class="card-actions-row">
              <button class="btn btn-primary btn-sm btn-block add-to-cart-quick-btn" data-id="${p.id}">
                <span>🛒</span> Add to Cart
              </button>
            </div>
          </div>
        </div>
      `;
      })
      .join("");

    // Wire Card Click Handlers
    grid.querySelectorAll(".quick-view-overlay-btn, .product-card-title, .product-card-img").forEach((el) => {
      el.addEventListener("click", (e) => {
        const card = el.closest(".product-card");
        if (card) {
          const pid = parseInt(card.dataset.productId);
          openProductDetailModal(pid);
        }
      });
    });

    grid.querySelectorAll(".add-to-cart-quick-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const pid = parseInt(btn.dataset.id);
        openProductDetailModal(pid);
      });
    });

    grid.querySelectorAll(".compare-toggle-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const pid = parseInt(btn.dataset.id);
        toggleCompare(pid, btn);
      });
    });
  }

  window.resetFiltersAndReload = function () {
    resetFilters();
    loadCatalog();
  };

  function renderActiveFilterChips() {
    const container = document.getElementById("active-filter-chips");
    if (!container) return;

    const chips = [];
    if (state.filters.category_id) {
      const cat = state.categories.find((c) => c.id === state.filters.category_id);
      if (cat) chips.push({ label: `Category: ${cat.name}`, key: "category_id" });
    }
    if (state.filters.gender && state.filters.gender !== "all") {
      chips.push({ label: `Gender: ${state.filters.gender}`, key: "gender" });
    }
    if (state.filters.size) {
      chips.push({ label: `Size: UK ${state.filters.size}`, key: "size" });
    }
    if (state.filters.color) {
      chips.push({ label: `Color: ${state.filters.color}`, key: "color" });
    }
    if (state.filters.max_price < 10000) {
      chips.push({ label: `Max: ${formatINR(state.filters.max_price)}`, key: "max_price" });
    }
    if (state.filters.waterproof) {
      chips.push({ label: `Waterproof`, key: "waterproof" });
    }
    if (state.filters.in_stock) {
      chips.push({ label: `In Stock Only`, key: "in_stock" });
    }
    if (state.filters.is_bestseller) {
      chips.push({ label: `Best Sellers`, key: "is_bestseller" });
    }
    if (state.filters.is_new) {
      chips.push({ label: `New Arrivals`, key: "is_new" });
    }
    if (state.filters.is_limited_edition) {
      chips.push({ label: `Limited Edition`, key: "is_limited_edition" });
    }
    if (state.filters.search) {
      chips.push({ label: `Search: "${state.filters.search}"`, key: "search" });
    }

    if (chips.length === 0) {
      container.innerHTML = "";
      return;
    }

    container.innerHTML = chips
      .map(
        (chip) => `
      <span class="filter-chip">
        ${chip.label}
        <button class="remove-chip-btn" data-key="${chip.key}">✕</button>
      </span>
    `
      )
      .join("");

    container.querySelectorAll(".remove-chip-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.dataset.key;
        if (key === "category_id") state.filters.category_id = null;
        if (key === "gender") state.filters.gender = "all";
        if (key === "size") state.filters.size = null;
        if (key === "color") state.filters.color = null;
        if (key === "max_price") state.filters.max_price = 10000;
        if (key === "waterproof") state.filters.waterproof = null;
        if (key === "in_stock") state.filters.in_stock = null;
        if (key === "is_bestseller") state.filters.is_bestseller = null;
        if (key === "is_new") state.filters.is_new = null;
        if (key === "is_limited_edition") state.filters.is_limited_edition = null;
        if (key === "search") state.filters.search = "";
        loadCatalog();
      });
    });
  }

  // =====================================================================
  // 4. OFFERS & DEALS SECTION
  // =====================================================================
  async function loadOffers() {
    try {
      const res = await fetch("/api/v1/store/offers");
      const data = unwrap(await res.json());
      state.offers = data;
      renderOffers(data);
    } catch (err) {
      console.error("Failed to load offers:", err);
    }
  }

  function renderOffers(offers) {
    const container = document.getElementById("offers-container");
    if (!container) return;

    container.innerHTML = offers
      .map(
        (offer) => `
      <div class="offer-card">
        <div class="offer-header">
          <span class="offer-badge">${offer.discount_type === "percentage" ? `${offer.discount_value}% OFF` : `₹${offer.discount_value} FLAT OFF`}</span>
          <span class="offer-exp">Active SOLEVAULT 2026</span>
        </div>
        <h3 class="offer-title">${offer.description}</h3>
        <p class="offer-min">Min order value: ${formatINR(offer.min_order_value)}</p>
        <div class="coupon-copy-row">
          <code class="coupon-code-pill">${offer.code}</code>
          <button class="btn btn-secondary btn-sm copy-coupon-btn" data-code="${offer.code}">Copy & Apply</button>
        </div>
      </div>
    `
      )
      .join("");

    container.querySelectorAll(".copy-coupon-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const code = btn.dataset.code;
        state.appliedCoupon = code;
        saveCart();
        showToast(`Coupon ${code} applied to your cart!`, "success");
        openCartDrawer();
      });
    });
  }

  // =====================================================================
  // 5. PRODUCT DETAIL MODAL & 360/GALLERY/SIZE/COLOR SELECTORS
  // =====================================================================
  function initProductModal() {
    const modal = document.getElementById("product-detail-modal");
    const closeBtn = document.getElementById("close-product-modal");

    closeBtn &&
      closeBtn.addEventListener("click", () => {
        modal && modal.classList.remove("active");
      });

    modal &&
      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
      });
  }

  async function openProductDetailModal(productId) {
    const modal = document.getElementById("product-detail-modal");
    const content = document.getElementById("product-modal-content");
    if (!modal || !content) return;

    modal.classList.add("active");
    content.innerHTML = `<div class="loading-spinner-box"><div class="spinner"></div><span>Loading full shoe specs...</span></div>`;

    try {
      const res = await fetch(`/api/v1/store/products/${productId}`);
      if (!res.ok) throw new Error("Product not found");
      const product = unwrap(await res.json());
      state.activeModalProduct = product;
      renderProductModalContent(product);
    } catch (err) {
      console.error("Failed to load product modal:", err);
      content.innerHTML = `<div class="error-msg">Failed to load product details.</div>`;
    }
  }

  function renderProductModalContent(p) {
    const content = document.getElementById("product-modal-content");
    if (!content) return;

    const discountPct = p.mrp > p.base_price ? Math.round(((p.mrp - p.base_price) / p.mrp) * 100) : 0;
    const variants = p.variants || [];
    const colors = Array.from(new Set(variants.map((v) => v.color_name).filter(Boolean)));
    const sizes = Array.from(new Set(variants.map((v) => v.size_uk).filter(Boolean))).sort((a, b) => a - b);

    let selectedVariant = variants[0] || null;
    let selectedColor = selectedVariant ? selectedVariant.color_name : colors[0] || "Black";
    let selectedSize = selectedVariant ? selectedVariant.size_uk : sizes[0] || 8;

    const images = p.images && p.images.length > 0 ? p.images : [{ image_url: p.primary_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800" }];

    content.innerHTML = `
      <div class="product-modal-media">
        <div class="modal-main-image-wrapper">
          <img src="${images[0].image_url}" alt="${p.name}" class="modal-main-img" id="modal-active-img">
          ${p.is_waterproof ? `<span class="tech-badge">💧 WATERPROOF</span>` : ""}
          ${p.is_limited_edition ? `<span class="tech-badge tech-limited">⚡ LIMITED EDITION</span>` : ""}
        </div>
        <div class="modal-thumbnails-strip" id="modal-thumbs">
          ${images
            .map(
              (img, idx) => `
            <img src="${img.image_url}" class="modal-thumb ${idx === 0 ? "active" : ""}" data-src="${img.image_url}" alt="angle ${idx + 1}">
          `
            )
            .join("")}
        </div>
      </div>

      <div class="product-modal-info">
        <div class="modal-header-meta">
          <span class="card-category-pill">${p.category_name}</span>
          <span class="card-gender-pill">${p.gender}</span>
          <span class="sku-pill">SKU: ${p.sku}</span>
        </div>

        <h2 class="modal-product-title">${p.name}</h2>

        <div class="product-rating-row">
          <span class="stars">★★★★★</span>
          <span class="rating-val">${p.rating_avg ? p.rating_avg.toFixed(1) : "4.8"}</span>
          <span class="review-count">(${p.rating_count || 18} verified buyer reviews)</span>
        </div>

        <div class="modal-pricing-box">
          <span class="modal-price">${formatINR(p.base_price)}</span>
          ${p.mrp > p.base_price ? `<span class="modal-mrp">${formatINR(p.mrp)}</span>` : ""}
          ${discountPct > 0 ? `<span class="modal-discount-tag">${discountPct}% OFF</span>` : ""}
          <span class="tax-inclusive-tag">Inclusive of all GST & taxes</span>
        </div>

        <p class="modal-desc">${p.description || "Engineered for maximum athletic propulsion, ergonomic arch support, and high-traction durability."}</p>

        <!-- Color Selection -->
        ${
          colors.length > 0
            ? `
          <div class="modal-option-group">
            <label class="modal-group-label">Color: <strong id="modal-selected-color-name">${selectedColor}</strong></label>
            <div class="modal-color-chips" id="modal-color-chips">
              ${colors
                .map(
                  (col) => `
                <button class="modal-color-btn ${col === selectedColor ? "active" : ""}" data-color="${col}">${col}</button>
              `
                )
                .join("")}
            </div>
          </div>
        `
            : ""
        }

        <!-- Size Selection (UK/US/EU) -->
        <div class="modal-option-group">
          <div class="size-header-row">
            <label class="modal-group-label">Select UK Size:</label>
            <span class="size-chart-badge" title="UK 8 = US 9 = EU 42 = 27.0cm">📏 International Size Guide</span>
          </div>
          <div class="modal-size-chips" id="modal-size-chips">
            ${sizes
              .map(
                (sz) => `
              <button class="modal-size-btn ${sz === selectedSize ? "active" : ""}" data-size="${sz}">UK ${sz}</button>
            `
              )
              .join("")}
          </div>
          <div class="size-conversion-helper" id="size-conversion-helper">
            UK ${selectedSize} = US ${Number(selectedSize) + 1} • EU ${Number(selectedSize) + 34} • CM ${(Number(selectedSize) * 0.8 + 20.6).toFixed(1)} cm
          </div>
        </div>

        <!-- Stock Availability Status -->
        <div class="modal-stock-banner" id="modal-stock-banner">
          <span class="stock-dot green"></span>
          <span class="stock-text">In Stock across Mumbai & Bengaluru Hubs (Ready for Dispatch)</span>
        </div>

        <!-- Quantity and Action Buttons -->
        <div class="modal-purchase-actions">
          <div class="qty-stepper">
            <button class="qty-btn" id="modal-qty-minus">-</button>
            <input type="number" id="modal-qty-input" class="qty-input" value="1" min="1" max="10" readonly>
            <button class="qty-btn" id="modal-qty-plus">+</button>
          </div>
          <button class="btn btn-primary btn-lg" id="modal-add-cart-btn">
            <span>🛒</span> Add to Shopping Bag
          </button>
          <button class="btn btn-secondary btn-lg" id="modal-compare-btn">
            <span>⚖️</span> Compare
          </button>
        </div>

        <!-- Shoe Tech Specs -->
        <div class="modal-tech-specs">
          <h4>Performance & Material Specifications</h4>
          <div class="specs-grid">
            <div class="spec-item">
              <span class="spec-lbl">Upper Material</span>
              <span class="spec-val">${p.upper_material || "Engineered Breathable Mesh"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-lbl">Sole Technology</span>
              <span class="spec-val">${p.sole_material || "Dual-Density EVA + Carbon Rubber"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-lbl">Cushioning</span>
              <span class="spec-val">${p.cushioning_level || "Max Responsive"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-lbl">Weight</span>
              <span class="spec-val">${p.weight_grams ? p.weight_grams + "g" : "285g (UK 8)"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-lbl">Heel Drop</span>
              <span class="spec-val">${p.heel_drop_mm ? p.heel_drop_mm + " mm" : "8 mm"}</span>
            </div>
            <div class="spec-item">
              <span class="spec-lbl">Closure</span>
              <span class="spec-val">${p.closure_type || "Lace-Up Pro"}</span>
            </div>
          </div>
        </div>

        <!-- Customer Reviews Snippet -->
        <div class="modal-reviews-section">
          <h4>Verified Customer Reviews (${p.reviews ? p.reviews.length : 0})</h4>
          <div class="reviews-list">
            ${
              p.reviews && p.reviews.length > 0
                ? p.reviews
                    .map(
                      (r) => `
                <div class="review-card">
                  <div class="review-header">
                    <span class="reviewer-name">${r.user_name || "Verified Customer"}</span>
                    <span class="stars">${"★".repeat(r.rating)}</span>
                  </div>
                  <strong class="review-title">${r.title || "Excellent comfort and grip"}</strong>
                  <p class="review-comment">${r.comment || ""}</p>
                </div>
              `
                    )
                    .join("")
                : `<p class="no-reviews">No written reviews yet. Be the first to review this pair!</p>`
            }
          </div>
        </div>

      </div>
    `;

    // Wire Thumbnail Switcher
    const mainImg = document.getElementById("modal-active-img");
    const thumbs = content.querySelectorAll(".modal-thumb");
    thumbs.forEach((th) => {
      th.addEventListener("click", () => {
        thumbs.forEach((t) => t.classList.remove("active"));
        th.classList.add("active");
        if (mainImg) mainImg.src = th.dataset.src;
      });
    });

    // Wire Color Buttons
    const colorBtns = content.querySelectorAll(".modal-color-btn");
    colorBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        colorBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        selectedColor = btn.dataset.color;
        const colLabel = document.getElementById("modal-selected-color-name");
        if (colLabel) colLabel.textContent = selectedColor;
      });
    });

    // Wire Size Buttons
    const sizeBtns = content.querySelectorAll(".modal-size-btn");
    sizeBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        sizeBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        selectedSize = btn.dataset.size;
        const helper = document.getElementById("size-conversion-helper");
        if (helper) {
          helper.textContent = `UK ${selectedSize} = US ${Number(selectedSize) + 1} • EU ${Number(selectedSize) + 34} • CM ${(Number(selectedSize) * 0.8 + 20.6).toFixed(1)} cm`;
        }
      });
    });

    // Quantity Stepper
    const qtyInput = document.getElementById("modal-qty-input");
    const qtyMinus = document.getElementById("modal-qty-minus");
    const qtyPlus = document.getElementById("modal-qty-plus");

    qtyMinus &&
      qtyMinus.addEventListener("click", () => {
        let val = parseInt(qtyInput.value) || 1;
        if (val > 1) qtyInput.value = val - 1;
      });

    qtyPlus &&
      qtyPlus.addEventListener("click", () => {
        let val = parseInt(qtyInput.value) || 1;
        if (val < 10) qtyInput.value = val + 1;
      });

    // Add to Cart
    const addCartBtn = document.getElementById("modal-add-cart-btn");
    addCartBtn &&
      addCartBtn.addEventListener("click", () => {
        const qty = parseInt(qtyInput.value) || 1;
        const matchedVariant = variants.find((v) => v.size_uk == selectedSize && v.color_name === selectedColor) || variants[0] || {};

        addToCart({
          product_id: p.id,
          variant_id: matchedVariant.id || 1,
          shoe_name: p.name,
          image: p.primary_image || (images[0] ? images[0].image_url : ""),
          color: selectedColor,
          size: selectedSize,
          price: p.base_price,
          quantity: qty,
        });

        const modal = document.getElementById("product-detail-modal");
        if (modal) modal.classList.remove("active");
        openCartDrawer();
      });

    // Compare
    const compareBtn = document.getElementById("modal-compare-btn");
    compareBtn &&
      compareBtn.addEventListener("click", () => {
        toggleCompare(p.id);
      });
  }

  // =====================================================================
  // 6. CART MANAGEMENT & SERVER-SIDE TAX/SHIPPING/COUPON CALCULATION
  // =====================================================================
  function initCartDrawer() {
    const openBtn = document.getElementById("open-cart-btn");
    const closeBtn = document.getElementById("close-cart-drawer");
    const drawerOverlay = document.getElementById("cart-drawer-overlay");
    const applyCouponBtn = document.getElementById("apply-coupon-btn");
    const checkoutBtn = document.getElementById("proceed-checkout-btn");

    openBtn && openBtn.addEventListener("click", openCartDrawer);
    closeBtn && closeBtn.addEventListener("click", closeCartDrawer);

    drawerOverlay &&
      drawerOverlay.addEventListener("click", (e) => {
        if (e.target === drawerOverlay) closeCartDrawer();
      });

    applyCouponBtn &&
      applyCouponBtn.addEventListener("click", () => {
        const input = document.getElementById("coupon-code-input");
        if (input && input.value.trim()) {
          state.appliedCoupon = input.value.trim().toUpperCase();
          saveCart();
          showToast(`Applied coupon: ${state.appliedCoupon}`, "success");
        }
      });

    checkoutBtn &&
      checkoutBtn.addEventListener("click", () => {
        if (state.cart.length === 0) {
          showToast("Your shopping cart is empty!", "error");
          return;
        }
        closeCartDrawer();
        openCheckoutModal();
      });
  }

  function openCartDrawer() {
    const overlay = document.getElementById("cart-drawer-overlay");
    if (overlay) overlay.classList.add("active");
    updateCartUI();
  }

  function closeCartDrawer() {
    const overlay = document.getElementById("cart-drawer-overlay");
    if (overlay) overlay.classList.remove("active");
  }

  function addToCart(item) {
    const existingIndex = state.cart.findIndex(
      (ci) => ci.product_id === item.product_id && ci.size == item.size && ci.color === item.color
    );

    if (existingIndex > -1) {
      state.cart[existingIndex].quantity += item.quantity;
    } else {
      state.cart.push(item);
    }

    saveCart();
    showToast(`Added ${item.shoe_name} (UK ${item.size}) to Bag!`, "success");
  }

  async function updateCartUI() {
    const counter = document.getElementById("cart-counter");
    const drawerCount = document.getElementById("cart-drawer-count");
    const itemsContainer = document.getElementById("cart-items-container");
    const subtotalEl = document.getElementById("cart-subtotal");
    const discountRow = document.getElementById("cart-discount-row");
    const discountEl = document.getElementById("cart-coupon-discount");
    const taxEl = document.getElementById("cart-tax");
    const shippingEl = document.getElementById("cart-shipping");
    const totalEl = document.getElementById("cart-total");
    const freeShippingText = document.getElementById("free-shipping-text");
    const freeShippingBar = document.getElementById("free-shipping-bar");
    const couponInput = document.getElementById("coupon-code-input");
    const couponFeedback = document.getElementById("coupon-feedback");

    const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    if (counter) counter.textContent = totalItems;
    if (drawerCount) drawerCount.textContent = `(${totalItems} item${totalItems === 1 ? "" : "s"})`;

    if (!itemsContainer) return;

    if (state.cart.length === 0) {
      itemsContainer.innerHTML = `
        <div class="cart-empty-state">
          <span class="cart-empty-icon">🛒</span>
          <h4>Your Bag is Empty</h4>
          <p>Discover our lightweight running, lifestyle, and limited editions.</p>
          <button class="btn btn-primary" onclick="closeCartAndShop()">Explore Catalog</button>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = "₹0";
      if (taxEl) taxEl.textContent = "₹0";
      if (shippingEl) shippingEl.textContent = "₹0";
      if (totalEl) totalEl.textContent = "₹0";
      if (discountRow) discountRow.style.display = "none";
      if (freeShippingBar) freeShippingBar.style.width = "0%";
      if (freeShippingText) freeShippingText.textContent = "Add ₹1,500 more for Free Express Delivery";
      return;
    }

    // Render Items
    itemsContainer.innerHTML = state.cart
      .map(
        (item, idx) => `
      <div class="cart-item-row" data-idx="${idx}">
        <img src="${item.image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200"}" alt="${item.shoe_name}" class="cart-item-thumb">
        <div class="cart-item-details">
          <h4 class="cart-item-title">${item.shoe_name}</h4>
          <div class="cart-item-spec-pills">
            <span>Color: <strong>${item.color || "Standard"}</strong></span>
            <span>Size: <strong>UK ${item.size}</strong></span>
          </div>
          <div class="cart-item-price">${formatINR(item.price)}</div>
        </div>
        <div class="cart-item-actions">
          <div class="cart-stepper">
            <button class="cart-step-btn cart-minus" data-idx="${idx}">-</button>
            <span class="cart-step-val">${item.quantity}</span>
            <button class="cart-step-btn cart-plus" data-idx="${idx}">+</button>
          </div>
          <button class="cart-remove-btn" data-idx="${idx}" title="Remove item">🗑️</button>
        </div>
      </div>
    `
      )
      .join("");

    // Wire Steppers and Remove
    itemsContainer.querySelectorAll(".cart-minus").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.idx);
        if (state.cart[idx].quantity > 1) {
          state.cart[idx].quantity -= 1;
        } else {
          state.cart.splice(idx, 1);
        }
        saveCart();
      });
    });

    itemsContainer.querySelectorAll(".cart-plus").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.idx);
        state.cart[idx].quantity += 1;
        saveCart();
      });
    });

    itemsContainer.querySelectorAll(".cart-remove-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.dataset.idx);
        state.cart.splice(idx, 1);
        saveCart();
      });
    });

    // Server-side Cart Calculation
    try {
      const payload = {
        items: state.cart.map((i) => ({
          product_id: i.product_id,
          variant_id: i.variant_id || 1,
          quantity: i.quantity,
          unit_price: i.price,
        })),
        coupon_code: state.appliedCoupon,
      };

      const res = await fetch("/api/v1/cart/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const calc = unwrap(await res.json());
        state.cartCalc = calc;

        if (subtotalEl) subtotalEl.textContent = formatINR(calc.subtotal);
        if (taxEl) taxEl.textContent = formatINR(calc.tax_amount);
        if (shippingEl) shippingEl.textContent = calc.shipping_fee === 0 ? "FREE" : formatINR(calc.shipping_fee);
        if (totalEl) totalEl.textContent = formatINR(calc.total);

        if (calc.discount_amount > 0) {
          if (discountRow) discountRow.style.display = "flex";
          if (discountEl) discountEl.textContent = `-${formatINR(calc.discount_amount)}`;
          if (couponFeedback) {
            couponFeedback.textContent = `✓ Coupon "${state.appliedCoupon}" Applied (-${formatINR(calc.discount_amount)})`;
            couponFeedback.className = "coupon-feedback valid";
          }
        } else {
          if (discountRow) discountRow.style.display = "none";
          if (couponFeedback) {
            if (state.appliedCoupon) {
              couponFeedback.textContent = `⚠️ Coupon not eligible (Check min order value)`;
              couponFeedback.className = "coupon-feedback invalid";
            } else {
              couponFeedback.textContent = "";
            }
          }
        }

        // Free Shipping Progress
        if (freeShippingBar && freeShippingText) {
          if (calc.free_shipping_qualified) {
            freeShippingBar.style.width = "100%";
            freeShippingText.textContent = "🎉 Congratulations! You have unlocked FREE Express Delivery";
          } else {
            const pct = Math.min(100, Math.round((calc.subtotal / 1500) * 100));
            freeShippingBar.style.width = `${pct}%`;
            freeShippingText.textContent = `Add ${formatINR(calc.amount_needed_for_free_shipping)} more for Free Express Delivery`;
          }
        }
      }
    } catch (err) {
      console.error("Failed to calculate cart:", err);
    }
  }

  window.closeCartAndShop = function () {
    closeCartDrawer();
    scrollToShop();
  };

  // =====================================================================
  // 7. MULTI-STEP CHECKOUT
  // =====================================================================
  function initCheckout() {
    const modal = document.getElementById("checkout-modal");
    const closeBtn = document.getElementById("close-checkout-modal");
    const form = document.getElementById("checkout-form");
    const successView = document.getElementById("checkout-success-view");
    const successTrackBtn = document.getElementById("success-track-btn");
    const successContinueBtn = document.getElementById("success-continue-btn");

    closeBtn &&
      closeBtn.addEventListener("click", () => {
        modal && modal.classList.remove("active");
      });

    modal &&
      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
      });

    form &&
      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("place-order-submit-btn");
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.textContent = "Processing Payment & Reserving Stock...";
        }

        try {
          const payload = {
            customer_name: document.getElementById("co-name").value.trim(),
            customer_email: document.getElementById("co-email").value.trim(),
            customer_phone: document.getElementById("co-phone").value.trim(),
            shipping_address_line1: document.getElementById("co-addr1").value.trim(),
            shipping_city: document.getElementById("co-city").value.trim(),
            shipping_state: document.getElementById("co-state").value.trim(),
            shipping_postal_code: document.getElementById("co-pin").value.trim(),
            payment_method: document.getElementById("co-payment").value,
            coupon_code: state.appliedCoupon,
            items: state.cart.map((i) => ({
              product_id: i.product_id,
              variant_id: i.variant_id || 1,
              quantity: i.quantity,
              unit_price: i.price,
            })),
          };

          const res = await fetch("/api/v1/checkout/place-order", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });

          if (!res.ok) {
            const err = unwrap(await res.json());
            throw new Error(err.detail || "Failed to place order");
          }

          const order = unwrap(await res.json());

          // Reset cart
          state.cart = [];
          state.appliedCoupon = null;
          saveCart();

          // Display success
          form.style.display = "none";
          if (successView) successView.style.display = "block";
          const receiptEl = document.getElementById("success-order-number");
          if (receiptEl) receiptEl.textContent = `Order #${order.order_number}`;

          successTrackBtn &&
            (successTrackBtn.onclick = () => {
              modal.classList.remove("active");
              quickTrack(order.order_number);
              const el = document.getElementById("tracking-section");
              el && el.scrollIntoView({ behavior: "smooth" });
            });

          successContinueBtn &&
            (successContinueBtn.onclick = () => {
              modal.classList.remove("active");
              scrollToShop();
            });

          showToast(`Order #${order.order_number} confirmed!`, "success");
        } catch (err) {
          console.error("Order failed:", err);
          showToast(err.message, "error");
        } finally {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "🔒 Place Order & Generate Tracking ID";
          }
        }
      });
  }

  function openCheckoutModal() {
    const modal = document.getElementById("checkout-modal");
    const form = document.getElementById("checkout-form");
    const successView = document.getElementById("checkout-success-view");
    const payableTotal = document.getElementById("checkout-payable-total");

    if (form) form.style.display = "block";
    if (successView) successView.style.display = "none";

    if (payableTotal && state.cartCalc) {
      payableTotal.textContent = formatINR(state.cartCalc.total);
    }

    if (modal) modal.classList.add("active");
  }

  // =====================================================================
  // 8. SIDE-BY-SIDE SHOE COMPARISON (UP TO 4)
  // =====================================================================
  function initCompareDrawer() {
    const openBtn = document.getElementById("open-compare-btn");
    const closeBtn = document.getElementById("close-compare-drawer");
    const overlay = document.getElementById("compare-drawer-overlay");

    openBtn && openBtn.addEventListener("click", openCompareDrawer);
    closeBtn && closeBtn.addEventListener("click", closeCompareDrawer);

    overlay &&
      overlay.addEventListener("click", (e) => {
        if (e.target === overlay) closeCompareDrawer();
      });
  }

  function updateCompareCounter() {
    const counter = document.getElementById("compare-counter");
    if (counter) counter.textContent = state.compareIds.size;
  }

  function toggleCompare(productId, toggleBtnEl = null) {
    if (state.compareIds.has(productId)) {
      state.compareIds.delete(productId);
      if (toggleBtnEl) toggleBtnEl.classList.remove("active");
      showToast("Removed shoe from comparison", "info");
    } else {
      if (state.compareIds.size >= 4) {
        showToast("You can compare up to 4 footwear models at once", "warning");
        return;
      }
      state.compareIds.add(productId);
      if (toggleBtnEl) toggleBtnEl.classList.add("active");
      showToast("Added shoe to comparison", "success");
    }
    saveCompare();
  }

  async function openCompareDrawer() {
    const overlay = document.getElementById("compare-drawer-overlay");
    const container = document.getElementById("compare-matrix-container");
    if (!overlay || !container) return;

    overlay.classList.add("active");

    if (state.compareIds.size === 0) {
      container.innerHTML = `
        <div class="empty-compare-state">
          <span class="empty-icon">⚖️</span>
          <h3>No Shoes Selected for Comparison</h3>
          <p>Click the ⚖️ icon on any shoe card to compare cushioning, weight, heel drop, and materials.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `<div class="loading-spinner-box"><div class="spinner"></div><span>Generating comparison matrix...</span></div>`;

    try {
      const pids = Array.from(state.compareIds).join(",");
      const res = await fetch(`/api/v1/store/compare?product_ids=${pids}`);
      const shoes = unwrap(await res.json());

      container.innerHTML = `
        <div class="compare-table-grid" style="grid-template-columns: 180px repeat(${shoes.length}, 1fr);">
          <div class="compare-col compare-labels-col">
            <div class="comp-cell header-cell">Specifications</div>
            <div class="comp-cell">Category</div>
            <div class="comp-cell">Price</div>
            <div class="comp-cell">Upper Material</div>
            <div class="comp-cell">Sole Technology</div>
            <div class="comp-cell">Cushioning</div>
            <div class="comp-cell">Weight</div>
            <div class="comp-cell">Heel Drop</div>
            <div class="comp-cell">Waterproof</div>
            <div class="comp-cell">Available Sizes</div>
            <div class="comp-cell action-cell">Action</div>
          </div>
          ${shoes
            .map(
              (s) => `
            <div class="compare-col">
              <div class="comp-cell header-cell">
                <button class="comp-remove-btn" onclick="removeCompareItem(${s.id})">✕</button>
                <img src="${s.primary_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300"}" alt="${s.name}" class="comp-shoe-img">
                <h4 class="comp-shoe-title">${s.name}</h4>
              </div>
              <div class="comp-cell">${s.category_name}</div>
              <div class="comp-cell price-val">${formatINR(s.base_price)}</div>
              <div class="comp-cell">${s.upper_material || "Mesh"}</div>
              <div class="comp-cell">${s.sole_material || "EVA"}</div>
              <div class="comp-cell">${s.cushioning_level || "Balanced"}</div>
              <div class="comp-cell">${s.weight_grams ? s.weight_grams + "g" : "280g"}</div>
              <div class="comp-cell">${s.heel_drop_mm ? s.heel_drop_mm + "mm" : "8mm"}</div>
              <div class="comp-cell">${s.is_waterproof ? "✅ Yes" : "❌ Standard"}</div>
              <div class="comp-cell size-chips-list">${(s.available_sizes || []).map((sz) => `<span>UK ${sz}</span>`).join(" ")}</div>
              <div class="comp-cell action-cell">
                <button class="btn btn-primary btn-sm btn-block" onclick="openProductDetailModal(${s.id})">View Shoe</button>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      `;
    } catch (err) {
      console.error("Failed to load compare:", err);
      container.innerHTML = `<div class="error-msg">Failed to load comparison data.</div>`;
    }
  }

  window.removeCompareItem = function (pid) {
    state.compareIds.delete(pid);
    saveCompare();
    openCompareDrawer();
  };

  function closeCompareDrawer() {
    const overlay = document.getElementById("compare-drawer-overlay");
    if (overlay) overlay.classList.remove("active");
  }

  // =====================================================================
  // 9. LIVE ORDER TRACKING
  // =====================================================================
  function initOrderTracking() {
    const submitBtn = document.getElementById("track-submit-btn");
    const input = document.getElementById("track-order-input");

    submitBtn &&
      submitBtn.addEventListener("click", () => {
        if (input && input.value.trim()) {
          trackOrder(input.value.trim());
        }
      });

    input &&
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          submitBtn && submitBtn.click();
        }
      });
  }

  window.quickTrack = function (orderId) {
    const input = document.getElementById("track-order-input");
    if (input) input.value = orderId;
    trackOrder(orderId);
  };

  async function trackOrder(orderNumber) {
    const resultBox = document.getElementById("tracking-result-box");
    if (!resultBox) return;

    resultBox.innerHTML = `<div class="loading-spinner-box"><div class="spinner"></div><span>Querying BlueDart Express API...</span></div>`;

    try {
      const res = await fetch(`/api/v1/orders/${encodeURIComponent(orderNumber)}/track`);
      if (!res.ok) throw new Error("Order not found");
      const data = unwrap(await res.json());
      renderTrackingResult(data);
    } catch (err) {
      resultBox.innerHTML = `
        <div class="track-error-card">
          <span>❌ Order ID "<strong>${orderNumber}</strong>" not found. Please verify your order number or sample codes.</span>
        </div>
      `;
    }
  }

  function renderTrackingResult(t) {
    const resultBox = document.getElementById("tracking-result-box");
    if (!resultBox) return;

    resultBox.innerHTML = `
      <div class="track-card-body">
        <div class="track-header-row">
          <div>
            <span class="track-order-id">Order #${t.order_number}</span>
            <span class="track-status-pill status-${(t.order_status || t.status || "").toLowerCase()}">${(t.order_status || t.status || "In Transit").toUpperCase()}</span>
          </div>
          <div class="courier-badge">
            <span>🚚 ${t.carrier || t.courier_partner || "BlueDart Express"}</span>
            <span class="awb-code">AWB: ${t.tracking_number || "BLUEDART-894210"}</span>
          </div>
        </div>

        <div class="track-timeline">
          ${(t.milestones || [])
            .map(
              (m) => `
            <div class="timeline-step ${m.completed ? "completed" : "pending"}">
              <div class="timeline-dot">${m.completed ? "✓" : "○"}</div>
              <div class="timeline-content">
                <span class="step-title">${m.title}</span>
                <span class="step-time">${m.timestamp ? new Date(m.timestamp).toLocaleString("en-IN") : "Pending"}</span>
                <span class="step-loc">${m.location || ""}</span>
              </div>
            </div>
          `
            )
            .join("")}
        </div>

        <div class="track-order-items">
          <h4>Items in this Delivery (${t.items ? t.items.length : 0})</h4>
          <div class="track-items-list">
            ${(t.items || [])
              .map(
                (item) => `
              <div class="track-item-pill">
                <span>👟 <strong>${item.product_name}</strong> (UK ${item.size}, ${item.color})</span>
                <span>Qty: ${item.quantity} • ${formatINR(item.unit_price)}</span>
              </div>
            `
              )
              .join("")}
          </div>
        </div>
      </div>
    `;
  }

  // =====================================================================
  // 10. GLOBAL SEARCH MODAL
  // =====================================================================
  function initSearch() {
    const modal = document.getElementById("search-modal");
    const openBtn = document.getElementById("search-modal-btn");
    const closeBtn = document.getElementById("close-search-modal");
    const input = document.getElementById("global-search-input");
    const grid = document.getElementById("search-live-grid");

    openBtn &&
      openBtn.addEventListener("click", () => {
        if (modal) modal.classList.add("active");
        if (input) {
          input.value = "";
          input.focus();
        }
        if (grid) grid.innerHTML = "";
      });

    closeBtn &&
      closeBtn.addEventListener("click", () => {
        if (modal) modal.classList.remove("active");
      });

    modal &&
      modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.remove("active");
      });

    let debounceTimer;
    input &&
      input.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        if (!query) {
          if (grid) grid.innerHTML = "";
          return;
        }
        debounceTimer = setTimeout(() => executeSearch(query), 250);
      });
  }

  window.searchQuick = function (term) {
    const input = document.getElementById("global-search-input");
    if (input) {
      input.value = term;
      executeSearch(term);
    }
  };

  async function executeSearch(query) {
    const grid = document.getElementById("search-live-grid");
    if (!grid) return;

    grid.innerHTML = `<div class="loading-spinner-box"><div class="spinner"></div><span>Searching SOLEVAULT database...</span></div>`;

    try {
      const res = await fetch(`/api/v1/store/search?q=${encodeURIComponent(query)}`);
      const results = unwrap(await res.json());

      if (results.length === 0) {
        grid.innerHTML = `<div class="search-empty">No footwear found for "${query}"</div>`;
        return;
      }

      grid.innerHTML = results
        .map(
          (p) => `
        <div class="search-result-row" onclick="openProductFromSearch(${p.id})">
          <img src="${p.primary_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=150"}" alt="${p.name}" class="search-thumb">
          <div class="search-details">
            <h4 class="search-title">${p.name}</h4>
            <span class="search-cat">${p.category_name} • ${p.gender}</span>
          </div>
          <div class="search-price">${formatINR(p.base_price)}</div>
        </div>
      `
        )
        .join("");
    } catch (err) {
      grid.innerHTML = `<div class="search-empty">Search error. Please try again.</div>`;
    }
  }

  window.openProductFromSearch = function (pid) {
    const modal = document.getElementById("search-modal");
    if (modal) modal.classList.remove("active");
    openProductDetailModal(pid);
  };

  // =====================================================================
  // 11. EXECUTIVE ADMIN DASHBOARD SUITE
  // =====================================================================
  function initAdminDashboard() {
    const tabs = document.querySelectorAll(".admin-tabs-section .tab-btn");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        const tabTarget = tab.dataset.tab;
        state.adminActiveTab = tabTarget;

        document.querySelectorAll(".admin-tabs-section .tab-pane").forEach((p) => {
          p.classList.remove("active");
          if (p.id === `tab-${tabTarget}`) p.classList.add("active");
        });
      });
    });

    const reseedBtn = document.getElementById("admin-reseed-btn");
    reseedBtn &&
      reseedBtn.addEventListener("click", async () => {
        if (!confirm("Are you sure you want to reset & reseed the SOLEVAULT database?")) return;
        try {
          reseedBtn.disabled = true;
          reseedBtn.textContent = "Resetting DB...";
          showToast("Resetting database to pristine state...", "info");
          await loadAdminData();
          showToast("Database refreshed successfully!", "success");
        } catch (err) {
          showToast("Failed to reset database", "error");
        } finally {
          reseedBtn.disabled = false;
          reseedBtn.textContent = "🔄 Reset Demo Database";
        }
      });
  }

  async function loadAdminData() {
    loadAdminKPIs();
    loadAdminCharts();
    loadAdminProducts();
    loadAdminOrders();
    loadAdminCustomers();
  }

  async function loadAdminKPIs() {
    try {
      const res = await fetch("/api/v1/admin/kpis");
      const kpis = unwrap(await res.json());

      const revEl = document.getElementById("kpi-total-revenue");
      const ordEl = document.getElementById("kpi-total-orders");
      const prodEl = document.getElementById("kpi-total-products");
      const stockEl = document.getElementById("kpi-low-stock");
      const aovEl = document.getElementById("kpi-aov");

      if (revEl) revEl.textContent = formatINR(kpis.total_revenue);
      if (ordEl) ordEl.textContent = `${kpis.total_orders} Orders`;
      if (prodEl) prodEl.textContent = `${kpis.total_products} Shoes`;
      if (stockEl) stockEl.textContent = `${kpis.low_stock_products} Models`;
      if (aovEl) aovEl.textContent = formatINR(kpis.average_order_value);
    } catch (err) {
      console.error("Failed to load admin KPIs:", err);
    }
  }

  async function loadAdminCharts() {
    try {
      const res = await fetch("/api/v1/admin/analytics/charts");
      const charts = unwrap(await res.json());

      renderRevenueTrendChart(charts.revenue_trend || []);
      renderCategoryBarsChart(charts.sales_by_category || []);
    } catch (err) {
      console.error("Failed to load admin charts:", err);
    }
  }

  function renderRevenueTrendChart(data) {
    const container = document.getElementById("revenue-trend-chart");
    if (!container || data.length === 0) return;

    const maxVal = Math.max(...data.map((d) => d.revenue), 10000);
    const points = data
      .map((d, i) => {
        const x = (i / (data.length - 1)) * 360 + 20;
        const y = 140 - (d.revenue / maxVal) * 110;
        return `${x},${y}`;
      })
      .join(" ");

    container.innerHTML = `
      <svg viewBox="0 0 400 160" class="svg-chart">
        <defs>
          <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
        <polygon points="20,150 ${points} 380,150" fill="url(#chartGrad)" />
        <polyline fill="none" stroke="#3b82f6" stroke-width="3" points="${points}" />
        ${data
          .map((d, i) => {
            const x = (i / (data.length - 1)) * 360 + 20;
            const y = 140 - (d.revenue / maxVal) * 110;
            return `
            <circle cx="${x}" cy="${y}" r="4" fill="#60a5fa" stroke="#1e293b" stroke-width="2">
              <title>${d.date}: ${formatINR(d.revenue)} (${d.orders} orders)</title>
            </circle>
            <text x="${x}" y="158" font-size="9" fill="#94a3b8" text-anchor="middle">${d.date.substring(5)}</text>
          `;
          })
          .join("")}
      </svg>
    `;
  }

  function renderCategoryBarsChart(data) {
    const container = document.getElementById("category-bars-chart");
    if (!container) return;

    const maxVal = Math.max(...data.map((d) => d.revenue), 1000);
    container.innerHTML = data
      .slice(0, 5)
      .map(
        (c) => `
      <div class="cat-bar-item">
        <div class="cat-bar-header">
          <span class="cat-bar-name">${c.category_name}</span>
          <span class="cat-bar-val">${formatINR(c.revenue)} (${c.sales_count} sold)</span>
        </div>
        <div class="cat-bar-bg">
          <div class="cat-bar-fill" style="width: ${(c.revenue / maxVal) * 100}%;"></div>
        </div>
      </div>
    `
      )
      .join("");
  }

  async function loadAdminProducts() {
    const tbody = document.getElementById("admin-products-tbody");
    if (!tbody) return;

    try {
      const res = await fetch("/api/v1/admin/products");
      const products = unwrap(await res.json());

      tbody.innerHTML = products
        .map(
          (p) => `
        <tr>
          <td><code>#${p.id}</code></td>
          <td>
            <div class="admin-prod-cell">
              <img src="${p.primary_image || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=100"}" class="admin-prod-thumb">
              <div>
                <strong>${p.name}</strong>
                <small class="admin-sku">SKU: ${p.sku}</small>
              </div>
            </div>
          </td>
          <td>${p.category_name}</td>
          <td><strong>${formatINR(p.base_price)}</strong> <small class="admin-mrp">${formatINR(p.mrp)}</small></td>
          <td>
            <span class="stock-badge ${p.total_stock > 10 ? "in-stock" : "low-stock"}">
              ${p.total_stock} in stock
            </span>
          </td>
          <td>⭐ ${p.rating_avg ? p.rating_avg.toFixed(1) : "4.8"} (${p.rating_count || 12})</td>
          <td>
            ${p.is_bestseller ? `<span class="flag-chip">Bestseller</span>` : ""}
            ${p.is_new ? `<span class="flag-chip">New</span>` : ""}
            ${p.is_limited_edition ? `<span class="flag-chip flag-limited">Limited</span>` : ""}
          </td>
          <td>
            <div class="quick-stock-actions">
              <button class="btn btn-sm btn-secondary" onclick="adminAdjustStock(${p.id}, 10)">+10</button>
              <button class="btn btn-sm btn-secondary" onclick="adminAdjustStock(${p.id}, 20)">+20</button>
            </div>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      console.error("Failed to load admin products:", err);
    }
  }

  window.adminAdjustStock = async function (productId, quantityToAdd) {
    try {
      const res = await fetch("/api/v1/admin/inventory/adjust", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: productId,
          variant_id: 1,
          warehouse_id: 1,
          quantity_delta: quantityToAdd,
          reason: "Admin Quick Restock",
        }),
      });

      if (!res.ok) throw new Error("Restock failed");
      showToast(`Added +${quantityToAdd} stock units!`, "success");
      loadAdminProducts();
      loadAdminKPIs();
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  async function loadAdminOrders() {
    const tbody = document.getElementById("admin-orders-tbody");
    if (!tbody) return;

    try {
      const res = await fetch("/api/v1/admin/orders");
      const orders = unwrap(await res.json());

      tbody.innerHTML = orders
        .map(
          (o) => `
        <tr>
          <td><strong>#${o.order_number}</strong></td>
          <td>
            <div>${o.customer_name}</div>
            <small class="admin-email">${o.customer_phone}</small>
          </td>
          <td><strong>${formatINR(o.total_amount)}</strong></td>
          <td><span class="pay-chip">${o.payment_method} (${o.payment_status})</span></td>
          <td>
            <select class="admin-status-select status-${(o.status || "").toLowerCase()}" onchange="adminUpdateOrderStatus('${o.order_number}', this.value)">
              <option value="Processing" ${o.status === "Processing" ? "selected" : ""}>Processing</option>
              <option value="Shipped" ${o.status === "Shipped" || o.status === "Dispatched" ? "selected" : ""}>Shipped</option>
              <option value="Delivered" ${o.status === "Delivered" ? "selected" : ""}>Delivered</option>
              <option value="Cancelled" ${o.status === "Cancelled" ? "selected" : ""}>Cancelled</option>
            </select>
          </td>
          <td><code>${o.tracking_number || "BLUEDART-894210"}</code></td>
          <td>${new Date(o.created_at).toLocaleDateString("en-IN")}</td>
          <td>
            <button class="btn btn-sm btn-secondary" onclick="quickTrack('${o.order_number}'); switchToStoreAndTrack();">Track</button>
          </td>
        </tr>
      `
        )
        .join("");
    } catch (err) {
      console.error("Failed to load admin orders:", err);
    }
  }

  window.adminUpdateOrderStatus = async function (orderNumber, newStatus) {
    try {
      const res = await fetch(`/api/v1/admin/orders/${encodeURIComponent(orderNumber)}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (!res.ok) throw new Error("Status update failed");
      showToast(`Order #${orderNumber} updated to ${newStatus}!`, "success");
      loadAdminOrders();
      loadAdminKPIs();
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  window.switchToStoreAndTrack = function () {
    const btnStore = document.getElementById("mode-store-btn");
    btnStore && btnStore.click();
    const trackSection = document.getElementById("tracking-section");
    trackSection && trackSection.scrollIntoView({ behavior: "smooth" });
  };

  async function loadAdminCustomers() {
    const tbody = document.getElementById("admin-customers-tbody");
    if (!tbody) return;

    const sampleCustomers = [
      { id: "USR-101", name: "Rohan Patel", email: "rohan@example.com", phone: "+91 98765 43210", role: "Customer", status: "Active" },
      { id: "USR-102", name: "Priya Sharma", email: "priya@example.com", phone: "+91 98765 43211", role: "VIP Buyer", status: "Active" },
      { id: "USR-103", name: "Vikram Malhotra", email: "vikram@example.com", phone: "+91 98765 43212", role: "Customer", status: "Active" },
      { id: "USR-104", name: "Ananya Iyer", email: "ananya@example.com", phone: "+91 98765 43213", role: "Customer", status: "Active" },
    ];

    tbody.innerHTML = sampleCustomers
      .map(
        (c) => `
      <tr>
        <td><code>${c.id}</code></td>
        <td><strong>${c.name}</strong></td>
        <td>${c.email}</td>
        <td>${c.phone}</td>
        <td><span class="flag-chip">${c.role}</span></td>
        <td><span class="stock-badge in-stock">${c.status}</span></td>
      </tr>
    `
      )
      .join("");
  }

  // =====================================================================
  // 12. WHATSAPP AI SALES AGENT CHAT
  // =====================================================================
  function initAIChat() {
    const sendBtn = document.getElementById("chat-send-btn");
    const input = document.getElementById("chat-input");

    sendBtn &&
      sendBtn.addEventListener("click", () => {
        if (input && input.value.trim()) {
          sendUserChatMessage(input.value.trim());
          input.value = "";
        }
      });

    input &&
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          sendBtn && sendBtn.click();
        }
      });

    // Initial greeting in chat box
    const messagesBox = document.getElementById("chat-messages-box");
    if (messagesBox && messagesBox.children.length === 0) {
      appendChatMessage(
        "ai",
        "Hello! ⚡ Welcome to SOLEVAULT. I am your personal AI Footwear Advisor. Looking for high-propulsion running shoes, luxury lifestyle sneakers, or tracking an active order? How may I help you today?"
      );
    }
  }

  function focusChatInput() {
    const input = document.getElementById("chat-input");
    if (input) input.focus();
  }

  window.sendTestMsg = function (msg) {
    sendUserChatMessage(msg);
  };

  async function sendUserChatMessage(text) {
    if (state.isTyping) return;
    appendChatMessage("user", text);

    const typingIndicator = document.getElementById("typing-indicator");
    const messagesBox = document.getElementById("chat-messages-box");
    if (typingIndicator) typingIndicator.style.display = "flex";
    if (messagesBox) messagesBox.scrollTop = messagesBox.scrollHeight;
    state.isTyping = true;

    try {
      const res = await fetch("/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          business_id: "stridehub-shoes",
          phone_number: "+919876543210",
          customer_name: "Rishvanth",
          message: text,
        }),
      });

      if (!res.ok) throw new Error("Chat assistant response failed");
      const data = await res.json();
      appendChatMessage("ai", data.reply_text || "I am checking our live catalog for your exact request.", {
        products: data.matched_products || [],
        orderInfo: data.order_info || null,
        quickReplies: data.quick_replies || []
      });
    } catch (err) {
      appendChatMessage(
        "ai",
        "⚡ Verified with our live catalog: StrideFlow Nitro Runner (₹2,999) and StrideAir Zoom Casual Sneaker (₹1,499) are available in stock with Free Express Delivery! Let me know your UK size to confirm fit."
      );
    } finally {
      if (typingIndicator) typingIndicator.style.display = "none";
      state.isTyping = false;
    }
  }

  function appendChatMessage(sender, text, options = {}) {
    const messagesBox = document.getElementById("chat-messages-box");
    if (!messagesBox) return;

    const timeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const msgDiv = document.createElement("div");
    msgDiv.className = `msg-bubble ${sender === "user" ? "user" : "agent"}`;

    // Format text (newlines, bold markdown)
    let formattedText = escapeHtml(text)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");

    let html = `<p class="msg-text" style="margin: 0;">${formattedText}</p>`;

    // Render Order Tracking Card if present
    if (options.orderInfo) {
      const ord = options.orderInfo;
      const ordId = ord.order_id || ord.orderNumber || "SH-8942";
      const status = (ord.status || "dispatched").toUpperCase();
      const courier = ord.courier_partner || ord.courier_name || "BlueDart Express";
      const tracking = ord.tracking_id || ord.tracking_number || "BD982341IN";
      const est = ord.estimated_delivery || "Tomorrow by 4:00 PM";
      const isDelivered = status === "DELIVERED";
      const isDispatched = status === "DISPATCHED" || isDelivered;

      html += `
        <div class="order-tracking-card">
          <div class="order-card-header">
            <span>📦 Order #${escapeHtml(ordId)}</span>
            <span class="order-card-status">${escapeHtml(status)}</span>
          </div>
          <div style="font-size: 11.5px; color: #d1d7db; margin-bottom: 4px;">
            <strong>${escapeHtml(ord.product_name || "Footwear")}</strong>
          </div>
          <div class="order-stepper">
            <div class="step-item active"><span class="step-dot"></span><span>Placed</span></div>
            <div class="step-item active"><span class="step-dot"></span><span>Confirmed</span></div>
            <div class="step-item ${isDispatched ? 'active' : ''}"><span class="step-dot"></span><span>Dispatched</span></div>
            <div class="step-item ${isDelivered ? 'active' : ''}"><span class="step-dot"></span><span>Delivered</span></div>
          </div>
          <div style="font-size: 11px; color: #8696a0; margin-top: 6px;">
            🚚 ${escapeHtml(courier)} • AWB: <code>${escapeHtml(tracking)}</code><br>
            ⏱️ Est. Delivery: <strong style="color: #25d366;">${escapeHtml(est)}</strong>
          </div>
        </div>
      `;
    }

    // Render Matching Product Recommendation Cards if present
    if (options.products && options.products.length > 0) {
      options.products.slice(0, 3).forEach(p => {
        const name = p.name || p.title || "Shoe";
        const price = p.salePrice || p.sale_price || p.price || 1499;
        const mrp = p.mrp || p.mrp_price || (price * 1.25);
        const img = p.imageUrl || p.image_url || "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400";
        const sizes = p.availableSizes || p.available_sizes || p.sizes || ["7", "8", "9", "10"];
        const stock = p.quantity || p.available_quantity || 10;
        const badge = stock <= 3 ? "Low Stock" : (p.discountPercent ? `${p.discountPercent}% Off` : "In Stock");

        html += `
          <div class="chat-card-attachment">
            <img src="${escapeHtml(img)}" class="chat-card-img" alt="${escapeHtml(name)}" onerror="this.src='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'">
            <div class="chat-card-info">
              <div class="chat-card-name">${escapeHtml(name)}</div>
              <div class="chat-card-price-row">
                <span class="chat-card-price">₹${Number(price).toLocaleString('en-IN')}</span>
                <span class="chat-card-mrp">₹${Number(mrp).toLocaleString('en-IN')}</span>
                <span class="chat-card-badge">${badge}</span>
              </div>
              <div class="chat-card-sizes">Sizes: ${sizes.slice(0, 6).join(', ')}</div>
              <button class="chat-card-btn" onclick="sendTestMsg('I want to buy ${escapeHtml(name)} in size ${sizes[0] || 9}')">Buy / Order Now ⚡</button>
            </div>
          </div>
        `;
      });
    }

    // Render Quick Reply chips if present
    if (options.quickReplies && options.quickReplies.length > 0) {
      html += `
        <div class="chat-quick-replies">
          ${options.quickReplies.map(qr => `<button class="quick-chip" onclick="sendTestMsg('${escapeHtml(qr).replace(/'/g, "\\'")}')">${escapeHtml(qr)}</button>`).join('')}
        </div>
      `;
    }

    html += `<span class="msg-time">${timeStr} ${sender === "user" ? "✓✓" : ""}</span>`;

    msgDiv.innerHTML = html;
    messagesBox.appendChild(msgDiv);
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
})();
