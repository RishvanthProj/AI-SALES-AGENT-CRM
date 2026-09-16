from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SalesExtraction(BaseModel):
    """
    Structured extraction of sales entities, intent, signals, and security flags
    from customer WhatsApp messages.
    """
    intent: str = Field(
        default="general_query",
        description="Core intent: greeting, product_enquiry, pricing, stock_check, general_query, "
                    "order_status, small_talk, complaint, inappropriate, off_topic, "
                    "budget_provided, timeline_provided, request_discount"
    )
    message_type: str = Field(
        default="inquiry",
        description="Type of message: greeting, inquiry, clarification, feedback, small_talk, abusive, jailbreak"
    )
    product_query: Optional[str] = Field(None, description="Product or category searched for by user")
    product_id: Optional[str] = Field(None, description="Product ID if explicitly identified")
    quantity: Optional[int] = Field(None, description="Quantity requested by user")
    budget: Optional[float] = Field(None, description="Numeric budget amount extracted")
    budget_range: Optional[str] = Field(None, description="Normalized budget string e.g. '₹3,000' or '$5k-$10k'")
    currency: str = Field(default="INR", description="Currency symbol or code (e.g. INR, USD)")
    timeline: Optional[str] = Field(None, description="Timeline requirement e.g. 'Immediately', 'Within 2 weeks'")
    is_urgent: bool = Field(default=False, description="Whether user expressed urgency")
    size: Optional[str] = Field(None, description="Size preference e.g. 'S', 'M', 'L', 'XL', '9'")
    color: Optional[str] = Field(None, description="Color preference e.g. 'black', 'blue'")
    customization_notes: Optional[str] = Field(None, description="Customization requirement or notes")
    customer_name: Optional[str] = Field(None, description="Customer name if given in message")
    requires_human: bool = Field(default=False, description="True if complex question or escalation requested")
    inappropriate_content: bool = Field(default=False, description="True if message contains abusive/vulgar/offensive language")
    is_jailbreak_attempt: bool = Field(default=False, description="True if user attempts prompt injection or system prompt reveal")
    language_detected: str = Field(default="en", description="Detected language: en, ta, tanglish, hi, etc.")
    confidence: float = Field(default=0.9, description="Extraction confidence (0.0 to 1.0)")


class GroundedResponseContext(BaseModel):
    """
    Context provided to the AI for generating natural-language copywriting
    strictly grounded in verified business facts.
    """
    business_name: str
    business_description: str
    current_stage: str
    lead_name: Optional[str] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    verified_products: List[Dict[str, Any]] = Field(default_factory=list)
    inventory_data: Optional[Dict[str, Any]] = None
    business_policies: Dict[str, Any] = Field(default_factory=dict)
    known_signals: Dict[str, Any] = Field(default_factory=dict)
    customer_message: str = ""
    language: str = "en"
    validation_notes: Optional[str] = None
