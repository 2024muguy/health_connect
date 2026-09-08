
## docs/API_Documentation.md

```markdown
# HealthConnect AI - API Documentation

## Base URL
http://localhost:8000/api/v1

text

## Authentication

### POST /auth/register
Register new user.

### POST /auth/login
Login and get tokens.

### POST /auth/refresh
Refresh access token.

## Chat

### POST /chat/message
Send message and get AI response.

**Request:**
```json
{
  "message": "How do I book an appointment?",
  "conversation_id": null,
  "session_token": "optional"
}
Response:

json
{
  "conversation_id": "CONV-ABC12345",
  "message": "To book an appointment...",
  "intent": "appointment_booking",
  "confidence": 0.85
}
Appointments
GET /appointments
List appointments.

POST /appointments
Create appointment.

POST /appointments/{id}/cancel
Cancel appointment.

Escalations
POST /escalations
Create escalation.

GET /escalations
List escalations (admin).

Admin
GET /admin/stats
Get dashboard statistics (admin).

Analytics
GET /analytics/metrics
Get metrics (admin).

