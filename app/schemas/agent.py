from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NeedExtraction(BaseModel):
    summary: str = Field(description="Summary of the customer's stated requirement or problem")
    category: Optional[str] = Field(None, description="Category of service or product requested")
    clarity_score: float = Field(default=0.8, description="Confidence score of the extracted need (0.0 to 1.0)")


class BudgetExtraction(BaseModel):
    raw_text: str = Field(description="Raw text mentioning budget")
    budget_range: Optional[str] = Field(None, description="Normalized budget range or amount, e.g. '$5k-$10k', '2000 USD'")
    is_provided: bool = Field(description="Whether a valid budget was indicated")
    confidence: float = Field(default=0.9, description="Extraction confidence (0.0 to 1.0)")


class TimelineExtraction(BaseModel):
    raw_text: str = Field(description="Raw text mentioning timeline")
    timeline_str: Optional[str] = Field(None, description="Normalized timeline, e.g. 'Immediately', 'Within 2 weeks', 'Next month'")
    is_provided: bool = Field(description="Whether a target timeframe was indicated")
    is_urgent: bool = Field(default=False, description="Whether the request is urgent")
    confidence: float = Field(default=0.9, description="Extraction confidence (0.0 to 1.0)")


class NodeLanguageOutput(BaseModel):
    reply_text: str = Field(description="Conversational response tailored for WhatsApp (concise, professional, engaging)")
    suggested_quick_replies: Optional[List[str]] = Field(default_factory=list, description="Optional quick-reply button suggestions")
