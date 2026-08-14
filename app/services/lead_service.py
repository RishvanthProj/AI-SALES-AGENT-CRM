import uuid
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Lead, Conversation


class InvalidStageTransitionError(ValueError):
    """Raised when an illegal lead stage transition is attempted."""
    pass


class LeadService:
    VALID_STAGES = [
        "greet",
        "qualify",
        "collect_budget",
        "collect_timeline",
        "score",
        "route",
        "quoted",
        "nurture",
        "human_handoff"
    ]

    @staticmethod
    async def get_or_create_lead(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        contact_number: str,
        name: Optional[str] = None
    ) -> Tuple[Lead, bool]:
        """
        Looks up an existing lead for the given contact number within the tenant's RLS scope,
        or creates a new lead initialized in the 'greet' stage.
        """
        stmt = select(Lead).where(
            Lead.tenant_id == tenant_id,
            Lead.contact_number == contact_number
        )
        result = await session.execute(stmt)
        lead = result.scalar_one_or_none()

        if lead:
            if name and not lead.name:
                lead.name = name
                await session.flush()
            return lead, False

        # Create new lead record
        lead = Lead(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            contact_number=contact_number,
            name=name,
            stage="greet",
            metadata_json={}
        )
        session.add(lead)
        await session.flush()
        return lead, True

    @staticmethod
    def validate_stage_transition(lead: Lead, new_stage: str, budget_signal: Optional[str] = None) -> None:
        """
        Validates business rules for stage transitions.
        CRITICAL RULE: A lead cannot transition to the 'quoted' state without a populated budget_signal.
        """
        if new_stage not in LeadService.VALID_STAGES:
            raise InvalidStageTransitionError(f"Invalid target stage '{new_stage}'. Must be one of {LeadService.VALID_STAGES}")

        effective_budget = budget_signal or lead.budget_signal

        # Core constraint check
        if new_stage == "quoted":
            if not effective_budget or not str(effective_budget).strip():
                raise InvalidStageTransitionError(
                    f"Lead {lead.id} cannot transition to 'quoted' state without a populated budget_signal field."
                )

    @staticmethod
    async def transition_stage(
        session: AsyncSession,
        lead: Lead,
        new_stage: str,
        budget_signal: Optional[str] = None,
        timeline_signal: Optional[str] = None,
        qualification_score: Optional[float] = None,
        route_destination: Optional[str] = None
    ) -> Lead:
        """
        Applies a validated stage transition to the lead.
        """
        # Validate constraints before applying
        LeadService.validate_stage_transition(lead, new_stage, budget_signal)

        lead.stage = new_stage

        if budget_signal:
            lead.budget_signal = budget_signal
        if timeline_signal:
            lead.timeline_signal = timeline_signal
        if qualification_score is not None:
            lead.qualification_score = qualification_score
        if route_destination:
            lead.route_destination = route_destination

        await session.flush()
        return lead

    @staticmethod
    async def record_conversation(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        lead_id: uuid.UUID,
        role: str,
        content: str,
        whatsapp_message_id: Optional[str] = None,
        raw_payload: Optional[Dict[str, Any]] = None
    ) -> Conversation:
        """
        Persists a conversation message turn into the database.
        """
        conversation = Conversation(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            lead_id=lead_id,
            role=role,
            content=content,
            whatsapp_message_id=whatsapp_message_id,
            raw_payload=raw_payload or {}
        )
        session.add(conversation)
        await session.flush()
        return conversation

