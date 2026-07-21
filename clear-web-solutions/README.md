# Clear Web Solutions AI Automation

A prototype AI-powered lead generation and outreach CRM built with FastAPI and SQLite.

## Features

- Lead capture and scoring
- AI-powered lead evaluation and outreach message generation
- Email/SMS/WhatsApp sending stubs via SMTP or Twilio
- Inbound reply tracking and warm lead marking
- Simple dashboard and analytics

## Setup

1. Copy `.env.example` to `.env` and set your credentials.
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   uvicorn app:app --reload
   ```
4. Visit `http://localhost:8000`

## Environment variables

- `OPENAI_API_KEY`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`
- `SENDGRID_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`, `TWILIO_WHATSAPP_FROM`

## Deployment

This project can be deployed to any Python hosting provider that supports FastAPI, such as Railway, Render, or Fly.io.

## Notes

- The current implementation uses SQLite for easy local development.
- The AI features require `OPENAI_API_KEY`.
- Messaging functions require SMTP or Twilio credentials.
