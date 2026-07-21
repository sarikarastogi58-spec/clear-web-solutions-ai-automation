from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(256), nullable=False)
    category = Column(String(128), nullable=False)
    city = Column(String(128), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    website = Column(String(256), nullable=True)
    rating = Column(String(16), nullable=True)
    review_count = Column(Integer, nullable=True)
    source = Column(String(128), nullable=True)
    status = Column(String(64), default="new")
    priority = Column(String(32), default="medium")
    score = Column(Integer, default=0)
    website_need_score = Column(Integer, default=0)
    business_potential = Column(Integer, default=0)
    digital_gaps = Column(Text, nullable=True)
    pitch_angle = Column(Text, nullable=True)
    last_contacted = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = relationship("Contact", back_populates="lead", cascade="all, delete-orphan")
    outreach_history = relationship("OutreachHistory", back_populates="lead", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    follow_ups = relationship("FollowUp", back_populates="lead", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    name = Column(String(128), nullable=True)
    role = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    channel_preference = Column(String(32), default="whatsapp")
    opted_out = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("Lead", back_populates="contacts")


class OutreachHistory(Base):
    __tablename__ = "outreach_history"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    channel = Column(String(32), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(32), default="pending")
    attempt_count = Column(Integer, default=0)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("Lead", back_populates="outreach_history")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    due_date = Column(DateTime, nullable=False)
    attempt_number = Column(Integer, default=1)
    status = Column(String(32), default="scheduled")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lead = relationship("Lead", back_populates="follow_ups")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    channel = Column(String(32), nullable=False)
    direction = Column(String(16), nullable=False)
    text = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="conversations")
