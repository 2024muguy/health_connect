
## Week 7 — Generative AI Track

**Focus:** Testing → Refinement → End-to-End Validation.

Key result: from a base RAG prototype (Week 6) to a **fully connected
assistant** with memory, streaming, conversational booking, escalation
short-circuit, and a 7-layer safety stack.

### Week 7 deliverables

- [`backend/docs/week7/W7_Project_Summary.md`](backend/docs/week7/W7_Project_Summary.md)
- [`backend/docs/week7/W7_Testing_Report.md`](backend/docs/week7/W7_Testing_Report.md)
- [`backend/docs/week7/W7_Visualizations.md`](backend/docs/week7/W7_Visualizations.md)
- [`backend/docs/week7/figures/`](backend/docs/week7/figures/) — 8 diagrams

### Verified in Week 7

- 15-turn memory recall (name, allergies persist)
- 4-turn conversational booking (real APT code in DB)
- 6-turn escalation state machine (no pollution)
- SSE streaming (curl + browser + app)
- 7/7 adversarial injection patterns blocked
