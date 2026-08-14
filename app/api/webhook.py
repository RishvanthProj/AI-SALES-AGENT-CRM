import json
import uuid
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException, Header, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.db.session import get_db, get_tenant_session, set_tenant_context
from app.db.models import Tenant, Lead
from app.services.whatsapp_service import WhatsAppService
from app.services.lead_service import LeadService, InvalidStageTransitionError
from app.agent.graph import sales_graph
from app.agent.state import SalesAgentState

router = APIRouter(prefix="/webhook/whatsapp", tags=["WhatsApp Webhook"])


@router.get("")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    db: AsyncSession = Depends(get_db)
):
    """
    WhatsApp Cloud API Webhook Verification (GET).
    Validates hub.verify_token and responds with the hub.challenge integer/string.
    """
    if not hub_mode or not hub_verify_token or not hub_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required hub verification parameters"
        )

    # Check global token or tenant-specific token
    is_valid = (hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN)

    if not is_valid:
        # Check tenant verify tokens
        stmt = select(Tenant).where(Tenant.verify_token == hub_verify_token)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()
        is_valid = bool(tenant)

    if is_valid and hub_mode == "subscribe":
        return Response(content=hub_challenge, media_type="text/plain", status_code=status.HTTP_200_OK)

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch"
    )


@router.post("")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    db: AsyncSession = Depends(get_db)
):
    """
    WhatsApp Cloud API Inbound Webhook Receiver (POST).
    1. Verifies Meta HMAC-SHA256 signature.
    2. Parses incoming message.
    3. Finds or creates the Lead under the matching Tenant.
    4. Executes LangGraph state machine.
    5. Dispatches reply to WhatsApp user.
    """
    raw_body = await request.body()

    # 1. Signature Verification
    # In development/test mode without app secret, permit bypass if configured
    if settings.WHATSAPP_APP_SECRET and settings.WHATSAPP_APP_SECRET != "default_app_secret_replace_me":
        is_valid_sig = WhatsAppService.verify_signature(
            raw_body=raw_body,
            signature_header=x_hub_signature_256,
            app_secret=settings.WHATSAPP_APP_SECRET
        )
        if not is_valid_sig:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid webhook HMAC signature (X-Hub-Signature-256 mismatch)"
            )

    # 2. Parse payload
    try:
        payload_dict = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    parsed = WhatsAppService.parse_incoming_message(payload_dict)
    if not parsed:
        # Acknowledge non-message event (e.g. status receipts, read confirmations)
        return {"status": "ignored", "reason": "No actionable incoming user message"}

    phone_number_id = parsed["phone_number_id"]
    contact_number = parsed["contact_number"]
    contact_name = parsed["contact_name"]
    message_text = parsed["message_text"]
    msg_id = parsed["message_id"]

    # 3. Tenant Lookup
    stmt = select(Tenant).where(Tenant.whatsapp_phone_number_id == phone_number_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()

    if not tenant:
        # Create a default fallback tenant if none exists (for testing/setup)
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Default WhatsApp Tenant",
            whatsapp_phone_number_id=phone_number_id,
            webhook_secret=settings.WHATSAPP_APP_SECRET,
            verify_token=settings.WHATSAPP_VERIFY_TOKEN,
            is_active=True
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    # 4. Process within Tenant Context
    await set_tenant_context(db, tenant.id)

    # Find or create lead for this contact number
    lead, created = await LeadService.get_or_create_lead(
        session=db,
        tenant_id=tenant.id,
        contact_number=contact_number,
        name=contact_name
    )

    # Record incoming message
    await LeadService.record_conversation(
        session=db,
        tenant_id=tenant.id,
        lead_id=lead.id,
        role="user",
        content=message_text,
        whatsapp_message_id=msg_id,
        raw_payload=payload_dict
    )

    # Prepare LangGraph state
    initial_state: SalesAgentState = {
        "tenant_id": str(tenant.id),
        "lead_id": str(lead.id),
        "contact_number": contact_number,
        "lead_name": lead.name,
        "current_stage": lead.stage,
        "incoming_message": message_text,
        "need_summary": lead.metadata_json.get("need_summary"),
        "budget_signal": lead.budget_signal,
        "timeline_signal": lead.timeline_signal,
        "qualification_score": float(lead.qualification_score or 0.0),
        "route_destination": lead.route_destination,
        "reply_text": "",
        "history": [],
        "error": None
    }

    # Execute LangGraph state machine
    final_state = sales_graph.invoke(initial_state)

    # Extract updated state signals
    updated_budget = final_state.get("budget_signal")
    updated_timeline = final_state.get("timeline_signal")
    updated_score = final_state.get("qualification_score", 0.0)
    route_dest = final_state.get("route_destination")
    reply_text = final_state.get("reply_text", "Thank you for reaching out!")

    # Update lead record with validated state
    target_stage = route_dest if route_dest else final_state.get("current_stage", "qualify")

    try:
        await LeadService.transition_stage(
            session=db,
            lead=lead,
            new_stage=target_stage,
            budget_signal=updated_budget,
            timeline_signal=updated_timeline,
            qualification_score=updated_score,
            route_destination=route_dest
        )
    except InvalidStageTransitionError:
        # Enforce fallback if constraint fails
        target_stage = "collect_budget"
        await LeadService.transition_stage(
            session=db,
            lead=lead,
            new_stage=target_stage,
            budget_signal=None,
            timeline_signal=updated_timeline,
            qualification_score=updated_score
        )

    # Record assistant reply
    await LeadService.record_conversation(
        session=db,
        tenant_id=tenant.id,
        lead_id=lead.id,
        role="assistant",
        content=reply_text,
        raw_payload={"stage": target_stage, "score": updated_score}
    )

    await db.commit()

    # Send outbound message to WhatsApp user if token configured
    if tenant.whatsapp_access_token:
        await WhatsAppService.send_whatsapp_message(
            phone_number_id=phone_number_id,
            to_number=contact_number,
            text_body=reply_text,
            access_token=tenant.whatsapp_access_token
        )

    return {
        "status": "processed",
        "lead_id": str(lead.id),
        "contact_number": contact_number,
        "stage": lead.stage,
        "qualification_score": float(lead.qualification_score or 0.0),
        "budget_signal": lead.budget_signal,
        "timeline_signal": lead.timeline_signal,
        "route_destination": lead.route_destination,
        "reply_sent": reply_text
    }
