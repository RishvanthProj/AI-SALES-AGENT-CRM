from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class WhatsAppVerificationQuery(BaseModel):
    hub_mode: Optional[str] = Field(None, alias="hub.mode")
    hub_challenge: Optional[str] = Field(None, alias="hub.challenge")
    hub_verify_token: Optional[str] = Field(None, alias="hub.verify_token")


class WhatsAppProfile(BaseModel):
    name: Optional[str] = None


class WhatsAppContact(BaseModel):
    profile: Optional[WhatsAppProfile] = None
    wa_id: str


class WhatsAppTextMessage(BaseModel):
    body: str


class WhatsAppInteractiveReply(BaseModel):
    id: str
    title: str


class WhatsAppInteractive(BaseModel):
    type: str
    button_reply: Optional[WhatsAppInteractiveReply] = None
    list_reply: Optional[WhatsAppInteractiveReply] = None


class WhatsAppMessageItem(BaseModel):
    from_: str = Field(..., alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[WhatsAppTextMessage] = None
    interactive: Optional[WhatsAppInteractive] = None


class WhatsAppMetadata(BaseModel):
    display_phone_number: Optional[str] = None
    phone_number_id: str


class WhatsAppValue(BaseModel):
    messaging_product: str
    metadata: WhatsAppMetadata
    contacts: Optional[List[WhatsAppContact]] = None
    messages: Optional[List[WhatsAppMessageItem]] = None


class WhatsAppChange(BaseModel):
    value: WhatsAppValue
    field: str


class WhatsAppEntry(BaseModel):
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    object: str
    entry: List[WhatsAppEntry]
