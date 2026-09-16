# 👟 StrideHub Shoes — Real-Time AI Sales Agent & CRM

An enterprise-grade, real-time AI-powered WhatsApp sales chat application and CRM system built for **StrideHub Shoes**, powered by **Google Gemini API**, **Cloud Firestore (Project: `ai-sales-agent---shoe`)**, **LangGraph**, and **FastAPI**.

---

## 🏗️ Architecture & Philosophy

```
CUSTOMER (WhatsApp UI / Web Simulator)
             │
             ▼
FASTAPI WEB APPLICATION & WEBHOOK LAYER (`app/main.py`, `app/api/`)
  ├── Real-Time Web Chat API (`/api/chat/message`)
  ├── CRM Analytics & Inventory API (`/api/crm/*`)
  ├── Meta WhatsApp Cloud API Inbound Webhook (`/webhook/whatsapp`)
  └── Modern WhatsApp Web UI + CRM Dashboard SPA (`app/static/`)
             │
             ▼
CLOUD FIRESTORE (Single Source of Truth - Project: `ai-sales-agent---shoe`)
  ├── `businesses`: StrideHub Shoes profile, policies, hours, FAQs, active offers
  ├── `products`: 70+ field shoe catalog (Running, Casual, Formal, Trail, sizes 5-12, specs)
  ├── `customers` & `leads`: CRM contact profiles, LangGraph stage, qualification scores (0-100)
  ├── `conversations` & `messages`: Real-time chat transcripts and message memory
  ├── `orders` & `order_items`: Orders, delivery status, BlueDart courier tracking
  └── `automation_rules` & `follow_up_jobs`: Automated re-engagement rules
             │
             ▼
LANGGRAPH WORKFLOW CONTROLLER (`app/agent/graph.py`)
  ├── [Greet] ──> [Qualify / Need] ──> [Product Lookup (Firestore)]
  └── [Collect Budget] ──> [Collect Timeline] ──> [Score] ──> [Route (Quoted/Nurture/Human Handoff)]
             │
             ▼
GEMINI CONVERSATIONAL INTELLIGENCE (`app/services/gemini_service.py`)
  ├── Natural, Non-Robotic Human Copywriting ("Hey! 👋 What kind of shoes are you looking for?")
  ├── Conversational Context Memory across multiple turns (e.g. "I need black shoes" -> "running" -> knows black running shoes)
  ├── Multilingual & Slang Understanding (English, Tamil, Tanglish 'bro stock iruka', 'price sollunga')
  ├── Typos & Casual Language Understanding ('how much dis', 'need 5 pcs')
  ├── Polite De-escalation of Abusive/Inappropriate Language
  └── Untrusted Input Defense (Prompt injection & system secret protections)
             │
             ▼
RESPONSE VALIDATION & ANTI-HALLUCINATION LAYER (`app/services/validation_service.py`)
  ├── Price Integrity: Exact Firebase prices (e.g. ₹1,299; never ₹1,499)
  ├── Discount Guard: Refuses unauthorized discounts (e.g. ₹800) unless active Firebase offer
  ├── Inventory & Variant Guard: Out-of-stock messages when stock = 0, corrects invalid sizes (e.g. size 14 not available, valid are 5-12)
  └── Atomic Inventory Updates: Prevents race conditions and negative inventory
```

---

## 🌟 Key Features

### 1. 💬 WhatsApp-Style Live Sales Chat
- Realistic WhatsApp Web interface with **StrideHub Shoes Official Verified Green Badge**.
- Real-time typing animation with natural delay.
- **Interactive Rich Shoe Cards**: High-res photos, badge pills (*Sale 33% Off*, *Only 3 left!*, *Out of Stock*), price comparison (MRP vs Sale Price), available size chips (5 to 12), and one-tap purchase.
- **Live Order Tracking Cards**: Step-by-step progress stepper (`Placed` -> `Confirmed` -> `Dispatched` -> `Delivered`).
- Contextual quick-reply chips.

### 2. 📊 Executive CRM Dashboard
- Live KPI Metrics: **Total Leads**, **Qualified Leads**, **Orders**, **Conversions %**, **Revenue ₹**, **Active Conversations**, **Pending Follow-ups**, **Human Handoffs**.
- **Interactive Funnel Visualization**: `Enquiries` -> `Qualified Leads` -> `Orders / Conversions`.
- Real-time activity timeline feed.

### 3. 👟 Shoe Catalog & Live Atomic Inventory
- Filterable and searchable shoe catalog (Running, Casual, Formal, Trail, Walking).
- Inline **Atomic Stock Controls (+ / -)** with instant Firestore synchronization.

### 4. 👥 Leads Pipeline (LangGraph Kanban)
- Kanban pipeline tracking lead state through LangGraph stages: `Greet` -> `Qualify` -> `Collect Budget` -> `Collect Timeline` -> `Score` -> `Route` (`Quoted`, `Nurture`, `Human Handoff`).
- Lead score progress meters (0–100 pts) with breakdown of needs, budget, and timeline signals.

---

## 🔒 Source of Truth Policy (Cloud Firestore)

Cloud Firestore is the **sole authoritative database** for all business facts:
- If a product costs **₹1,299**, the AI will **never** state ₹1,499.
- If a product has **stock = 0**, the AI will **never** claim it is available.
- If a customer asks for an unapproved discount (e.g. **₹800**), the AI will state the exact current price and refuse the unauthorized discount.
- If a customer asks for **size 14**, the AI will clarify that size 14 is not available and present the available size range (**5 to 12**).

---

## 🚀 Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
```
Edit `.env` with your Google Gemini API key and Firebase configuration:
```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
AI_PROVIDER=gemini
FIREBASE_PROJECT_ID=ai-sales-agent---shoe
```

### 2. Run the Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open the Web Application
Open your browser and navigate to:
```
http://localhost:8000
```

---

## 🧪 Running Automated Tests

Run the full suite of **44 automated tests**:
```bash
pytest -v
```

Test suites include:
- `tests/test_stridehub_shoes.py`: Product search, size 14 correction, out of stock (stock=0), low stock (stock=3), price fidelity (₹1,299), discount refusal (₹800), order tracking (#SH-8942), Tanglish, context memory, atomic inventory, and REST APIs.
- `tests/test_gemini_conversational.py`: Natural language, typos, greetings, small talk, abusive language de-escalation, prompt injection defense, LangGraph scoring.
- `tests/test_firebase_grounding.py`: Anti-hallucination validation, price sanitization, stock detection, and atomic inventory updates.
- `tests/test_multitenant_isolation.py`: Cross-tenant boundary enforcement in Firestore.
- `tests/test_stage_transition.py`: Budget constraint enforcement for `quoted` stage.
- `tests/test_webhook.py`: Meta WhatsApp Cloud API signature verification and lead creation.
- `tests/test_rls_isolation.py`: PostgreSQL RLS tenant data isolation.
