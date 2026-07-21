import os
from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import Conversation, FollowUp, Lead, OutreachHistory
from schemas import (
    Analytics,
    Conversation,
    ConversationCreate,
    FollowUp,
    FollowUpCreate,
    Lead,
    LeadCreate,
    LeadUpdate,
    Outreach,
    OutreachCreate,
)
from services.ai_service import generate_lead_score, generate_outreach_message, generate_support_reply
from services.lead_scoring import score_lead_metadata
from services.messaging_service import send_email, send_twilio_message

app = FastAPI(title="Clear Web Solutions AI CRM")
app.mount("/static", StaticFiles(directory="./static"), name="static")


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=FileResponse)
def dashboard():
    return FileResponse("./static/index.html")


@app.get("/api/leads", response_model=List[Lead])
def list_leads(db: Session = Depends(get_db)):
    leads = db.query(Lead).order_by(Lead.updated_at.desc()).all()
    return leads


@app.post("/api/leads", response_model=Lead)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)):
    lead_data = payload.dict()
    score_data = score_lead_metadata(lead_data.get("rating"), lead_data.get("review_count"), lead_data.get("website"))
    lead = Lead(**lead_data, **score_data)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@app.get("/api/leads/{lead_id}", response_model=Lead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.put("/api/leads/{lead_id}", response_model=Lead)
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead


@app.post("/api/leads/{lead_id}/score", response_model=Lead)
def score_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead_data = {
        "business_name": lead.business_name,
        "category": lead.category,
        "city": lead.city,
        "rating": lead.rating,
        "review_count": lead.review_count,
        "website": lead.website,
    }
    score = generate_lead_score(lead_data)
    for key, value in score.items():
        setattr(lead, key, value)
    db.commit()
    db.refresh(lead)
    return lead


@app.post("/api/leads/{lead_id}/outreach", response_model=Outreach)
def outreach_lead(lead_id: int, payload: OutreachCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if payload.channel not in ["email", "sms", "whatsapp"]:
        raise HTTPException(status_code=400, detail="Channel must be email, sms, or whatsapp")

    outreach = OutreachHistory(
        lead_id=lead_id,
        channel=payload.channel,
        message=payload.message,
        status="pending",
        attempt_count=0,
    )
    db.add(outreach)
    db.commit()
    db.refresh(outreach)

    if payload.channel == "email" and lead.email:
        result = send_email(lead.email, "Grow your business with a website and WhatsApp integration", payload.message)
    elif payload.channel in ["sms", "whatsapp"] and lead.phone:
        result = send_twilio_message(payload.message, lead.phone, channel=payload.channel)
    else:
        result = {"success": False, "error": "Missing contact details for selected channel"}

    outreach.attempt_count += 1
    outreach.status = "sent" if result.get("success") else "failed"
    outreach.response = result.get("error") if not result.get("success") else result.get("body")
    outreach.sent_at = datetime.utcnow()
    db.commit()
    db.refresh(outreach)

    lead.last_contacted = datetime.utcnow()
    if outreach.status == "sent":
        lead.status = "contacted"
    db.commit()
    db.refresh(lead)
    return outreach


@app.post("/api/leads/{lead_id}/message", response_model=Conversation)
def record_message(lead_id: int, payload: ConversationCreate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    conversation = Conversation(**payload.dict())
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    if payload.direction == "inbound":
        lead.status = "warm"
        lead.last_contacted = datetime.utcnow()
        db.commit()
        db.refresh(lead)

    return conversation


@app.post("/api/inbound/reply")
def inbound_reply(request: Request, db: Session = Depends(get_db)):
    payload = request.json()
    text = payload.get("text")
    phone = payload.get("phone")
    if not text or not phone:
        raise HTTPException(status_code=400, detail="phone and text are required")

    lead = db.query(Lead).filter(Lead.phone == phone).order_by(Lead.updated_at.desc()).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found for phone")

    conversation = Conversation(
        lead_id=lead.id,
        channel=payload.get("channel", "sms"),
        direction="inbound",
        text=text,
        metadata=str(payload.get("metadata", "")),
    )
    db.add(conversation)
    lead.status = "warm"
    lead.last_contacted = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    db.refresh(lead)
    return {"status": "received", "lead_id": lead.id}


@app.post("/api/followups", response_model=FollowUp)
def schedule_followup(payload: FollowUpCreate, db: Session = Depends(get_db)):
    followup = FollowUp(**payload.dict(), status="scheduled")
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@app.get("/api/followups", response_model=List[FollowUp])
def list_followups(db: Session = Depends(get_db)):
    return db.query(FollowUp).order_by(FollowUp.due_date.asc()).all()


@app.get("/api/analytics", response_model=Analytics)
def analytics(db: Session = Depends(get_db)):
    total_leads = db.query(Lead).count()
    high_priority_leads = db.query(Lead).filter(Lead.priority == "high").count()
    messages_sent = db.query(OutreachHistory).filter(OutreachHistory.status == "sent").count()
    replies_received = db.query(Conversation).filter(Conversation.direction == "inbound").count()
    interested_leads = db.query(Lead).filter(Lead.status == "warm").count()
    conversion_rate = float(interested_leads) / float(total_leads) * 100.0 if total_leads else 0.0
    return Analytics(
        total_leads=total_leads,
        high_priority_leads=high_priority_leads,
        messages_sent=messages_sent,
        replies_received=replies_received,
        interested_leads=interested_leads,
        conversion_rate=round(conversion_rate, 1),
    )


@app.get("/api/outreach/message/{lead_id}")
def build_outreach_message(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    message = generate_outreach_message(
        {
            "business_name": lead.business_name,
            "category": lead.category,
            "city": lead.city,
            "website": lead.website,
        }
    )
    return {"message": message}


@app.post("/api/support/reply")
def support_reply(payload: dict, db: Session = Depends(get_db)):
    lead = None
    phone = payload.get("phone")
    if phone:
        lead = db.query(Lead).filter(Lead.phone == phone).order_by(Lead.updated_at.desc()).first()
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    reply = generate_support_reply(text, {"business_name": lead.business_name, "city": lead.city} if lead else None)
    return {"reply": reply}
