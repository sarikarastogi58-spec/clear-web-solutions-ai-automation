from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    business_name: str
    category: str
    city: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    rating: Optional[str] = None
    review_count: Optional[int] = None
    source: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    score: Optional[int] = None
    website_need_score: Optional[int] = None
    business_potential: Optional[int] = None
    digital_gaps: Optional[str] = None
    pitch_angle: Optional[str] = None


class Lead(LeadBase):
    id: int
    status: str
    priority: str
    score: int
    website_need_score: int
    business_potential: int
    digital_gaps: Optional[str] = None
    pitch_angle: Optional[str] = None
    last_contacted: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ContactBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    channel_preference: Optional[str] = Field(default="whatsapp")
    opted_out: Optional[bool] = False


class ContactCreate(ContactBase):
    lead_id: int


class Contact(ContactBase):
    id: int
    lead_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OutreachCreate(BaseModel):
    lead_id: int
    channel: str
    message: str


class Outreach(BaseModel):
    id: int
    lead_id: int
    channel: str
    message: str
    status: str
    attempt_count: int
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    response: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FollowUpCreate(BaseModel):
    lead_id: int
    due_date: datetime
    attempt_number: Optional[int] = 1
    notes: Optional[str] = None


class FollowUp(BaseModel):
    id: int
    lead_id: int
    due_date: datetime
    attempt_number: int
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    lead_id: int
    channel: str
    direction: str
    text: str
    metadata: Optional[str] = None


class Conversation(BaseModel):
    id: int
    lead_id: int
    channel: str
    direction: str
    text: str
    metadata: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class Analytics(BaseModel):
    total_leads: int
    high_priority_leads: int
    messages_sent: int
    replies_received: int
    interested_leads: int
    conversion_rate: float
