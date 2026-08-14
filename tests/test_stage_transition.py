import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Tenant, Lead
from app.services.lead_service import LeadService, InvalidStageTransitionError


@pytest.mark.asyncio
async def test_lead_cannot_transition_to_quoted_without_budget_signal(
    db_session: AsyncSession,
    sample_tenant: Tenant
):
    """
    Test Requirement:
    Confirm a lead CANNOT transition to the 'quoted' state without a populated budget_signal field.
    """
    # 1. Create a lead in initial stage with NO budget signal
    lead, created = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=sample_tenant.id,
        contact_number="+14155552671",
        name="Alex Smith"
    )
    assert created is True
    assert lead.stage == "greet"
    assert lead.budget_signal is None

    # 2. Attempt to transition to 'quoted' stage without budget_signal
    with pytest.raises(InvalidStageTransitionError) as exc_info:
        await LeadService.transition_stage(
            session=db_session,
            lead=lead,
            new_stage="quoted",
            budget_signal=None
        )

    # 3. Verify exception details
    assert "cannot transition to 'quoted' state without a populated budget_signal" in str(exc_info.value)
    assert lead.stage != "quoted"

    # 4. Attempt to transition with an empty whitespace string as budget_signal
    with pytest.raises(InvalidStageTransitionError) as exc_info_empty:
        await LeadService.transition_stage(
            session=db_session,
            lead=lead,
            new_stage="quoted",
            budget_signal="   "
        )
    assert "cannot transition to 'quoted' state without a populated budget_signal" in str(exc_info_empty.value)

    # 5. Now provide a valid, populated budget_signal and verify the transition succeeds
    valid_budget = "$15,000 - $25,000 USD"
    updated_lead = await LeadService.transition_stage(
        session=db_session,
        lead=lead,
        new_stage="quoted",
        budget_signal=valid_budget,
        timeline_signal="Within 30 days",
        qualification_score=85.0
    )

    assert updated_lead.stage == "quoted"
    assert updated_lead.budget_signal == valid_budget
    assert updated_lead.timeline_signal == "Within 30 days"
    assert float(updated_lead.qualification_score) == 85.0


@pytest.mark.asyncio
async def test_lead_with_existing_budget_signal_can_transition_to_quoted(
    db_session: AsyncSession,
    sample_tenant: Tenant
):
    """
    Confirm that if budget_signal was already saved in a previous turn,
    transition to 'quoted' succeeds without re-passing the argument.
    """
    lead, _ = await LeadService.get_or_create_lead(
        session=db_session,
        tenant_id=sample_tenant.id,
        contact_number="+14155559988",
        name="Jordan Lee"
    )
    # Collect budget during collect_budget stage
    await LeadService.transition_stage(
        session=db_session,
        lead=lead,
        new_stage="collect_budget",
        budget_signal="$50,000 Enterprise"
    )
    assert lead.budget_signal == "$50,000 Enterprise"

    # Now transition to 'quoted'
    updated = await LeadService.transition_stage(
        session=db_session,
        lead=lead,
        new_stage="quoted"
    )
    assert updated.stage == "quoted"
    assert updated.budget_signal == "$50,000 Enterprise"
