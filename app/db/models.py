import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Numeric,
    DateTime,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
    JSON
)
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class GUID(TypeDecorator):
    """
    Platform-independent GUID / UUID type.
    Uses PostgreSQL's native UUID type in production, and CHAR(36) in SQLite during testing.
    """
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError):
            return value


# Cross-dialect JSONB type
JSONType = JSON().with_variant(JSONB, "postgresql")


def utc_now():
    return datetime.now(timezone.utc)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    whatsapp_phone_number_id = Column(String(100), unique=True, nullable=False, index=True)
    whatsapp_access_token = Column(Text, nullable=True)
    webhook_secret = Column(String(255), nullable=False)
    verify_token = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    qualification_flows = relationship("QualificationFlow", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    quotes_invoices = relationship("QuoteInvoice", back_populates="tenant", cascade="all, delete-orphan")
    follow_up_jobs = relationship("FollowUpJob", back_populates="tenant", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    contact_number = Column(String(50), nullable=False)
    name = Column(String(255), nullable=True)
    stage = Column(String(50), default="greet", nullable=False) # greet, qualify, collect_budget, collect_timeline, score, route, quoted, nurture, human_handoff
    budget_signal = Column(String(255), nullable=True)
    timeline_signal = Column(String(255), nullable=True)
    qualification_score = Column(Numeric(5, 2), default=0.0, nullable=True)
    route_destination = Column(String(50), nullable=True)
    metadata_json = Column("metadata", JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "contact_number", name="uq_tenant_contact"),
        Index("idx_leads_tenant_contact", "tenant_id", "contact_number"),
        Index("idx_leads_tenant_stage", "tenant_id", "stage"),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    quotes = relationship("QuoteInvoice", back_populates="lead", cascade="all, delete-orphan")
    follow_up_jobs = relationship("FollowUpJob", back_populates="lead", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(GUID, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    whatsapp_message_id = Column(String(255), nullable=True)
    raw_payload = Column(JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("idx_conversations_tenant_lead", "tenant_id", "lead_id"),
        Index("idx_conversations_created_at", "created_at"),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    lead = relationship("Lead", back_populates="conversations")


class QualificationFlow(Base):
    __tablename__ = "qualification_flows"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    config = Column(JSONType, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="qualification_flows")


class QuoteInvoice(Base):
    __tablename__ = "quotes_invoices"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(GUID, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    status = Column(String(50), default="draft", nullable=False) # draft, sent, accepted, rejected, paid
    payload = Column(JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="quotes_invoices")
    lead = relationship("Lead", back_populates="quotes")


class FollowUpJob(Base):
    __tablename__ = "follow_up_jobs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(GUID, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id = Column(GUID, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="pending", nullable=False) # pending, executed, cancelled, failed
    task_type = Column(String(100), nullable=False) # nurture_checkin, quote_followup, payment_reminder
    payload = Column(JSONType, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="follow_up_jobs")
    lead = relationship("Lead", back_populates="follow_up_jobs")
