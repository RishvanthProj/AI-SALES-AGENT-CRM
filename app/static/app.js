/**
 * Starboyz Footwear — Professional CRM Web Application & API Client Layer
 * Real-time interconnected SaaS command center grounded in FastAPI and Cloud Firestore.
 */

// =============================================================================
// 1. Centralized API Client Layer
// =============================================================================
const crmApi = {
  baseUrl: '/api/crm',

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const defaultHeaders = { 'Content-Type': 'application/json' };
    try {
      const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...options.headers }
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Request failed with status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Dashboard & Analytics
  getDashboard(timeRange = '30d') {
    return this.request(`/dashboard?time_range=${timeRange}`);
  },
  getAnalytics(timeRange = '30d') {
    return this.request(`/analytics?time_range=${timeRange}`);
  },
  getHealth() {
    return this.request('/health');
  },
  reseed() {
    return this.request('/seed', { method: 'POST' });
  },

  // Leads & Pipeline
  getLeads(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/leads?${query}`);
  },
  getLead360(leadId) {
    return this.request(`/leads/${encodeURIComponent(leadId)}`);
  },
  updateLeadStage(leadId, stage, reason = '') {
    return this.request(`/leads/${encodeURIComponent(leadId)}/stage`, {
      method: 'POST',
      body: JSON.stringify({ lead_id: leadId, stage, reason, business_id: 'stridehub-shoes' })
    });
  },
  bulkUpdateLeads(payload) {
    return this.request('/leads/bulk', {
      method: 'POST',
      body: JSON.stringify({ ...payload, business_id: 'stridehub-shoes' })
    });
  },
  getPipeline() {
    return this.request('/pipeline');
  },

  // Customers & Customer 360
  getCustomers(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/customers?${query}`);
  },
  getCustomer360(customerId) {
    return this.request(`/customers/${encodeURIComponent(customerId)}`);
  },

  // Conversations & Transcripts
  getConversations() {
    return this.request('/conversations');
  },
  getTranscript(customerId) {
    return this.request(`/conversations/${encodeURIComponent(customerId)}`);
  },

  // Products & Inventory
  getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/products?${query}`);
  },
  getProductDetail(productId) {
    return this.request(`/products/${encodeURIComponent(productId)}`);
  },
  saveProduct(product) {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(product)
    });
  },
  deleteProduct(productId) {
    return this.request(`/products/${encodeURIComponent(productId)}`, { method: 'DELETE' });
  },
  duplicateProduct(productId) {
    return this.request(`/products/${encodeURIComponent(productId)}/duplicate`, { method: 'POST' });
  },
  getInventoryOverview() {
    return this.request('/inventory');
  },
  adjustInventory(payload) {
    return this.request('/inventory/adjust', {
      method: 'POST',
      body: JSON.stringify({ ...payload, business_id: 'stridehub-shoes' })
    });
  },
  getStockMovements(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/inventory/movements?${query}`);
  },

  // Orders & Fulfillment
  getOrders(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/orders?${query}`);
  },
  getOrderDetail(orderId) {
    return this.request(`/orders/${encodeURIComponent(orderId)}`);
  },
  updateOrderStatus(orderId, status) {
    return this.request(`/orders/${encodeURIComponent(orderId)}/status`, {
      method: 'PUT',
      body: JSON.stringify({ order_id: orderId, status, business_id: 'stridehub-shoes' })
    });
  },

  // Quotes & Invoices
  getQuotes() {
    return this.request('/quotes');
  },
  createQuote(quote) {
    return this.request('/quotes', {
      method: 'POST',
      body: JSON.stringify(quote)
    });
  },
  updateQuoteStatus(quoteId, status) {
    return this.request(`/quotes/${encodeURIComponent(quoteId)}/status?status=${encodeURIComponent(status)}`, {
      method: 'PUT'
    });
  },

  // Tasks & Follow-ups
  getTasks(filterView = 'all') {
    return this.request(`/tasks?filter_view=${filterView}`);
  },
  createTask(task) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(task)
    });
  },
  updateTask(taskId, updates) {
    return this.request(`/tasks/${encodeURIComponent(taskId)}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  },
  deleteTask(taskId) {
    return this.request(`/tasks/${encodeURIComponent(taskId)}`, { method: 'DELETE' });
  },

  // Notes, Tags & Activity
  getNotes(entityType, entityId) {
    return this.request(`/notes?entity_type=${entityType}&entity_id=${entityId}`);
  },
  addNote(payload) {
    return this.request('/notes', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  getTags() {
    return this.request('/tags');
  },
  createTag(payload) {
    return this.request('/tags', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },
  deleteTag(tagId) {
    return this.request(`/tags/${encodeURIComponent(tagId)}`, { method: 'DELETE' });
  },
  getActivity(limit = 40) {
    return this.request(`/activity?limit=${limit}`);
  },
  search(query) {
    return this.request(`/search?query=${encodeURIComponent(query)}`);
  },
  getSettings() {
    return this.request('/settings');
  },
  saveSettings(settings) {
    return this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(settings)
    });
  }
};

// =============================================================================
// 2. CRM Application State & Core Logic
// =============================================================================
class CrmApplication {
  constructor() {
    this.currentView = 'dashboard';
    this.timeRange = '30d';
    this.activeCustomerId = null;
    this.activeLeadId = null;
    this.selectedLeads = new Set();
    this.pollingInterval = null;
    this.catalogProducts = [];
  }

  init() {
    this.bindNavigation();
    this.bindModals();
    this.bindForms();
    this.bindSearch();
    this.bindModeSwitcher();
    this.startBackgroundSync();
    this.switchView('dashboard');
  }

  // Toast Helper
  showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast show toast-${type}`;
    setTimeout(() => {
      toast.className = 'toast';
    }, 3200);
  }

  // Navigation Handlers
  bindNavigation() {
    document.querySelectorAll('.crm-nav-item').forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.getAttribute('data-view');
        this.switchView(view);
      });
    });

    const sidebarToggle = document.getElementById('sidebar-toggle-btn');
    const sidebar = document.getElementById('crm-sidebar');
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
      });
    }
  }

  bindModeSwitcher() {
    const crmBtn = document.getElementById('mode-crm-btn');
    const storeBtn = document.getElementById('mode-store-btn');
    const chatBtn = document.getElementById('mode-chat-btn');

    const crmView = document.getElementById('crm-view');
    const storeView = document.getElementById('storefront-view');
    const chatView = document.getElementById('chat-view');

    crmBtn?.addEventListener('click', () => {
      crmBtn.classList.add('active');
      storeBtn?.classList.remove('active');
      chatBtn?.classList.remove('active');
      crmView.style.display = 'block';
      if (storeView) storeView.style.display = 'none';
      if (chatView) chatView.style.display = 'none';
      this.refreshCurrentView();
    });

    storeBtn?.addEventListener('click', () => {
      storeBtn.classList.add('active');
      crmBtn?.classList.remove('active');
      chatBtn?.classList.remove('active');
      if (crmView) crmView.style.display = 'none';
      if (storeView) storeView.style.display = 'block';
      if (chatView) chatView.style.display = 'none';
      this.loadStorefrontProducts();
    });

    chatBtn?.addEventListener('click', () => {
      chatBtn.classList.add('active');
      crmBtn?.classList.remove('active');
      storeBtn?.classList.remove('active');
      if (crmView) crmView.style.display = 'none';
      if (storeView) storeView.style.display = 'none';
      if (chatView) chatView.style.display = 'block';
      this.initLiveChat();
    });
  }

  switchView(viewName, params = {}) {
    this.currentView = viewName;
    document.querySelectorAll('.crm-nav-item').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
    });

    document.querySelectorAll('.crm-pane').forEach(pane => {
      pane.classList.remove('active');
    });

    const targetPane = document.getElementById(`pane-${viewName}`);
    if (targetPane) targetPane.classList.add('active');

    this.updateViewHeader(viewName);
    this.refreshCurrentView(params);
  }

  updateViewHeader(viewName) {
    const titleEl = document.getElementById('crm-view-title');
    const subtitleEl = document.getElementById('crm-view-subtitle');
    const actionsEl = document.getElementById('crm-top-actions');

    const headers = {
      dashboard: { title: 'Dashboard Overview', sub: 'Real-time sales performance, qualification metrics & inventory overview.' },
      inbox: { title: 'Live Conversations & Inbox', sub: 'Monitor unscripted terminal chat & customer WhatsApp messages.' },
      leads: { title: 'Leads Management', sub: 'Filter, qualify, score, and transition buyer leads through sales stages.' },
      customers: { title: 'Customer 360 Database', sub: 'Lifetime order values, addresses, preferences, and activity history.' },
      pipeline: { title: 'Sales Funnel Pipeline', sub: 'Kanban view of leads moving from Enquired to Converted.' },
      products: { title: 'Footwear Catalog', sub: 'Authoritative shoes, variants, materials, sizes, and pricing.' },
      inventory: { title: 'Inventory & Stock Management', sub: 'Live warehouse stock, reorder levels, and atomic updates.' },
      movements: { title: 'Stock Movements Audit Log', sub: 'Historical audit trail of all inventory deductions and restocks.' },
      orders: { title: 'Orders & Fulfillment', sub: 'Courier tracking, COD/UPI status, delivery timelines.' },
      quotes: { title: 'Quotes & Invoices', sub: 'Generate, manage, and convert custom pricing quotes to orders.' },
      tasks: { title: 'Tasks & Sales Follow-ups', sub: 'Scheduled customer follow-ups and priority action items.' },
      tags: { title: 'Tags & Segmentation', sub: 'Categorize customers and leads with custom colored badges.' },
      activity: { title: 'System-Wide Activity Stream', sub: 'Audit timeline of all operations across the platform.' },
      analytics: { title: 'Deep Analytics & Conversion Reports', sub: 'Cohort retention, drop-offs, and product demand metrics.' },
      settings: { title: 'Store Settings & Policies', sub: 'Configure business profile, operating hours, and return rules.' },
      health: { title: 'System Health & Diagnostics', sub: 'Real-time status of FastAPI, Cloud Firestore, and Gemini.' }
    };

    const cur = headers[viewName] || { title: 'CRM Platform', sub: '' };
    if (titleEl) titleEl.textContent = cur.title;
    if (subtitleEl) subtitleEl.textContent = cur.sub;

    if (actionsEl) {
      if (viewName === 'dashboard') {
        actionsEl.innerHTML = `
          <select class="select-input" id="dash-range-select" onchange="crmApp.setTimeRange(this.value)">
            <option value="7d" ${this.timeRange === '7d' ? 'selected' : ''}>7 Days</option>
            <option value="30d" ${this.timeRange === '30d' ? 'selected' : ''}>30 Days</option>
            <option value="90d" ${this.timeRange === '90d' ? 'selected' : ''}>90 Days</option>
          </select>
          <button class="btn btn-secondary" onclick="crmApp.refreshCurrentView()"><span>🔄</span> Refresh</button>
        `;
      } else {
        actionsEl.innerHTML = `
          <button class="btn btn-secondary" onclick="crmApp.refreshCurrentView()"><span>🔄</span> Refresh</button>
        `;
      }
    }
  }

  setTimeRange(range) {
    this.timeRange = range;
    this.refreshCurrentView();
  }

  refreshCurrentView(params = {}) {
    switch (this.currentView) {
      case 'dashboard':
        this.loadDashboard();
        break;
      case 'inbox':
        this.loadInbox();
        break;
      case 'leads':
        this.loadLeads(params);
        break;
      case 'customers':
        this.loadCustomers(params);
        break;
      case 'pipeline':
        this.loadPipeline();
        break;
      case 'products':
        this.loadProducts(params);
        break;
      case 'inventory':
        this.loadInventory();
        break;
      case 'movements':
        this.loadMovements(params);
        break;
      case 'orders':
        this.loadOrders(params);
        break;
      case 'quotes':
        this.loadQuotes();
        break;
      case 'tasks':
        this.loadTasks(params.filterView || 'all');
        break;
      case 'tags':
        this.loadTags();
        break;
      case 'activity':
        this.loadActivity();
        break;
      case 'analytics':
        this.loadAnalytics();
        break;
      case 'settings':
        this.loadSettings();
        break;
      case 'health':
        this.loadHealth();
        break;
    }
  }

  startBackgroundSync() {
    if (this.pollingInterval) clearInterval(this.pollingInterval);
    // Background polling every 4 seconds to reflect terminal chat actions live
    this.pollingInterval = setInterval(() => {
      if (this.currentView === 'dashboard') {
        this.loadDashboard(false);
      } else if (this.currentView === 'inbox' && this.activeCustomerId) {
        this.loadTranscript(this.activeCustomerId, false);
      } else if (this.currentView === 'pipeline') {
        this.loadPipeline(false);
      }
    }, 4000);
  }

  // ===========================================================================
  // 3. View Loaders
  // ===========================================================================

  // 1. Dashboard
  async loadDashboard(showSkeletons = true) {
    try {
      const data = await crmApi.getDashboard(this.timeRange);
      const kpis = data.kpis || {};
      const sec = data.secondary || {};
      const charts = data.charts || {};

      // Populate Top KPIs
      this.setText('kpi-total-leads', kpis.total_leads || 0);
      this.setText('kpi-new-leads-trend', `${kpis.new_leads || 0} New recently`);
      this.setText('kpi-qualified-leads', kpis.qualified_leads || 0);
      this.setText('kpi-active-conversations', kpis.active_conversations || 0);
      this.setText('kpi-total-orders', kpis.total_orders || 0);
      this.setText('kpi-pending-orders-trend', `${sec.pending_orders || 0} In fulfillment`);
      this.setText('kpi-total-revenue', `₹${(kpis.total_revenue || 0).toLocaleString('en-IN')}`);
      this.setText('kpi-conversion-rate', `${kpis.conversion_rate || 0}%`);
      this.setText('kpi-aov', `₹${(kpis.average_order_value || 0).toLocaleString('en-IN')}`);
      this.setText('kpi-human-handoff', sec.human_handoff || 0);

      // Populate Secondary Indicators
      this.setText('sec-nurture', sec.nurture_leads || 0);
      this.setText('sec-pending-orders', sec.pending_orders || 0);
      this.setText('sec-low-stock', sec.low_stock || 0);
      this.setText('sec-out-stock', sec.out_of_stock || 0);
      this.setText('sec-followups', sec.followups_due || 0);

      // Update sidebar badge pills
      this.setText('inbox-badge-count', kpis.active_conversations || 0);
      this.setText('leads-badge-count', kpis.total_leads || 0);
      this.setText('orders-badge-count', kpis.total_orders || 0);
      this.setText('tasks-badge-count', sec.followups_due || 0);

      const lowStockBadge = document.getElementById('low-stock-badge-count');
      if (lowStockBadge) {
        if (sec.low_stock > 0) {
          lowStockBadge.style.display = 'inline-block';
          lowStockBadge.textContent = sec.low_stock;
        } else {
          lowStockBadge.style.display = 'none';
        }
      }

      // Handoff Banner
      const banner = document.getElementById('crm-handoff-banner');
      if (banner) {
        if (sec.human_handoff > 0) {
          banner.style.display = 'flex';
          this.setText('handoff-banner-text', `${sec.human_handoff} customer(s) requested human sales consultation.`);
        } else {
          banner.style.display = 'none';
        }
      }

      // Render Charts
      this.renderSvgTrendChart('dash-revenue-chart', charts.revenue_trend || [], '₹');
      this.renderSvgTrendChart('dash-leads-chart', charts.leads_trend || [], '');
      this.renderFunnelChart('dash-funnel-chart', charts.funnel || {});
      this.renderTopProductsList('dash-top-products-list', charts.top_products || []);

    } catch (err) {
      console.error('Failed loading dashboard:', err);
    }
  }

  // 2. Inbox & Conversations
  async loadInbox() {
    try {
      const conversations = await crmApi.getConversations();
      const listEl = document.getElementById('inbox-conversations-list');
      if (!listEl) return;

      if (!conversations.length) {
        listEl.innerHTML = '<div class="empty-state">No conversations recorded yet. Start terminal_chat.py to interact with customer.</div>';
        return;
      }

      listEl.innerHTML = conversations.map(c => {
        const isHandoff = c.stage === 'human_handoff' || c.requires_handoff;
        const timeAgo = this.formatTimeAgo(c.timestamp);
        return `
          <div class="conv-item ${this.activeCustomerId === c.customer_id ? 'active' : ''}" onclick="crmApp.selectConversation('${c.customer_id}', '${escape(c.customer_name)}')">
            <div class="conv-header">
              <span class="conv-name">${this.escapeHtml(c.customer_name)}</span>
              <span class="conv-time">${timeAgo}</span>
            </div>
            <div class="conv-preview">${this.escapeHtml(c.last_message || 'Start of conversation')}</div>
            <div style="display: flex; gap: 6px; margin-top: 6px;">
              <span class="status-badge status-${c.stage}">${c.stage}</span>
              <span class="score-pill score-${c.score >= 70 ? 'high' : c.score >= 40 ? 'mid' : 'low'}">${c.score:.0f} pts</span>
              ${isHandoff ? '<span class="status-badge status-human_handoff">⚠️ Handoff</span>' : ''}
            </div>
          </div>
        `;
      }).join('');

      if (!this.activeCustomerId && conversations.length > 0) {
        this.selectConversation(conversations[0].customer_id, conversations[0].customer_name);
      }
    } catch (err) {
      console.error('Failed loading inbox:', err);
    }
  }

  async selectConversation(customerId, customerName) {
    this.activeCustomerId = customerId;
    this.setText('transcript-name', unescape(customerName));
    this.setText('transcript-phone', customerId);

    // Update active class in list
    document.querySelectorAll('.conv-item').forEach(el => {
      el.classList.toggle('active', el.querySelector('.conv-name')?.textContent === unescape(customerName));
    });

    await this.loadTranscript(customerId);
    await this.loadInboxCustomerSidebar(customerId);
  }

  async loadTranscript(customerId, scroll = true) {
    try {
      const messages = await crmApi.getTranscript(customerId);
      const box = document.getElementById('transcript-messages-box');
      if (!box) return;

      if (!messages.length) {
        box.innerHTML = '<div class="empty-state">No messages in transcript.</div>';
        return;
      }

      box.innerHTML = messages.map(m => {
        const isUser = m.role === 'user';
        const timeStr = new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        return `
          <div class="chat-bubble ${isUser ? 'user' : 'assistant'}">
            <div class="bubble-content">${this.escapeHtml(m.content)}</div>
            <span class="bubble-time">${timeStr} &bull; ${isUser ? 'Customer' : 'AI Agent'}</span>
          </div>
        `;
      }).join('');

      if (scroll) box.scrollTop = box.scrollHeight;
    } catch (err) {
      console.error('Failed loading transcript:', err);
    }
  }

  async loadInboxCustomerSidebar(customerId) {
    try {
      const detailsEl = document.getElementById('inbox-cust-details');
      if (!detailsEl) return;

      const c360 = await crmApi.getCustomer360(customerId);
      const cust = c360.customer || {};
      const lead = c360.lead || {};

      detailsEl.innerHTML = `
        <div style="margin-bottom: 12px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase;">Contact Number</div>
          <div style="font-weight: 700;">${cust.phone_number || customerId}</div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase;">Lead Stage & Score</div>
          <div style="display: flex; gap: 6px; margin-top: 4px;">
            <span class="status-badge status-${lead.stage || 'enquired'}">${lead.stage || 'Enquired'}</span>
            <span class="score-pill score-${(lead.qualification_score || 0) >= 70 ? 'high' : 'mid'}">${lead.qualification_score || 0} / 100</span>
          </div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase;">Budget Signal</div>
          <div>${lead.budget_signal || 'Not specified'}</div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase;">Timeline</div>
          <div>${lead.timeline_signal || 'Immediate'}</div>
        </div>
        <div style="margin-bottom: 14px;">
          <div style="font-size: 11px; color: var(--text-dim); text-transform: uppercase;">Interested Footwear</div>
          <div>${(lead.interested_product_names && lead.interested_product_names.join(', ')) || 'Shoe inquiries'}</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          <button class="btn btn-sm btn-primary" onclick="crmApp.openLeadDetailModal('${customerId}')">Open Full Lead 360</button>
          <button class="btn btn-sm btn-secondary" onclick="crmApp.openCreateQuoteModal('${customerId}', '${cust.name || 'Customer'}')">Create Quote</button>
        </div>
      `;
    } catch (err) {
      console.error('Failed loading inbox customer sidebar:', err);
    }
  }

  // 3. Leads Management
  async loadLeads(params = {}) {
    try {
      const stageFilter = document.getElementById('leads-stage-filter')?.value || params.stage || 'all';
      const scoreFilter = document.getElementById('leads-score-filter')?.value || '0';
      const search = document.getElementById('leads-search-input')?.value || params.search || '';

      const queryParams = { stage: stageFilter, search };
      if (scoreFilter !== '0') queryParams.min_score = scoreFilter;

      const leads = await crmApi.getLeads(queryParams);
      const tbody = document.getElementById('leads-tbody');
      if (!tbody) return;

      if (!leads.length) {
        tbody.innerHTML = '<tr><td colspan="11" class="empty-state">No leads match your search criteria.</td></tr>';
        return;
      }

      tbody.innerHTML = leads.map(l => {
        const score = l.qualification_score || 0;
        const scoreClass = score >= 70 ? 'high' : score >= 40 ? 'mid' : 'low';
        const shoesStr = (l.interested_product_names && l.interested_product_names.length) ? l.interested_product_names.join(', ') : (l.need_summary || '--');
        const isChecked = this.selectedLeads.has(l.lead_id);

        return `
          <tr>
            <td><input type="checkbox" ${isChecked ? 'checked' : ''} onchange="crmApp.toggleLeadSelection('${l.lead_id}')"></td>
            <td><strong>${this.escapeHtml(l.name || 'Customer')}</strong></td>
            <td><code>${this.escapeHtml(l.contact_number)}</code></td>
            <td><span class="status-badge status-${l.stage}">${l.stage}</span></td>
            <td><span class="score-pill score-${scoreClass}">${score:.0f} pts</span></td>
            <td>${this.escapeHtml(l.budget_signal || '--')}</td>
            <td>${this.escapeHtml(l.timeline_signal || '--')}</td>
            <td><span style="font-size: 12px;">${this.escapeHtml(shoesStr)}</span></td>
            <td><span class="status-badge">${l.source}</span></td>
            <td>${this.formatTimeAgo(l.updated_at || l.created_at)}</td>
            <td>
              <button class="btn btn-sm btn-secondary" onclick="crmApp.openLeadDetailModal('${l.lead_id}')">View 360</button>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading leads:', err);
    }
  }

  toggleLeadSelection(leadId) {
    if (this.selectedLeads.has(leadId)) {
      this.selectedLeads.delete(leadId);
    } else {
      this.selectedLeads.add(leadId);
    }
    const bar = document.getElementById('leads-bulk-bar');
    const countEl = document.getElementById('leads-selected-count');
    if (bar && countEl) {
      if (this.selectedLeads.size > 0) {
        bar.style.display = 'flex';
        countEl.textContent = `${this.selectedLeads.size} lead(s) selected`;
      } else {
        bar.style.display = 'none';
      }
    }
  }

  async bulkMoveStage(stage) {
    if (!this.selectedLeads.size) return;
    try {
      await crmApi.bulkUpdateLeads({
        lead_ids: Array.from(this.selectedLeads),
        stage
      });
      this.showToast(`Updated ${this.selectedLeads.size} leads to ${stage.toUpperCase()}`, 'success');
      this.selectedLeads.clear();
      document.getElementById('leads-bulk-bar').style.display = 'none';
      this.loadLeads();
    } catch (err) {
      this.showToast('Bulk update failed', 'danger');
    }
  }

  // 4. Customers Management
  async loadCustomers(params = {}) {
    try {
      const typeFilter = document.getElementById('customers-type-filter')?.value || 'all';
      const search = document.getElementById('customers-search-input')?.value || '';

      const customers = await crmApi.getCustomers({ customer_type: typeFilter, search });
      const tbody = document.getElementById('customers-tbody');
      if (!tbody) return;

      if (!customers.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No customers found.</td></tr>';
        return;
      }

      tbody.innerHTML = customers.map(c => {
        const spentStr = `₹${(c.total_spent || 0).toLocaleString('en-IN')}`;
        const aovStr = `₹${(c.average_order_value || 0).toLocaleString('en-IN')}`;
        const loc = [c.city, c.state].filter(Boolean).join(', ') || 'India';
        return `
          <tr>
            <td><strong>${this.escapeHtml(c.name || 'Customer')}</strong></td>
            <td><code>${this.escapeHtml(c.phone_number)}</code></td>
            <td>${this.escapeHtml(c.email || '--')}</td>
            <td>${this.escapeHtml(loc)}</td>
            <td><strong>${c.total_orders || 0}</strong></td>
            <td><strong style="color: var(--success);">${spentStr}</strong></td>
            <td>${aovStr}</td>
            <td><span class="status-badge status-${c.customer_type}">${c.customer_type}</span></td>
            <td>${(c.tags || []).map(t => `<span class="score-pill score-high" style="font-size:10px;">${t}</span>`).join(' ')}</td>
            <td>
              <button class="btn btn-sm btn-secondary" onclick="crmApp.openCustomerDetailModal('${c.id}')">Profile 360</button>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading customers:', err);
    }
  }

  // 5. Funnel Pipeline (Kanban)
  async loadPipeline(showLoading = true) {
    try {
      const kanban = await crmApi.getPipeline();
      const board = document.getElementById('kanban-board');
      if (!board) return;

      const stages = [
        { key: 'enquired', label: '1. Enquired', icon: '⚡' },
        { key: 'engaged', label: '2. Engaged', icon: '💬' },
        { key: 'quoted', label: '3. Quoted', icon: '📑' },
        { key: 'nurture', label: '4. Nurture', icon: '🌱' },
        { key: 'human_handoff', label: '5. Human Handoff', icon: '⚠️' },
        { key: 'converted', label: '6. Converted', icon: '🎉' }
      ];

      board.innerHTML = stages.map(s => {
        const cards = kanban[s.key] || [];
        return `
          <div class="kanban-column" data-stage="${s.key}">
            <div class="kanban-col-header">
              <span class="kanban-col-title">${s.icon} ${s.label}</span>
              <span class="kanban-col-count">${cards.length}</span>
            </div>
            <div class="kanban-col-cards">
              ${cards.length ? cards.map(c => this.renderKanbanCard(c)).join('') : '<div class="empty-state" style="padding: 20px 0;">No leads in stage.</div>'}
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading pipeline:', err);
    }
  }

  renderKanbanCard(card) {
    const score = card.qualification_score || 0;
    const scoreClass = score >= 70 ? 'high' : score >= 40 ? 'mid' : 'low';
    const shoeName = (card.interested_product_names && card.interested_product_names[0]) || card.need_summary || 'Shoe Interest';

    return `
      <div class="kanban-card" onclick="crmApp.openLeadDetailModal('${card.lead_id}')">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
          <strong style="font-size: 13px;">${this.escapeHtml(card.name || 'Customer')}</strong>
          <span class="score-pill score-${scoreClass}">${score:.0f}</span>
        </div>
        <div style="font-size: 11px; color: var(--text-dim); margin-bottom: 6px;">${this.escapeHtml(card.contact_number)}</div>
        <div style="font-size: 12px; color: var(--primary); font-weight: 600; margin-bottom: 8px;">${this.escapeHtml(shoeName)}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: var(--text-dim);">
          <span>${card.budget_signal || 'No budget'}</span>
          <span>${this.formatTimeAgo(card.updated_at || card.created_at)}</span>
        </div>
      </div>
    `;
  }

  // 6. Product Catalog
  async loadProducts(params = {}) {
    try {
      const category = document.getElementById('products-category-filter')?.value || 'all';
      const stockStatus = document.getElementById('products-stock-filter')?.value || 'all';
      const search = document.getElementById('products-search-input')?.value || '';

      const products = await crmApi.getProducts({ category, stock_status: stockStatus, search });
      this.catalogProducts = products;
      const tbody = document.getElementById('products-tbody');
      if (!tbody) return;

      if (!products.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No footwear products match filters.</td></tr>';
        return;
      }

      tbody.innerHTML = products.map(p => {
        const sizesStr = (p.availableSizes || []).join(', ');
        return `
          <tr>
            <td>
              <div style="display: flex; align-items: center; gap: 10px;">
                <img src="${p.imageUrl || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=100'}" style="width: 36px; height: 36px; border-radius: 6px; object-fit: cover;">
                <div>
                  <strong>${this.escapeHtml(p.name)}</strong>
                  <div style="font-size: 10px; color: var(--text-dim);">SKU: ${p.sku}</div>
                </div>
              </div>
            </td>
            <td><span class="status-badge">${p.category}</span></td>
            <td><strong>₹${(p.price || 0).toLocaleString('en-IN')}</strong> <span style="font-size: 11px; color: var(--text-dim); text-decoration: line-through;">₹${(p.mrp || 0).toLocaleString('en-IN')}</span></td>
            <td><strong>${p.quantity} units</strong></td>
            <td><span class="status-badge status-${p.stockStatus}">${p.stockStatus.replace('_', ' ')}</span></td>
            <td><span style="font-size: 11px;">[${sizesStr}]</span></td>
            <td>⭐ ${p.rating || 4.8}</td>
            <td>
              <button class="btn btn-sm btn-secondary" onclick="crmApp.openAdjustStockModal('${p.id}', '${escape(p.name)}')">⚡ Stock &plusmn;</button>
            </td>
            <td>
              <div style="display: flex; gap: 4px;">
                <button class="btn btn-sm btn-secondary" onclick="crmApp.openProductDetailModal('${p.id}')">Detail</button>
                <button class="btn btn-sm btn-secondary" onclick="crmApp.duplicateProduct('${p.id}')">Clone</button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading products:', err);
    }
  }

  // 7. Inventory Overview
  async loadInventory() {
    try {
      const data = await crmApi.getInventoryOverview();
      this.setText('inv-total-skus', data.total_items || 0);
      this.setText('inv-in-stock', data.in_stock_count || 0);
      this.setText('inv-low-stock', data.low_stock_count || 0);
      this.setText('inv-out-stock', data.out_of_stock_count || 0);

      const tbody = document.getElementById('inventory-tbody');
      if (!tbody) return;

      const prods = data.products || [];
      tbody.innerHTML = prods.map(p => `
        <tr>
          <td><strong>${this.escapeHtml(p.name)}</strong></td>
          <td><code>${p.sku}</code></td>
          <td>Central Bengaluru Warehouse</td>
          <td><strong style="font-size: 15px;">${p.quantity} units</strong></td>
          <td>${p.lowStockThreshold || 5} units</td>
          <td><span class="status-badge status-${p.stockStatus}">${p.stockStatus}</span></td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="crmApp.openAdjustStockModal('${p.id}', '${escape(p.name)}')">Adjust Stock</button>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      console.error('Failed loading inventory:', err);
    }
  }

  // 8. Stock Movements Audit Log
  async loadMovements(params = {}) {
    try {
      const search = document.getElementById('movements-search-input')?.value || '';
      const movements = await crmApi.getStockMovements({ search });
      const tbody = document.getElementById('movements-tbody');
      if (!tbody) return;

      if (!movements.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No stock movements recorded yet.</td></tr>';
        return;
      }

      tbody.innerHTML = movements.map(m => {
        const sign = m.quantity_change > 0 ? '+' : '';
        const deltaColor = m.quantity_change > 0 ? 'var(--success)' : 'var(--danger)';
        return `
          <tr>
            <td><code>${m.movement_id}</code></td>
            <td>${new Date(m.created_at).toLocaleString()}</td>
            <td><strong>${this.escapeHtml(m.product_name)}</strong></td>
            <td><strong style="color: ${deltaColor}; font-size: 14px;">${sign}${m.quantity_change}</strong></td>
            <td>${m.previous_quantity}</td>
            <td><strong>${m.new_quantity}</strong></td>
            <td><span class="status-badge">${m.reason}</span></td>
            <td>${m.performed_by}</td>
            <td><code>${m.reference_id || '--'}</code></td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading stock movements:', err);
    }
  }

  // 9. Orders & Fulfillment
  async loadOrders(params = {}) {
    try {
      const statusFilter = document.getElementById('orders-status-filter')?.value || 'all';
      const search = document.getElementById('orders-search-input')?.value || '';

      const orders = await crmApi.getOrders({ status: statusFilter, search });
      const tbody = document.getElementById('orders-tbody');
      if (!tbody) return;

      if (!orders.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty-state">No orders found.</td></tr>';
        return;
      }

      tbody.innerHTML = orders.map(o => {
        const amtStr = `₹${(o.amount || 0).toLocaleString('en-IN')}`;
        return `
          <tr>
            <td><strong>#${o.order_id}</strong></td>
            <td>${this.escapeHtml(o.customer_name)}</td>
            <td>${this.escapeHtml(o.product_name || 'Footwear Item')}</td>
            <td><strong>${amtStr}</strong></td>
            <td>${o.payment_method}</td>
            <td><span class="status-badge status-${o.payment_status === 'paid' ? 'converted' : 'quoted'}">${o.payment_status}</span></td>
            <td><span class="status-badge status-${o.status}">${o.status}</span></td>
            <td>${o.courier_partner} (<code>${o.tracking_id}</code>)</td>
            <td>${new Date(o.order_date).toLocaleDateString()}</td>
            <td>
              <select class="select-input" style="padding: 4px; font-size: 11px;" onchange="crmApp.updateOrderStatus('${o.order_id}', this.value)">
                <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
                <option value="confirmed" ${o.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                <option value="packed" ${o.status === 'packed' ? 'selected' : ''}>Packed</option>
                <option value="dispatched" ${o.status === 'dispatched' ? 'selected' : ''}>Dispatched</option>
                <option value="out_for_delivery" ${o.status === 'out_for_delivery' ? 'selected' : ''}>Out for Delivery</option>
                <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
                <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
              </select>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading orders:', err);
    }
  }

  async updateOrderStatus(orderId, newStatus) {
    try {
      await crmApi.updateOrderStatus(orderId, newStatus);
      this.showToast(`Order #${orderId} marked as ${newStatus.toUpperCase()}`, 'success');
      this.loadOrders();
    } catch (err) {
      this.showToast('Failed to update status', 'danger');
    }
  }

  // 10. Quotes & Invoices
  async loadQuotes() {
    try {
      const quotes = await crmApi.getQuotes();
      const tbody = document.getElementById('quotes-tbody');
      if (!tbody) return;

      if (!quotes.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No quotes generated yet.</td></tr>';
        return;
      }

      tbody.innerHTML = quotes.map(q => {
        const amtStr = `₹${(q.total_amount || 0).toLocaleString('en-IN')}`;
        return `
          <tr>
            <td><strong>#${q.quote_id}</strong></td>
            <td>${this.escapeHtml(q.customer_name)}</td>
            <td><code>${q.contact_number}</code></td>
            <td><strong style="color: var(--primary);">${amtStr}</strong></td>
            <td><span class="status-badge status-${q.status}">${q.status}</span></td>
            <td><code>${q.invoice_id || '--'}</code></td>
            <td>${q.valid_until || '7 Days'}</td>
            <td>${new Date(q.created_at).toLocaleDateString()}</td>
            <td>
              <button class="btn btn-sm btn-primary" onclick="crmApp.acceptQuote('${q.quote_id}')">Accept & Invoice</button>
            </td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading quotes:', err);
    }
  }

  async acceptQuote(quoteId) {
    try {
      await crmApi.updateQuoteStatus(quoteId, 'accepted');
      this.showToast(`Quote #${quoteId} accepted and invoice generated!`, 'success');
      this.loadQuotes();
    } catch (err) {
      this.showToast('Failed accepting quote', 'danger');
    }
  }

  // 11. Tasks & Follow-ups
  async loadTasks(filterView = 'all') {
    try {
      const tasks = await crmApi.getTasks(filterView);
      const container = document.getElementById('tasks-container');
      if (!container) return;

      if (!tasks.length) {
        container.innerHTML = '<div class="empty-state">No follow-up tasks in this view.</div>';
        return;
      }

      container.innerHTML = tasks.map(t => {
        const isDone = t.status === 'completed';
        return `
          <div class="kpi-card" style="align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 12px;">
              <input type="checkbox" ${isDone ? 'checked' : ''} onchange="crmApp.toggleTaskComplete('${t.task_id}', this.checked)">
              <div>
                <strong style="font-size: 14px; text-decoration: ${isDone ? 'line-through' : 'none'};">${this.escapeHtml(t.title)}</strong>
                <div style="font-size: 11px; color: var(--text-dim); margin-top: 2px;">
                  Customer: <strong>${t.customer_name || 'General'}</strong> &bull; Due: ${t.due_date || 'Today'}
                </div>
              </div>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="status-badge status-${t.priority === 'urgent' ? 'human_handoff' : 'engaged'}">${t.priority}</span>
              <button class="icon-btn" onclick="crmApp.deleteTask('${t.task_id}')">🗑️</button>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      console.error('Failed loading tasks:', err);
    }
  }

  async toggleTaskComplete(taskId, completed) {
    try {
      await crmApi.updateTask(taskId, { status: completed ? 'completed' : 'pending' });
      this.showToast(completed ? 'Task completed!' : 'Task reopened', 'success');
      this.loadTasks();
    } catch (err) {
      this.showToast('Failed updating task', 'danger');
    }
  }

  async deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;
    try {
      await crmApi.deleteTask(taskId);
      this.showToast('Task removed', 'info');
      this.loadTasks();
    } catch (err) {
      this.showToast('Failed removing task', 'danger');
    }
  }

  // 12. Tags & Segments
  async loadTags() {
    try {
      const tags = await crmApi.getTags();
      const container = document.getElementById('tags-manager-container');
      if (!container) return;

      container.innerHTML = tags.map(t => `
        <div class="kpi-card" style="align-items: center; justify-content: space-between; border-left: 4px solid ${t.color};">
          <div>
            <strong>${this.escapeHtml(t.name)}</strong>
            <div style="font-size: 11px; color: var(--text-dim);">${t.category}</div>
          </div>
          <button class="btn btn-sm btn-secondary" onclick="crmApp.deleteTag('${t.tag_id}')">Delete</button>
        </div>
      `).join('');
    } catch (err) {
      console.error('Failed loading tags:', err);
    }
  }

  async deleteTag(tagId) {
    if (!confirm('Delete this tag?')) return;
    try {
      await crmApi.deleteTag(tagId);
      this.showToast('Tag deleted', 'info');
      this.loadTags();
    } catch (err) {
      this.showToast('Failed deleting tag', 'danger');
    }
  }

  // 13. Activity Timeline
  async loadActivity() {
    try {
      const acts = await crmApi.getActivity(50);
      const feed = document.getElementById('activity-feed-container');
      if (!feed) return;

      feed.innerHTML = acts.map(a => `
        <div style="padding: 12px 16px; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 8px; margin-bottom: 10px;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
            <strong>${this.escapeHtml(a.title)}</strong>
            <span style="font-size: 11px; color: var(--text-dim);">${new Date(a.created_at).toLocaleString()}</span>
          </div>
          <p style="font-size: 13px; color: var(--text-muted);">${this.escapeHtml(a.description)}</p>
          <div style="font-size: 10px; color: var(--text-dim); margin-top: 4px;">Source: ${a.source} &bull; Entity: ${a.entity_type}</div>
        </div>
      `).join('');
    } catch (err) {
      console.error('Failed loading activity feed:', err);
    }
  }

  // 14. Deep Analytics
  async loadAnalytics() {
    try {
      const data = await crmApi.getAnalytics(this.timeRange);
      this.renderCategoryBars('analytics-category-bars', data.category_sales || []);
      this.renderFunnelChart('analytics-funnel-bars', data.funnel || {});
    } catch (err) {
      console.error('Failed loading analytics:', err);
    }
  }

  // 15. Store Settings
  async loadSettings() {
    try {
      const settings = await crmApi.getSettings();
      const nameEl = document.getElementById('set-store-name');
      const addrEl = document.getElementById('set-store-address');
      const hoursEl = document.getElementById('set-store-hours');
      const shipEl = document.getElementById('set-store-shipping');
      const retEl = document.getElementById('set-store-return');
      const exEl = document.getElementById('set-store-exchange');

      if (nameEl) nameEl.value = settings.business_name || 'Starboyz';
      if (addrEl) addrEl.value = settings.address || '';
      if (hoursEl) hoursEl.value = settings.working_hours || '';
      if (shipEl) shipEl.value = settings.shipping_information || '';
      if (retEl) retEl.value = settings.return_refund_policy || '';
      if (exEl) exEl.value = settings.exchange_policy || '';
    } catch (err) {
      console.error('Failed loading settings:', err);
    }
  }

  // 16. Health Diagnostics
  async loadHealth() {
    try {
      const h = await crmApi.getHealth();
      console.log('Health:', h);
    } catch (err) {
      console.error('Failed loading health:', err);
    }
  }

  // ===========================================================================
  // 4. Modals & Detail Drawers
  // ===========================================================================
  bindModals() {
    document.querySelectorAll('.modal-close-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
      });
    });

    document.getElementById('open-add-lead-btn')?.addEventListener('click', () => {
      this.showToast('Type a message in terminal_chat.py to automatically create a grounded lead!', 'info');
    });

    document.getElementById('open-adjust-stock-modal-btn')?.addEventListener('click', () => {
      this.openAdjustStockModal();
    });

    document.getElementById('open-create-quote-btn')?.addEventListener('click', () => {
      this.openCreateQuoteModal();
    });

    document.getElementById('open-create-task-btn')?.addEventListener('click', () => {
      this.openModal('task-modal');
    });

    document.getElementById('open-create-tag-btn')?.addEventListener('click', () => {
      this.openModal('tag-modal');
    });
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  }

  async openLeadDetailModal(leadId) {
    try {
      const detail = await crmApi.getLead360(leadId);
      const lead = detail.lead || {};
      const customer = detail.customer || {};
      const convs = detail.conversations || [];
      const score = lead.qualification_score || 0;

      const modal = document.getElementById('lead-modal');
      const content = document.getElementById('lead-modal-content');
      if (!modal || !content) return;

      content.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px; margin-bottom: 20px;">
          <div>
            <h2 style="font-size: 20px;">${this.escapeHtml(customer.name || lead.name || 'Customer')}</h2>
            <div style="color: var(--text-muted); font-size: 13px;">${lead.contact_number} &bull; Source: <strong>${lead.source}</strong></div>
          </div>
          <div style="display: flex; gap: 10px; align-items: center;">
            <select class="select-input" onchange="crmApp.updateLeadStageFromModal('${lead.lead_id}', this.value)">
              <option value="enquired" ${lead.stage === 'enquired' ? 'selected' : ''}>Enquired</option>
              <option value="engaged" ${lead.stage === 'engaged' ? 'selected' : ''}>Engaged</option>
              <option value="quoted" ${lead.stage === 'quoted' ? 'selected' : ''}>Quoted</option>
              <option value="nurture" ${lead.stage === 'nurture' ? 'selected' : ''}>Nurture</option>
              <option value="human_handoff" ${lead.stage === 'human_handoff' ? 'selected' : ''}>Human Handoff</option>
              <option value="converted" ${lead.stage === 'converted' ? 'selected' : ''}>Converted</option>
            </select>
            <span class="score-pill score-${score >= 70 ? 'high' : 'mid'}" style="font-size: 14px; padding: 4px 12px;">${score:.0f} / 100</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div>
            <h4>Qualification Signals</h4>
            <div style="background: var(--bg-surface); padding: 14px; border-radius: 8px; margin-top: 8px; font-size: 13px;">
              <p><strong>Need:</strong> ${lead.need_summary || 'Shoe recommendation'}</p>
              <p style="margin-top: 6px;"><strong>Budget:</strong> ${lead.budget_signal || 'Not captured'}</p>
              <p style="margin-top: 6px;"><strong>Timeline:</strong> ${lead.timeline_signal || 'Immediate'}</p>
              <p style="margin-top: 6px;"><strong>Interested Shoes:</strong> ${(lead.interested_product_names || []).join(', ') || 'Viewing catalog'}</p>
            </div>
          </div>

          <div>
            <h4>Conversation Messages (${convs.length})</h4>
            <div style="background: var(--bg-surface); padding: 14px; border-radius: 8px; margin-top: 8px; max-height: 220px; overflow-y: auto;">
              ${convs.map(m => `
                <div style="margin-bottom: 8px; font-size: 12px;">
                  <strong>${m.role === 'user' ? 'Customer' : 'AI Agent'}:</strong> ${this.escapeHtml(m.content)}
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px;">
          <button class="btn btn-secondary" onclick="crmApp.closeModal('lead-modal')">Close</button>
          <button class="btn btn-primary" onclick="crmApp.openCreateQuoteModal('${lead.lead_id}', '${customer.name || 'Customer'}')">Create Quote</button>
        </div>
      `;

      this.openModal('lead-modal');
    } catch (err) {
      console.error('Failed opening lead detail:', err);
    }
  }

  async updateLeadStageFromModal(leadId, stage) {
    try {
      await crmApi.updateLeadStage(leadId, stage);
      this.showToast(`Lead moved to ${stage.toUpperCase()}`, 'success');
      this.loadLeads();
    } catch (err) {
      this.showToast('Stage update failed', 'danger');
    }
  }

  async openCustomerDetailModal(customerId) {
    try {
      const c360 = await crmApi.getCustomer360(customerId);
      const cust = c360.customer || {};
      const orders = c360.orders || [];

      const modal = document.getElementById('customer-modal');
      const content = document.getElementById('customer-modal-content');
      if (!modal || !content) return;

      content.innerHTML = `
        <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px; margin-bottom: 20px;">
          <h2 style="font-size: 20px;">${this.escapeHtml(cust.name || 'Customer')}</h2>
          <div style="color: var(--text-muted); font-size: 13px;">${cust.phone_number} &bull; ${cust.email || 'No email registered'}</div>
        </div>
        <div class="kpi-grid" style="margin-bottom: 20px;">
          <div class="kpi-card">
            <span class="kpi-icon">🛍️</span>
            <div><span class="kpi-label">Orders</span><div class="kpi-value">${cust.total_orders || 0}</div></div>
          </div>
          <div class="kpi-card">
            <span class="kpi-icon">💰</span>
            <div><span class="kpi-label">Total Spent</span><div class="kpi-value" style="color: var(--success);">₹${(cust.total_spent || 0).toLocaleString('en-IN')}</div></div>
          </div>
          <div class="kpi-card">
            <span class="kpi-icon">💎</span>
            <div><span class="kpi-label">AOV</span><div class="kpi-value">₹${(cust.average_order_value || 0).toLocaleString('en-IN')}</div></div>
          </div>
        </div>
        <h4>Order History (${orders.length})</h4>
        <div style="margin-top: 10px;">
          ${orders.map(o => `
            <div style="padding: 10px; background: var(--bg-surface); border-radius: 6px; margin-bottom: 6px; display: flex; justify-content: space-between;">
              <span><strong>#${o.order_id}</strong> &bull; ${o.product_name}</span>
              <strong style="color: var(--success);">₹${(o.amount || 0).toLocaleString('en-IN')}</strong>
            </div>
          `).join('')}
        </div>
      `;

      this.openModal('customer-modal');
    } catch (err) {
      console.error('Failed opening customer modal:', err);
    }
  }

  async openProductDetailModal(productId) {
    try {
      const data = await crmApi.getProductDetail(productId);
      const prod = data.product || {};
      const sales = data.sales || {};
      const movements = data.stock_movements || [];

      const modal = document.getElementById('product-modal');
      const content = document.getElementById('product-modal-content');
      if (!modal || !content) return;

      content.innerHTML = `
        <div style="display: flex; gap: 20px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 16px; margin-bottom: 20px;">
          <img src="${prod.imageUrl || 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200'}" style="width: 100px; height: 100px; border-radius: 8px; object-fit: cover;">
          <div>
            <h2 style="font-size: 20px;">${this.escapeHtml(prod.name)}</h2>
            <div style="color: var(--text-muted); font-size: 13px;">SKU: <strong>${prod.sku}</strong> &bull; Category: <strong>${prod.category}</strong></div>
            <div style="margin-top: 8px; font-size: 18px; font-weight: 800; color: var(--primary);">
              ₹${(prod.price || 0).toLocaleString('en-IN')} <span style="font-size: 13px; color: var(--text-dim); text-decoration: line-through;">MRP ₹${(prod.mrp || 0).toLocaleString('en-IN')}</span>
            </div>
          </div>
        </div>
        <div class="kpi-grid" style="margin-bottom: 16px;">
          <div class="kpi-card"><div><span class="kpi-label">Units Sold</span><div class="kpi-value">${sales.units_sold || 0}</div></div></div>
          <div class="kpi-card"><div><span class="kpi-label">Revenue</span><div class="kpi-value">₹${(sales.revenue || 0).toLocaleString('en-IN')}</div></div></div>
          <div class="kpi-card"><div><span class="kpi-label">Current Stock</span><div class="kpi-value">${prod.quantity || 0}</div></div></div>
        </div>
        <h4>Recent Inventory Movements</h4>
        <div style="background: var(--bg-surface); padding: 12px; border-radius: 8px; margin-top: 8px; max-height: 180px; overflow-y: auto;">
          ${movements.map(m => `
            <div style="font-size: 12px; margin-bottom: 6px; display: flex; justify-content: space-between;">
              <span>${m.reason} (${m.quantity_change > 0 ? '+' : ''}${m.quantity_change})</span>
              <span style="color: var(--text-dim);">${new Date(m.created_at).toLocaleDateString()}</span>
            </div>
          `).join('')}
        </div>
      `;

      this.openModal('product-modal');
    } catch (err) {
      console.error('Failed opening product modal:', err);
    }
  }

  async openAdjustStockModal(productId = '', productName = '') {
    const select = document.getElementById('adj-product-select');
    if (select) {
      const products = await crmApi.getProducts();
      select.innerHTML = products.map(p => `
        <option value="${p.id}" ${p.id === productId ? 'selected' : ''}>${p.name} (Stock: ${p.quantity})</option>
      `).join('');
    }
    this.openModal('adjust-stock-modal');
  }

  async openCreateQuoteModal(customerId = '', customerName = '') {
    const custInput = document.getElementById('quote-cust-name');
    const phoneInput = document.getElementById('quote-cust-phone');
    const prodSelect = document.getElementById('quote-product-select');

    if (custInput) custInput.value = customerName || '';
    if (phoneInput) phoneInput.value = customerId || '+919876543210';

    if (prodSelect) {
      const products = await crmApi.getProducts();
      prodSelect.innerHTML = products.map(p => `
        <option value="${p.id}" data-price="${p.price}">${p.name} — ₹${p.price}</option>
      `).join('');
    }

    this.openModal('quote-modal');
  }

  // ===========================================================================
  // 5. Forms Binding
  // ===========================================================================
  bindForms() {
    // Adjust Stock Form
    document.getElementById('adjust-stock-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const productId = document.getElementById('adj-product-select')?.value;
      const delta = parseInt(document.getElementById('adj-delta')?.value, 10);
      const reason = document.getElementById('adj-reason')?.value;
      const reference = document.getElementById('adj-reference')?.value;

      try {
        await crmApi.adjustInventory({
          product_id: productId,
          delta: delta,
          reason: reason,
          reference_id: reference
        });
        this.showToast('Stock adjusted atomically!', 'success');
        this.closeModal('adjust-stock-modal');
        this.refreshCurrentView();
      } catch (err) {
        this.showToast('Failed to adjust stock: ' + err.message, 'danger');
      }
    });

    // Create Quote Form
    document.getElementById('create-quote-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const custName = document.getElementById('quote-cust-name')?.value;
      const custPhone = document.getElementById('quote-cust-phone')?.value;
      const prodSelect = document.getElementById('quote-product-select');
      const prodId = prodSelect?.value;
      const prodName = prodSelect?.options[prodSelect.selectedIndex]?.text.split('—')[0].trim();
      const price = parseFloat(prodSelect?.options[prodSelect.selectedIndex]?.getAttribute('data-price') || '0');
      const qty = parseInt(document.getElementById('quote-qty')?.value, 10);
      const discount = parseFloat(document.getElementById('quote-discount')?.value || '0');

      const subtotal = price * qty;
      const total = Math.max(0, subtotal - discount);

      try {
        await crmApi.createQuote({
          quote_id: `QU-${Math.floor(1000 + Math.random() * 9000)}`,
          businessId: 'stridehub-shoes',
          customer_id: custPhone,
          customer_name: custName,
          contact_number: custPhone,
          items: [{ product_id: prodId, product_name: prodName, size: '9', quantity: qty, unit_price: price, total_price: subtotal }],
          subtotal: subtotal,
          discount: discount,
          total_amount: total,
          status: 'sent'
        });
        this.showToast('Quote generated & sent!', 'success');
        this.closeModal('quote-modal');
        this.refreshCurrentView();
      } catch (err) {
        this.showToast('Failed creating quote', 'danger');
      }
    });

    // Create Task Form
    document.getElementById('create-task-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('task-title-input')?.value;
      const cust = document.getElementById('task-cust-input')?.value;
      const dueDate = document.getElementById('task-due-date')?.value;
      const priority = document.getElementById('task-priority-select')?.value;

      try {
        await crmApi.createTask({
          task_id: `task_${Date.now()}`,
          businessId: 'stridehub-shoes',
          title,
          customer_name: cust,
          due_date: dueDate,
          priority,
          status: 'pending'
        });
        this.showToast('Task added to schedule', 'success');
        this.closeModal('task-modal');
        this.loadTasks();
      } catch (err) {
        this.showToast('Failed adding task', 'danger');
      }
    });

    // Create Tag Form
    document.getElementById('create-tag-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('tag-name-input')?.value;
      const color = document.getElementById('tag-color-input')?.value;

      try {
        await crmApi.createTag({ name, color, category: 'custom' });
        this.showToast('Tag created!', 'success');
        this.closeModal('tag-modal');
        this.loadTags();
      } catch (err) {
        this.showToast('Failed creating tag', 'danger');
      }
    });

    // Settings Profile Form
    document.getElementById('settings-profile-form')?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = document.getElementById('set-store-name')?.value;
      const addr = document.getElementById('set-store-address')?.value;
      const hours = document.getElementById('set-store-hours')?.value;
      const ship = document.getElementById('set-store-shipping')?.value;
      const ret = document.getElementById('set-store-return')?.value;
      const ex = document.getElementById('set-store-exchange')?.value;

      try {
        await crmApi.saveSettings({
          businessId: 'stridehub-shoes',
          business_name: name,
          address: addr,
          working_hours: hours,
          shipping_information: ship,
          return_refund_policy: ret,
          exchange_policy: ex
        });
        this.showToast('Store settings updated!', 'success');
      } catch (err) {
        this.showToast('Failed saving settings', 'danger');
      }
    });

    // Filter Listeners
    document.getElementById('leads-stage-filter')?.addEventListener('change', () => this.loadLeads());
    document.getElementById('leads-score-filter')?.addEventListener('change', () => this.loadLeads());
    document.getElementById('leads-search-input')?.addEventListener('input', () => this.loadLeads());

    document.getElementById('customers-type-filter')?.addEventListener('change', () => this.loadCustomers());
    document.getElementById('customers-search-input')?.addEventListener('input', () => this.loadCustomers());

    document.getElementById('products-category-filter')?.addEventListener('change', () => this.loadProducts());
    document.getElementById('products-stock-filter')?.addEventListener('change', () => this.loadProducts());
    document.getElementById('products-search-input')?.addEventListener('input', () => this.loadProducts());

    document.getElementById('orders-status-filter')?.addEventListener('change', () => this.loadOrders());
    document.getElementById('orders-search-input')?.addEventListener('input', () => this.loadOrders());
  }

  // ===========================================================================
  // 6. Global Search & Hotkeys
  // ===========================================================================
  bindSearch() {
    const searchBtn = document.getElementById('search-modal-btn');
    const searchInput = document.getElementById('global-search-input');
    const searchGrid = document.getElementById('search-live-grid');

    searchBtn?.addEventListener('click', () => {
      this.openModal('search-modal');
      setTimeout(() => searchInput?.focus(), 100);
    });

    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.openModal('search-modal');
        setTimeout(() => searchInput?.focus(), 100);
      }
      if (e.key === 'Escape') {
        this.closeModal('search-modal');
      }
    });

    let debounceTimer;
    searchInput?.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const query = searchInput.value.trim();
      if (!query) {
        searchGrid.innerHTML = '<div class="empty-state">Type a search query to explore across all CRM business entities.</div>';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const results = await crmApi.search(query);
          this.renderSearchResults(results);
        } catch (err) {
          console.error('Search failed:', err);
        }
      }, 250);
    });
  }

  renderSearchResults(results) {
    const grid = document.getElementById('search-live-grid');
    if (!grid) return;

    let html = '';

    if (results.leads?.length) {
      html += '<h4 style="color: var(--primary); margin: 12px 0 6px;">Leads</h4>';
      html += results.leads.map(l => `
        <div class="conv-item" onclick="crmApp.closeModal('search-modal'); crmApp.openLeadDetailModal('${l.id}')">
          <strong>${this.escapeHtml(l.title)}</strong> &bull; ${l.subtitle}
        </div>
      `).join('');
    }

    if (results.products?.length) {
      html += '<h4 style="color: var(--primary); margin: 12px 0 6px;">Footwear Catalog</h4>';
      html += results.products.map(p => `
        <div class="conv-item" onclick="crmApp.closeModal('search-modal'); crmApp.openProductDetailModal('${p.id}')">
          <strong>${this.escapeHtml(p.title)}</strong> &bull; ${p.subtitle}
        </div>
      `).join('');
    }

    if (results.orders?.length) {
      html += '<h4 style="color: var(--primary); margin: 12px 0 6px;">Orders</h4>';
      html += results.orders.map(o => `
        <div class="conv-item" onclick="crmApp.closeModal('search-modal'); crmApp.switchView('orders')">
          <strong>${this.escapeHtml(o.title)}</strong> &bull; ${o.subtitle}
        </div>
      `).join('');
    }

    if (!html) {
      html = '<div class="empty-state">No matching CRM records found.</div>';
    }

    grid.innerHTML = html;
  }

  // ===========================================================================
  // 7. Interactive SVG Chart Renderers
  // ===========================================================================
  renderSvgTrendChart(containerId, points, prefix = '') {
    const container = document.getElementById(containerId);
    if (!container || !points.length) return;

    const width = container.clientWidth || 400;
    const height = 180;
    const padding = 24;

    const maxVal = Math.max(...points.map(p => p.value), 10);
    const minVal = 0;

    const stepX = (width - padding * 2) / Math.max(1, points.length - 1);
    const scaleY = (height - padding * 2) / (maxVal - minVal);

    const coords = points.map((p, i) => {
      const x = padding + i * stepX;
      const y = height - padding - (p.value - minVal) * scaleY;
      return { x, y, label: p.date, val: p.value };
    });

    const pathD = coords.reduce((acc, c, i) => {
      return i === 0 ? `M ${c.x} ${c.y}` : `${acc} L ${c.x} ${c.y}`;
    }, '');

    const areaD = `${pathD} L ${coords[coords.length - 1].x} ${height - padding} L ${coords[0].x} ${height - padding} Z`;

    const svg = `
      <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}">
        <defs>
          <linearGradient id="grad-${containerId}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.0"/>
          </linearGradient>
        </defs>
        <path d="${areaD}" fill="url(#grad-${containerId})" />
        <path d="${pathD}" fill="none" stroke="#3b82f6" stroke-width="2.5" />
        ${coords.map(c => `
          <circle cx="${c.x}" cy="${c.y}" r="3.5" fill="#60a5fa" stroke="#090d12" stroke-width="1.5" />
        `).join('')}
      </svg>
    `;

    container.innerHTML = svg;
  }

  renderFunnelChart(containerId, funnelCounts) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const stages = Object.entries(funnelCounts);
    const maxVal = Math.max(...stages.map(([_, v]) => v), 1);

    container.innerHTML = stages.map(([stage, count]) => {
      const pct = Math.round((count / maxVal) * 100);
      return `
        <div class="funnel-bar-row">
          <div class="funnel-bar-label-row">
            <span>${stage}</span>
            <strong>${count} leads</strong>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  renderTopProductsList(containerId, products) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = products.map((p, i) => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 13px;">
        <div>
          <strong>${i + 1}. ${this.escapeHtml(p.name)}</strong>
          <div style="font-size: 11px; color: var(--text-dim);">${p.units_sold || 0} units &bull; Stock: ${p.stock}</div>
        </div>
        <strong style="color: var(--success);">₹${(p.revenue || 0).toLocaleString('en-IN')}</strong>
      </div>
    `).join('');
  }

  renderCategoryBars(containerId, catSales) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const maxRev = Math.max(...catSales.map(c => c.revenue), 1000);

    container.innerHTML = catSales.map(c => {
      const pct = Math.round((c.revenue / maxRev) * 100);
      return `
        <div class="funnel-bar-row">
          <div class="funnel-bar-label-row">
            <span>${c.category}</span>
            <strong>₹${c.revenue.toLocaleString('en-IN')}</strong>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${pct}%; background: #10b981;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // ===========================================================================
  // 8. Storefront & Live Chat Compatibility
  // ===========================================================================
  async loadStorefrontProducts() {
    const grid = document.getElementById('store-products-grid');
    if (!grid) return;
    const products = await crmApi.getProducts();
    grid.innerHTML = products.map(p => `
      <div class="kpi-card" style="flex-direction: column;">
        <img src="${p.imageUrl}" style="width: 100%; height: 160px; object-fit: cover; border-radius: 8px; margin-bottom: 12px;">
        <h3>${p.name}</h3>
        <p style="color: var(--text-muted); font-size: 12px; margin: 4px 0 12px;">${p.description}</p>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <strong style="font-size: 16px; color: var(--primary);">₹${p.price}</strong>
          <span class="status-badge status-${p.stockStatus}">${p.stockStatus}</span>
        </div>
      </div>
    `).join('');
  }

  initLiveChat() {
    const box = document.getElementById('chat-messages-box');
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');

    if (!box) return;
    if (box.children.length === 0) {
      box.innerHTML = `
        <div class="chat-bubble assistant">
          Hello! Welcome to Starboyz Shoes. What kind of shoes are you looking for today?
        </div>
      `;
    }

    const sendHandler = async () => {
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      box.innerHTML += `<div class="chat-bubble user">${this.escapeHtml(text)}</div>`;
      box.scrollTop = box.scrollHeight;

      try {
        const res = await fetch('/api/chat/message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: [] })
        });
        const data = await res.json();
        box.innerHTML += `<div class="chat-bubble assistant">${this.escapeHtml(data.reply_text || data.reply || 'Thank you for your message!')}</div>`;
        box.scrollTop = box.scrollHeight;
      } catch (err) {
        box.innerHTML += `<div class="chat-bubble assistant">Thank you! Our AI Sales Assistant has recorded your requirement.</div>`;
      }
    };

    sendBtn?.addEventListener('click', sendHandler);
    input?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendHandler();
    });
  }

  // ===========================================================================
  // Utilities
  // ===========================================================================
  setText(elementId, text) {
    const el = document.getElementById(elementId);
    if (el) el.textContent = text;
  }

  formatTimeAgo(isoStr) {
    if (!isoStr) return 'just now';
    const diff = (Date.now() - new Date(isoStr).getTime()) / 1000;
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}

// Global Application Singleton
const crmApp = new CrmApplication();

document.addEventListener('DOMContentLoaded', () => {
  crmApp.init();
});
