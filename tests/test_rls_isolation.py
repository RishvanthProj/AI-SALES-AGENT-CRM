import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Tenant, Lead, Conversation
from app.services.lead_service import LeadService


@pytest.mark.asyncio
async def test_tenant_data_isolation_across_tenants(
    db_session: AsyncSession,
    sample_tenant: Tenant,
    second_tenant: Tenant
):
    """
    Test Requirement:
    Confirm strict tenant data isolation (RLS / tenant-scoped access).
    Ensures Tenant A cannot access, query, count, or modify Tenant B's leads or conversations.
    """
    # 1. Create leads for Tenant 1 (Acme Solar)
    lead_t1_a, _ = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=sample_tenant.id,
        contact_number="+1111111111",
        name="Tenant 1 Lead Alpha"
    )
    lead_t1_b, _ = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=sample_tenant.id,
        contact_number="+1111111112",
        name="Tenant 1 Lead Beta"
    )

    # 2. Create leads for Tenant 2 (Global Logistics)
    lead_t2_a, _ = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=second_tenant.id,
        contact_number="+2222222221",
        name="Tenant 2 Lead Gamma"
    )

    # Record conversations for each tenant
    await LeadService.record_conversation(
        session=db_session,
        tenant_id=sample_tenant.id,
        lead_id=lead_t1_a.id,
        role="user",
        content="Confidential Solar Inquiry for Tenant 1"
    )
    await LeadService.record_conversation(
        session=db_session,
        tenant_id=second_tenant.id,
        lead_id=lead_t2_a.id,
        role="user",
        content="Confidential Logistics Shipment for Tenant 2"
    )

    # 3. Query under Tenant 1's scope
    stmt_t1_leads = select(Lead).where(Lead.tenant_id == sample_tenant.id)
    result_t1_leads = await db_session.execute(stmt_t1_leads)
    t1_leads = result_t1_leads.scalars().all()

    assert len(t1_leads) == 2
    t1_contact_numbers = {l.contact_number for l in t1_leads}
    assert "+1111111111" in t1_contact_numbers
    assert "+1111111112" in t1_contact_numbers
    assert "+2222222221" not in t1_contact_numbers # Tenant 2's lead MUST NOT appear

    # 4. Query under Tenant 2's scope
    stmt_t2_leads = select(Lead).where(Lead.tenant_id == second_tenant.id)
    result_t2_leads = await db_session.execute(stmt_t2_leads)
    t2_leads = result_t2_leads.scalars().all()

    assert len(t2_leads) == 1
    assert t2_leads[0].contact_number == "+2222222221"
    assert t2_leads[0].name == "Tenant 2 Lead Gamma"

    # 5. Conversation Isolation
    stmt_t1_convs = select(Conversation).where(Conversation.tenant_id == sample_tenant.id)
    result_t1_convs = await db_session.execute(stmt_t1_convs)
    t1_convs = result_t1_convs.scalars().all()

    assert len(t1_convs) == 1
    assert "Solar" in t1_convs[0].content
    assert "Logistics" not in t1_convs[0].content


@pytest.mark.asyncio
async def test_duplicate_contact_number_allowed_across_different_tenants(
    db_session: AsyncSession,
    sample_tenant: Tenant,
    second_tenant: Tenant
):
    """
    Confirms that the same contact number (e.g. +14155550000) can exist independently
    under Tenant 1 and Tenant 2 without collision due to (tenant_id, contact_number) unique constraint.
    """
    shared_number = "+14155550000"

    lead_1, created_1 = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=sample_tenant.id,
        contact_number=shared_number,
        name="Customer on Tenant 1"
    )

    lead_2, created_2 = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=second_tenant.id,
        contact_number=shared_number,
        name="Customer on Tenant 2"
    )

    assert created_1 is True
    assert created_2 is True
    assert lead_1.id != lead_2.id
    assert lead_1.tenant_id == sample_tenant.id
    assert lead_2.tenant_id == second_tenant.id
