import hmac
import hashlib
import json
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import settings
from app.services.whatsapp_service import WhatsAppService


@pytest.mark.asyncio
async def test_webhook_get_verification_handshake():
    """
    Test WhatsApp Cloud API Webhook Subscription Verification (GET).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Valid handshake
        response = await client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
                "hub.challenge": "1158201444"
            }
        )
        assert response.status_code == 200
        assert response.text == "1158201444"

        # 2. Invalid verify token
        invalid_response = await client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token_xyz",
                "hub.challenge": "1158201444"
            }
        )
        assert invalid_response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_hmac_signature_verification():
    """
    Test X-Hub-Signature-256 HMAC verification.
    """
    raw_payload = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode("utf-8")
    app_secret = "test_secret_key_123"

    # Compute valid signature
    valid_sig = "sha256=" + hmac.new(
        key=app_secret.encode("utf-8"),
        msg=raw_payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    assert WhatsAppService.verify_signature(raw_payload, valid_sig, app_secret) is True
    assert WhatsAppService.verify_signature(raw_payload, "sha256=invalid_hash", app_secret) is False
    assert WhatsAppService.verify_signature(raw_payload, None, app_secret) is False


@pytest.mark.asyncio
async def test_webhook_post_incoming_message_creates_lead():
    """
    Test that an inbound WhatsApp message automatically creates a lead record
    if one doesn't exist for that contact number.
    """
    transport = ASGITransport(app=app)
    contact_number = "+14155557766"
    phone_number_id = "109876543210"

    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+16505551111",
                                "phone_number_id": phone_number_id
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Morgan Davis"},
                                    "wa_id": "14155557766"
                                }
                            ],
                            "messages": [
                                {
                                    "from": contact_number,
                                    "id": "wamid.HBgLMTQxNTU1NTc3NjYVAgASGBQzQTkyREI4...",
                                    "timestamp": "1723680000",
                                    "text": {
                                        "body": "Hi, we are looking for enterprise cloud migration services."
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    raw_payload = json.dumps(webhook_payload, separators=(",", ":")).encode("utf-8")
    signature = "sha256=" + hmac.new(
        key=settings.WHATSAPP_APP_SECRET.encode("utf-8"),
        msg=raw_payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhook/whatsapp",
            content=raw_payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature,
            },
        )

        assert response.status_code == 200
        res_data = response.json()
        assert res_data["status"] == "processed"
        assert res_data["contact_number"] == contact_number
        assert res_data["lead_id"] is not None
        assert res_data["reply_sent"] is not None
