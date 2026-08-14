import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LeadBase(BaseModel):
    contact_number: str
    name: Optional[str] = None
    stage: str = "greet"
    budget_signal: Optional[str] = None
    timeline_signal: Optional[str] = None
    qualification_score: Optional[float] = 0.0
    route_destination: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LeadCreate(LeadBase):
    tenant_id: uuid.UUID


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    stage: Optional[str] = None
    budget_signal: Optional[str] = None
    timeline_signal: Optional[str] = None
    qualification_score: Optional[float] = None
    route_destination: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LeadResponse(LeadBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StageTransitionRequest(BaseModel):
    new_stage: str
    budget_signal: Optional[str] = None
    timeline_signal: Optional[str] = None
