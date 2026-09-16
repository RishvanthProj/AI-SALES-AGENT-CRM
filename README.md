# 👟 STARBOYZ FOOTWEAR — AI SALES OS & ENTERPRISE CRM PLATFORM

An enterprise-grade, real-time AI Sales Assistant and CRM Operating System built for **Starboyz Footwear**, powered by **Google Gemini API**, **Cloud Firestore**, **LangGraph**, and **FastAPI**.

---

## 🏗️ Architecture & Interconnection Overview

The platform operates as a unified, dual-interface sales & operations engine connected to a single authoritative database:

```
                                  CLOUD FIRESTORE (Single Authoritative Source of Truth)
                       ┌────────────────────────────────────────────────────────────────────────┐
                       │ • businesses: Starboyz profile, policies, hours, FAQs, active offers   │
                       │ • products: Verified catalog (prices, MRPs, sizes, variants, specs)    │
                       │ • inventory_movements: Atomic audit trail for all stock adjustments   │
                       │ • customers & 360: Aggregated lifetime spend, orders, AOV, transcripts │
                       │ • leads & pipeline: LangGraph qualification score & Kanban stages      │
                       │ • orders & order_items: Orders, delivery status, BlueDart tracking     │
                       │ • quotes, tasks, notes, tags & activity stream: Operational records    │
                       └───────────────────▲──────────────────────────────▲─────────────────────┘
                                           │                              │
                     ┌─────────────────────┴───────┐              ┌───────┴────────────────────┐
                     │                             │              │                            │
                     ▼                             ▼              ▼                            ▼
      ┌─────────────────────────────┐  ┌────────────────────────────────────────────────────────┐
      │   INTERFACE A: TERMINAL     │  │                  INTERFACE B: SAAS CRM                 │
      │   AI SALES CHATBOT          │  │                  WEB APPLICATION COMMAND CENTER        │
      │                             │  │                                                        │
      │ • python terminal_chat.py   │  │ • http://localhost:8000 (FastAPI + Modern SPA)         │
      │ • Standalone CLI runner     │  │ • 18-Section Enterprise Command Center                 │
      │ • Gemini Active Listening   │  │ • Executive KPI Dashboard (Leads, Revenue, Orders)     │
      │ • Tanglish/Hinglish Support │  │ • Live Customer Chat Inbox (3-Column Split View)       │
      │ • Anti-Hallucination Guard  │  │ • Leads Management & LangGraph Pipeline (Kanban)       │
      │ • Interactive CLI Checkout  │  │ • Customer 360 Deep Profile & Order History            │
      │ • Atomic stock decrement    │  │ • Product Catalog CRUD & Inventory Adjustments         │
      │ • BlueDart tracking receipt │  │ • Quotes, Tasks, Notes, Tags & Activity Audit Stream   │
      └─────────────────────────────┘  └────────────────────────────────────────────────────────┘
```

---

## ✨ Key Capabilities

### 1. Standalone Terminal AI Sales Chat (`python terminal_chat.py`)
- **Zero Robotic Scripts & Zero Emojis**: Speaks naturally like a knowledgeable store specialist and friend.
- **Active Listening & Discovery**: Listens to customer intent first, asks for UK shoe size and budget before suggesting the ideal match.
- **Multilingual & Slang Adaptation**: Fluently recognizes and responds in **Tanglish** (Tamil in Latin script), **Hinglish** (Hindi in Latin script), and **Tenglish** (Telugu in Latin script), maintaining language consistency throughout the sale.
- **Robust Edge-Case Handling**: Detects bulk orders (>4 pairs), gracefully deflects prompt injection attempts, and politely de-escalates aggressive language.
- **Interactive In-Terminal Checkout**: Collects shipping address, calculates order totals, supports Cash on Delivery (COD) and simulated instant UPI QR Code scanning, records the transaction in Cloud Firestore, and issues an instant tracking code (`#SB-xxxx` + BlueDart AWB).

### 2. Full-Featured SaaS CRM Platform (`http://localhost:8000`)
- **Executive Dashboard**: Real-time sales KPIs, revenue trends, lead conversion rates, pending follow-ups, and low-stock alerts.
- **Live Chat Inbox**: 3-column split view (conversation list, live transcript stream, and customer profile panel) with auto-refresh polling (4s interval).
- **Leads & Pipeline (Kanban)**: Visual kanban board categorizing leads across 6 stages (`Enquired`, `Engaged`, `Quoted`, `Nurture`, `Human Handoff`, `Converted`) with lead scoring (0–100 pts).
- **Customer 360**: Unified profile aggregating lifetime spend, total orders, average order value (AOV), purchased products, and full conversation transcripts.
- **Catalog & Inventory Management**: Interactive shoe catalog with instant search, variant filtering, inline atomic stock adjustments, and complete stock movement audit history.
- **Quotes & Invoices**: Create quotes, auto-generate invoices upon acceptance, and track payment status.
- **Tasks & Follow-ups**: Prioritized task list (`Today`, `Pending`, `Overdue`, `Completed`) linked to leads and customers.
- **Activity Timeline**: Comprehensive real-time event log tracking all customer messages, order placements, stock adjustments, and stage transitions.

### 3. Authoritative Anti-Hallucination & Grounding Engine
- **Price Integrity**: AI responses are validated against verified Firestore pricing; unauthorized discount promises are automatically corrected.
- **Inventory & Size Guard**: The bot will never claim a shoe is available if stock = 0, and will correct customers requesting sizes outside the valid range (UK 5–12).
- **Atomic Operations**: Prevents race conditions and negative inventory during simultaneous checkouts.

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
```
Ensure `.env` contains your Gemini API key and Firebase settings:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
AI_PROVIDER=gemini
FIREBASE_PROJECT_ID=ai-sales-agent---shoe
PORT=8000
HOST=127.0.0.1
```

### 2. Launch Development Server
```bash
./run_dev.sh
```
Or start manually via uvicorn:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Launch Terminal Sales Chatbot (In a separate terminal window)
```bash
python terminal_chat.py
```

### 4. Access Web Interfaces
- **SaaS CRM Platform**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/crm/dashboard` | Returns aggregated KPIs, conversion metrics, and trend charts |
| `GET` | `/api/crm/leads` | Lists all leads with filtering by stage and score |
| `GET` | `/api/crm/leads/{lead_id}` | Detailed lead record with linked customer, quotes, and timeline |
| `POST` | `/api/crm/leads/{lead_id}/stage` | Updates lead pipeline stage |
| `GET` | `/api/crm/customers` | Lists all CRM customers with order stats and spend |
| `GET` | `/api/crm/customers/{customer_id}/360` | Full 360-degree customer profile with history |
| `GET` | `/api/crm/conversations` | Lists all active conversation threads with last message preview |
| `GET` | `/api/crm/conversations/{customer_id}` | Complete message transcript for a customer |
| `POST` | `/api/crm/conversations/{customer_id}/send` | Send agent reply message to customer |
| `GET` | `/api/crm/pipeline` | Pipeline Kanban data partitioned by stage |
| `GET` | `/api/crm/products` | Lists shoe catalog with stock and pricing |
| `POST` | `/api/crm/products` | Create new shoe product |
| `PUT` | `/api/crm/products/{product_id}` | Update product details |
| `DELETE` | `/api/crm/products/{product_id}` | Delete product from catalog |
| `POST` | `/api/crm/inventory/adjust` | Atomically adjust inventory with reason and audit log |
| `GET` | `/api/crm/inventory/movements` | Stock movement audit history |
| `GET` | `/api/crm/orders` | Lists all customer orders with tracking status |
| `POST` | `/api/crm/orders` | Create order |
| `GET` | `/api/crm/quotes` | Lists sales quotes |
| `POST` | `/api/crm/quotes` | Create sales quote |
| `PATCH` | `/api/crm/quotes/{quote_id}/status` | Accept/reject quote and generate invoice |
| `GET` | `/api/crm/tasks` | Lists tasks by filter view (`all`, `today`, `overdue`, `pending`) |
| `POST` | `/api/crm/tasks` | Create task |
| `GET` | `/api/crm/activity` | Unified activity audit stream |
| `GET` | `/api/crm/search?q={query}` | Global search across products, leads, customers, orders |
| `GET` | `/api/crm/health` | System health check and database status |

---

## 🧪 Testing & Automated Verification

Run the comprehensive pytest suite covering grounding, conversation, CRM API, inventory atomicity, and multi-tenant isolation:

```bash
pytest -v
```

To run individual test modules:
```bash
# CRM Interconnection & Grounding
pytest -v tests/test_crm_interconnection.py tests/test_firebase_grounding.py

# Conversational Intelligence & Multilingual Adaptation
pytest -v tests/test_gemini_conversational.py tests/test_multilingual_adaptation.py
```
