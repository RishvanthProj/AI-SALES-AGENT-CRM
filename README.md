# Starboyz Footwear — Real-Time AI Sales Agent & CRM

An enterprise-grade, real-time AI-powered sales chat application and CRM system built for **Starboyz Footwear**, powered by **Google Gemini API**, **Cloud Firestore (Project: `ai-sales-agent---shoe`)**, **LangGraph**, and **FastAPI**.

---

## Architecture & System Flow

```
CUSTOMER (WhatsApp UI / Terminal CLI / Web Simulator)
             │
             ▼
FASTAPI WEB APPLICATION & WEBHOOK LAYER (app/main.py, app/api/, terminal_chat.py)
  ├── Real-Time Web Chat API (/api/chat/message)
  ├── Interactive Terminal Chat Runner (terminal_chat.py)
  ├── CRM Analytics & Inventory API (/api/crm/*)
  ├── Meta WhatsApp Cloud API Inbound Webhook (/webhook/whatsapp)
  └── Modern Clean Web UI + CRM Dashboard SPA (app/static/)
             │
             ▼
CLOUD FIRESTORE (Single Source of Truth - Project: ai-sales-agent---shoe)
  ├── businesses: Starboyz profile, policies, hours, FAQs, active offers
  ├── products: 70+ field shoe catalog (Running, Casual, Formal, Trail, sizes 5-12, specs)
  ├── customers & leads: CRM contact profiles, LangGraph stage, qualification scores (0-100)
  ├── conversations & messages: Real-time chat transcripts and message memory
  ├── orders & order_items: Orders, delivery status, BlueDart courier tracking (#SB-xxxx)
  └── automation_rules & follow_up_jobs: Automated re-engagement rules
             │
             ▼
LANGGRAPH WORKFLOW CONTROLLER (app/agent/graph.py)
  ├── [Greet] ──> [Qualify / Need] ──> [Product Lookup (Firestore)]
  └── [Collect Budget] ──> [Collect Timeline] ──> [Score] ──> [Route (Quoted/Nurture/Human Handoff)]
             │
             ▼
GEMINI CONVERSATIONAL INTELLIGENCE (app/services/gemini_service.py)
  ├── Natural, Non-Robotic Human Copywriting (Plain text, zero emojis, conversational friend persona)
  ├── Active Listening & Discovery (Asks for use case, budget, UK size before recommending shoes)
  ├── Conversational Context Memory across multiple turns
  ├── Multilingual & Slang Understanding (English, Tamil, Tanglish 'bro stock iruka', 'price sollunga')
  ├── Typos & Casual Language Understanding ('how much dis', 'need 5 pcs')
  ├── Edge-case Brain (Bulk order detection > 4 pairs, polite de-escalation of foul language)
  └── Untrusted Input Defense (Prompt injection & system secret protections)
             │
             ▼
RESPONSE VALIDATION & ANTI-HALLUCINATION LAYER (app/services/validation_service.py)
  ├── Price Integrity: Exact Firebase prices (e.g. Rs. 1,299; never Rs. 1,499)
  ├── Discount Guard: Refuses unauthorized discounts unless active Firebase offer
  ├── Inventory & Variant Guard: Out-of-stock messages when stock = 0, corrects invalid sizes (valid are 5-12)
  └── Atomic Inventory Updates: Prevents race conditions and negative inventory
```

---

## Key Features

### 1. Interactive Terminal Chat (Zero Emojis, Human Friend Persona)
- Pure terminal conversation via `python terminal_chat.py`.
- No robotic scripts or force-selling; listens first, categorizes preferences, and asks for budget & UK size.
- In-chat interactive checkout: collects Name, Address, City, State/Pincode, displays clean order summary, handles COD or simulated instant UPI QR scan, atomically decrements stock in Cloud Firestore, and issues tracking ID (#SB-xxxx + BlueDart AWB).

### 2. Live Web Sales Chat & CRM Dashboard
- Clean web interface with Starboyz branding.
- Real-time typing animation and responsive layout.
- Interactive rich shoe cards and live order tracking stepper.
- CRM KPIs: Total Leads, Qualified Leads, Orders, Conversions %, Revenue, Active Conversations.

### 3. Shoe Catalog & Atomic Inventory
- Filterable and searchable shoe catalog (Running, Casual, Formal, Trail, Walking).
- Inline atomic stock controls with instant Firestore synchronization.

### 4. Leads Pipeline (LangGraph Kanban)
- Kanban pipeline tracking lead state through LangGraph stages: `Greet` -> `Qualify` -> `Collect Budget` -> `Collect Timeline` -> `Score` -> `Route`.
- Lead score progress meters (0–100 pts) with breakdown of needs, budget, and timeline signals.

---

## Source of Truth Policy (Cloud Firestore)

Cloud Firestore is the **sole authoritative database** for all business facts:
- If a product costs **Rs. 1,299**, the AI will **never** state Rs. 1,499.
- If a product has **stock = 0**, the AI will **never** claim it is available.
- If a customer asks for an unapproved discount (e.g. **Rs. 800**), the AI will state the exact current price and refuse the unauthorized discount.
- If a customer asks for **size 14**, the AI will clarify that size 14 is not available and present the available size range (**5 to 12**).

---

## Quick Start

### 1. Environment Setup
```bash
cp .env.example .env
```
Edit `.env` with your Google Gemini API key and Firebase configuration:
```ini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
AI_PROVIDER=gemini
FIREBASE_PROJECT_ID=ai-sales-agent---shoe
```

### 2. Run Interactive Terminal Chat
```bash
python terminal_chat.py
```

### 3. Run Web Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at `http://localhost:8000`.

---

## Running Automated Tests

Run the full suite of **60 automated tests**:
```bash
pytest -v
```

Test suites include:
- `tests/test_multilingual_adaptation.py`: Pan-India transliterated language adaptation (Tanglish persistence for Tamil Nadu, Hinglish, Tenglish, Manglish, English), end-to-end multi-turn dialog, and zero emoji enforcement.
- `tests/test_stridehub_shoes.py`: Product search, size 14 correction, out of stock (stock=0), low stock (stock=3), price fidelity, discount refusal, order tracking, Tanglish, context memory, atomic inventory, and REST APIs.
- `tests/test_gemini_conversational.py`: Natural language, typos, greetings, small talk, abusive language de-escalation, prompt injection defense, LangGraph scoring.
- `tests/test_firebase_grounding.py`: Anti-hallucination validation, price sanitization, stock detection, and atomic inventory updates.
- `tests/test_multitenant_isolation.py`: Cross-tenant boundary enforcement in Firestore.
- `tests/test_stage_transition.py`: Budget constraint enforcement for `quoted` stage.
- `tests/test_webhook.py`: Meta WhatsApp Cloud API signature verification and lead creation.
- `tests/test_rls_isolation.py`: PostgreSQL RLS tenant data isolation.
