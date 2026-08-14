import hmac
import hashlib
from typing import Optional, Dict, Any, Tuple
import httpx
from app.config import settings
from app.schemas.whatsapp import WhatsAppWebhookPayload


class WhatsAppService:
    @staticmethod
    def verify_webhook_token(mode: Optional[str], token: Optional[str], expected_token: str) -> bool:
        """
        Verifies the Meta WhatsApp Webhook subscription token during setup.
        """
        if not mode or not token:
            return False
        return mode == "subscribe" and token == expected_token

    @staticmethod
    def verify_signature(raw_body: bytes, signature_header: Optional[str], app_secret: str) -> bool:
        """
        Verifies the X-Hub-Signature-256 header sent with incoming Meta webhooks.
        Signature format: sha256={hash}
        """
        if not signature_header or not signature_header.startswith("sha256="):
            return False

        expected_sig = signature_header.replace("sha256=", "").strip()
        computed_sig = hmac.new(
            key=app_secret.encode("utf-8"),
            msg=raw_body,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_sig, computed_sig)

    @staticmethod
    def parse_incoming_message(payload_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parses WhatsApp Business Cloud API incoming webhook payload into a normalized dict:
        {
            "phone_number_id": str,
            "contact_number": str,
            "contact_name": str,
            "message_id": str,
            "message_text": str,
            "timestamp": str,
            "raw": dict
        }
        """
        try:
            entry = payload_dict.get("entry", [])
            if not entry:
                return None

            changes = entry[0].get("changes", [])
            if not changes:
                return None

            val = changes[0].get("value", {})
            metadata = val.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")

            messages = val.get("messages", [])
            if not messages:
                # Status updates (delivered, read) or system notifications
                return None

            msg = messages[0]
            from_number = msg.get("from")
            msg_id = msg.get("id")
            timestamp = msg.get("timestamp")
            msg_type = msg.get("type")

            # Extract content from text or interactive replies
            message_text = ""
            if msg_type == "text":
                message_text = msg.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                interactive = msg.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    message_text = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    message_text = interactive.get("list_reply", {}).get("title", "")

            # Extract Contact Name
            contacts = val.get("contacts", [])
            contact_name = "WhatsApp User"
            if contacts:
                contact_name = contacts[0].get("profile", {}).get("name", "WhatsApp User")

            return {
                "phone_number_id": phone_number_id,
                "contact_number": from_number,
                "contact_name": contact_name,
                "message_id": msg_id,
                "message_text": message_text.strip(),
                "timestamp": timestamp,
                "raw": payload_dict
            }
        except Exception:
            return None

    @staticmethod
    async def send_whatsapp_message(
        phone_number_id: str,
        to_number: str,
        text_body: str,
        access_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an outbound text message to a WhatsApp user via Meta Cloud API.
        """
        url = f"{settings.WHATSAPP_API_URL}/{phone_number_id}/messages"
        token = access_token or "dummy_token_for_testing"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text_body
            }
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            return {
                "status_code": resp.status_code,
                "response": resp.json() if resp.status_code < 400 else resp.text
            }
