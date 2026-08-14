-- ============================================================================
-- Multi-Tenant WhatsApp Sales-Qualification Database Schema with RLS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tenants Table (Root multi-tenant entity)
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    whatsapp_phone_number_id VARCHAR(100) UNIQUE NOT NULL,
    whatsapp_access_token TEXT,
    webhook_secret VARCHAR(255) NOT NULL,
    verify_token VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 2. Leads Table (Tenant-scoped)
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contact_number VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    stage VARCHAR(50) DEFAULT 'greet' NOT NULL, -- greet, qualify, collect_budget, collect_timeline, score, route, quoted, nurture, human_handoff
    budget_signal VARCHAR(255),                  -- Populated budget requirement (e.g. '$10k-$25k', '5000 USD')
    timeline_signal VARCHAR(255),                -- Populated timeline requirement (e.g. 'Within 2 weeks', 'Q3')
    qualification_score NUMERIC(5, 2) DEFAULT 0, -- Score from 0.00 to 100.00
    route_destination VARCHAR(50),               -- quoted, nurture, human_handoff
    metadata JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_tenant_contact UNIQUE (tenant_id, contact_number)
);

CREATE INDEX IF NOT EXISTS idx_leads_tenant_contact ON leads(tenant_id, contact_number);
CREATE INDEX IF NOT EXISTS idx_leads_tenant_stage ON leads(tenant_id, stage);

-- 3. Conversations Table (Tenant-scoped)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    whatsapp_message_id VARCHAR(255),
    raw_payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_conversations_tenant_lead ON conversations(tenant_id, lead_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- 4. Qualification Flows Table (Tenant-scoped)
CREATE TABLE IF NOT EXISTS qualification_flows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    config JSONB DEFAULT '{}'::jsonb NOT NULL, -- threshold scores, custom prompt overrides, custom routing rules
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_qualification_flows_tenant ON qualification_flows(tenant_id);

-- 5. Quotes and Invoices Table (Tenant-scoped)
CREATE TABLE IF NOT EXISTS quotes_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD' NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' NOT NULL, -- draft, sent, accepted, rejected, paid
    payload JSONB DEFAULT '{}'::jsonb NOT NULL,  -- line items, payment links, discounts
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_quotes_invoices_tenant_lead ON quotes_invoices(tenant_id, lead_id);

-- 6. Follow-Up Jobs Table (Tenant-scoped)
CREATE TABLE IF NOT EXISTS follow_up_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL, -- pending, executed, cancelled, failed
    task_type VARCHAR(100) NOT NULL,              -- nurture_checkin, quote_followup, payment_reminder
    payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_follow_up_jobs_tenant_status ON follow_up_jobs(tenant_id, status, scheduled_at);

-- ============================================================================
-- Row-Level Security (RLS) Configuration
-- ============================================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualification_flows ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_up_jobs ENABLE ROW LEVEL SECURITY;

-- Force RLS even for table owners (except superuser / bypassrls)
ALTER TABLE leads FORCE ROW LEVEL SECURITY;
ALTER TABLE conversations FORCE ROW LEVEL SECURITY;
ALTER TABLE qualification_flows FORCE ROW LEVEL SECURITY;
ALTER TABLE quotes_invoices FORCE ROW LEVEL SECURITY;
ALTER TABLE follow_up_jobs FORCE ROW LEVEL SECURITY;

-- RLS Policy: Leads
DROP POLICY IF EXISTS tenant_isolation_leads ON leads;
CREATE POLICY tenant_isolation_leads ON leads
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);

-- RLS Policy: Conversations
DROP POLICY IF EXISTS tenant_isolation_conversations ON conversations;
CREATE POLICY tenant_isolation_conversations ON conversations
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);

-- RLS Policy: Qualification Flows
DROP POLICY IF EXISTS tenant_isolation_qualification_flows ON qualification_flows;
CREATE POLICY tenant_isolation_qualification_flows ON qualification_flows
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);

-- RLS Policy: Quotes Invoices
DROP POLICY IF EXISTS tenant_isolation_quotes_invoices ON quotes_invoices;
CREATE POLICY tenant_isolation_quotes_invoices ON quotes_invoices
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);

-- RLS Policy: Follow-Up Jobs
DROP POLICY IF EXISTS tenant_isolation_follow_up_jobs ON follow_up_jobs;
CREATE POLICY tenant_isolation_follow_up_jobs ON follow_up_jobs
    FOR ALL
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
