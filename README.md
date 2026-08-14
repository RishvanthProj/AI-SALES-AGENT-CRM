# WhatsApp Multi-Tenant Sales-Qualification Backend

An enterprise-grade, multi-tenant backend service for WhatsApp sales qualification built with **Python**, **FastAPI**, **PostgreSQL (with Row-Level Security)**, **LangGraph**, and **Anthropic Claude API**.

---

## 🏗️ Architecture & Philosophy

```
                               ┌──────────────────────────────────────────────┐
                               │       WhatsApp Business Cloud API            │
                               └──────────────────────┬───────────────────────┘
                                                      │ Inbound Webhook (POST)
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │           FastAPI Webhook Router             │
                               │        - Meta HMAC-SHA256 Signature Verify   │
                               │        - Verify Token Challenge (GET)        │
                               └──────────────────────┬───────────────────────┘
                                                      │
                                                      ▼
                       ┌──────────────────────────────────────────────────────────────┐
                       │          Tenant-Scoped Database Session (PostgreSQL)         │
                       │           SET LOCAL app.current_tenant_id = :tenant_id       │
                       │        - Enforces Row-Level Security across all queries      │
                       │        - Get or Create Lead record for contact number        │
                       └──────────────────────────────┬───────────────────────────────┘
                                                      │
                                                      ▼
                       ┌──────────────────────────────────────────────────────────────┐
                       │               LangGraph State Machine Engine                 │
                       │                                                              │
                       │   [Greet] ──> [Qualify] ──> [Collect Budget]                 │
                       │                                     │                        │
                       │   [Route] <── [Score]   <── [Collect Timeline]               │
                       │      │                                                       │
                       │      ├──> Quoted (Score >= 70 AND budget_signal present)     │
                       │      ├──> Nurture (Score < 40)                               │
                       │      └──> Human Handoff (High-touch)                         │
                       │                                                              │
                       │   * Graph topology controls all stage transitions.           │
                       │   * Claude LLM only performs field extraction & copy.        │
                       └──────────────────────────────┬───────────────────────────────┘
                                                      │
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │         Outbound WhatsApp Messenger          │
                               │       - Dispatches contextual reply          │
                               └──────────────────────────────────────────────┘
```

---

## 🛡️ PostgreSQL Database & Row-Level Security (RLS)

All tenant-scoped tables enforce Row-Level Security:
1. `tenants`: Root multi-tenant entity (phone number IDs, webhook secrets, tokens).
2. `leads`: Stores contact number, stage, `budget_signal`, `timeline_signal`, `qualification_score`, `route_destination`.
3. `conversations`: Inbound & outbound message history with payload logs.
4. `qualification_flows`: Tenant-customized scoring thresholds & prompt rules.
5. `quotes_invoices`: Generated quotes, amounts, and statuses.
6. `follow_up_jobs`: Scheduled automated touchpoints.

### RLS Policy Definition
```sql
CREATE POLICY tenant_isolation_leads ON leads
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
```

---

## 🔒 Stage Transition Guard: Budget Constraint

A lead **cannot** transition to the `quoted` stage without a populated `budget_signal`:
```python
# app/services/lead_service.py
if new_stage == "quoted":
    if not effective_budget or not str(effective_budget).strip():
        raise InvalidStageTransitionError(
            f"Lead {lead.id} cannot transition to 'quoted' state without a populated budget_signal field."
        )
```

---

## 🚀 Getting Started

### 1. Environment Setup
```bash
cp .env.example .env
```
Edit `.env` with your credentials:
```ini
ANTHROPIC_API_KEY=sk-ant-api03-...
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_sales_db
WHATSAPP_VERIFY_TOKEN=your_token
WHATSAPP_APP_SECRET=your_app_secret
```

### 2. Run Database Migrations
Execute the SQL script in your Postgres instance:
```bash
psql -d whatsapp_sales_db -f app/db/schema.sql
```

### 3. Run FastAPI Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Included test suites:
- `tests/test_stage_transition.py`: Confirms leads cannot reach `quoted` state without a populated `budget_signal`.
- `tests/test_rls_isolation.py`: Confirms tenant data isolation and boundary enforcement.
- `tests/test_webhook.py`: Confirms Meta token handshake, signature verification, and automated lead creation.
- `tests/test_langgraph_flow.py`: Confirms deterministic execution across LangGraph nodes.
