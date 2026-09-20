# Week 7 GenAI Visualizations

All figures are generated from code in `backend/scripts/generate_week7_diagrams.py`.
They are deterministic and reproducible.

---

## 1. Pipeline architecture

![Pipeline](figures/01_pipeline_architecture.png)

Every stage in one diagram: input guard → booking/escalation short-circuit →
orchestrator → RAG retrieval + memory → Groq generation → response with
citations, `requires_human`, and confidence gate.

---

## 2. Feature coverage radar

![Radar](figures/02_feature_radar.png)

Week 5 shipped the base RAG. Week 7 shipped memory, streaming, booking,
escalation short-circuit, safety layers, KB cleanup, multi-turn coherence,
and tool use.

---

## 3. Latency budget

![Latency](figures/03_latency_budget.png)

Measured during the Week 7 live demo. SSE first-token is 0.45s; total
median turn 4.0s. The classifier step (1.5s) is the biggest fixed cost.

---

## 4. Safety layer stack

![Safety](figures/04_safety_layers.png)

Seven independent safety layers protect every turn — no single layer
is trusted to be sufficient.

---

## 5. KB cleanup waterfall

![KB](figures/05_kb_cleanup.png)

Removed 31 noisy chunks (metadata, data dictionary, raw appointment stats,
short fragments). Kept 12 patient-facing chunks.

---

## 6. Conversational booking flow

![Booking](figures/06_booking_flow.png)

Real 4-turn transcript from the Week 7 test. Assistant collects service,
location, contact method, date, time, and calls the shared appointment API.

---

## 7. Escalation state machine

![Escalation](figures/07_escalation_fsm.png)

Shows the fail-safe pending-flag design: set on any escalation phrase,
survives the turn, and auto-expires after a bare confirmation. No state
pollution — a normal KB query still works after escalation.

---

## 8. Feature delivery heatmap

![Heatmap](figures/08_test_heatmap.png)

Progression across three weeks by test category. Every category moved
from ✗ or – to ✓.

---

## Product screenshots

### Chat interface
![Chat interface](figures/screenshot_chat.png)

*Screenshot: chat with streamed reply, memory badge, and confidence indicator.*

### Appointment booking
![Booking](figures/screenshot_booking.png)

*Screenshot: appointment detail page with the new appointment code.*

### Dashboard
![Dashboard](figures/screenshot_dashboard.png)

*Screenshot: Next.js dashboard showing appointments, notifications, and chat entry.*
