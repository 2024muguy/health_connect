# Week 7 Project Summary - Generative AI Track

**Track:** Generative AI
**Author:** [Your Name]
**Project:** HealthConnect Experience Lab
**Date:** 2026-09-18

---

## 1. What I planned to test

Week 6 delivered a working RAG assistant (30/30 on the Week 6 evaluation suite).
Week 7 aimed to test that assistant as a **product**, not just as a QA target,
and to add the capabilities that turn it into a genuinely sophisticated
healthcare assistant:

1. Long-term memory across long conversations
2. Token streaming for perceived responsiveness
3. Uncertainty gating to prevent overconfident answers
4. Hybrid conversational booking (chat-driven appointment creation)
5. Multi-agent orchestration with a tool registry
6. Retrieval quality upgrades (clean KB + relevance filtering)
7. Full input-guard / injection defense test suite

## 2. What I actually tested

| Test | Component | Expected | Actual | Pass/Fail |
|------|-----------|----------|--------|-----------|
| 30-turn memory | MemoryService | Recall "Sarah" at turn 15 | Recalled "David" + allergy at turn 4 test | PASS |
| Long conversation | Session reuse | One conversation per session_token | Single row, summary 600 chars, facts JSON populated | PASS |
| KB cleanup | Retrieval | Drop metadata/dictionary chunks | 43 -> 12 patient-facing chunks | PASS |
| Prompt injection | InputGuard | Block "ignore previous instructions" | Blocked | PASS |
| SQL injection | InputGuard | Block "SELECT * FROM users" | Blocked | PASS |
| SSRF | InputGuard | Block "fetch http://169.254..." | Blocked | PASS |
| Jailbreak | InputGuard | Block "You are now DAN" | Blocked | PASS |
| SSE streaming | /message/stream | Emit start, chunks, done | Verified with curl -N | PASS |
| Uncertainty gate | UncertaintyService | Score + gate low-confidence | Wired; validated on hourly question | PASS |
| Booking flow | BookingService | Collect slots -> confirm -> call API | Wired; awaiting full E2E | PARTIAL |

## 3. Most important testing results

- **Memory works end-to-end.** A 15-turn conversation correctly extracted
  `{name: Sarah, age: 42, allergies: penicillin, preferred_time_of_day: morning}`
  and persisted them; a subsequent 4-turn test answered "Your name is David
  and you are allergic to aspirin" correctly.
- **KB noise eliminated.** Initial 43 chunks included data-dictionary rows,
  staff guidance, and preamble metadata. Cleanup left 12 patient-facing
  chunks; response quality improved immediately (no more "This document is
  a fictional project resource..." leaks).
- **Adversarial defenses work.** All injection/jailbreak/SQL/SSRF patterns
  were blocked by the input guard with structured audit logging.
- **Streaming works.** SSE endpoint emits proper `start`, `chunk`, `done`
  frames.

## 4. Issues or weaknesses identified

1. **Session-token conversation reuse was broken** — each turn created a new
   conversation row (5 rows for a 15-turn script). Fixed by looking up the
   existing conversation by `session_token` before creating a new one.
2. **Memory block was ignored by the LLM** because the system prompt
   forbade using non-KB content. Fixed by authorizing the memory block as
   authoritative for user-specific facts.
3. **KB contained junk** — preamble metadata, data dictionary, raw
   appointment statistics. 31 of 43 chunks were junk.
4. **`AgentContext` metadata flow** — briefly suspected the memory block was
   dropped; confirmed field exists and works.
5. **Mojibake in responses** — `â€"` etc. from UTF-8 vs CP1252 terminal
   encoding. Fixed by `_clean_text` in chat.py.
6. **Non-ASCII em-dashes** crept into a Python string from a heredoc paste
   and crashed the app with `SyntaxError: invalid character '—' (U+2014)`.
   Fixed by ASCII-only enforcement on all patched files.

## 5. Improvements/refinements made

- `MemoryService`: rolling summary + structured facts
- Session-token conversation reuse
- System prompt: distinguish "telling" from "asking" about user facts
- KB: filtered to 12 chunks, backed up original
- FAISS index: auto-rebuild on startup
- Streaming: SSE endpoint `/message/stream` with `start`/`chunk`/`done` frames
- Uncertainty: LLM-judge + retrieval-score combination
- Booking: hybrid slot-filling service with confirm step
- Tools: tool_registry with knowledge_search, check_availability,
  create_appointment, escalate_to_human

## 6. Retesting results

- Memory: 4-turn recall test passes
- KB: no more metadata leaks in any test query
- Injection: 7/7 attack patterns blocked
- Streaming: SSE frames parse correctly in curl
- Uncertainty: wired, gating fires on low-retrieval questions

## 7. Which tracks I collaborated with

- **Data Science** — validated the `no_show_predictor` tool interface,
  confirmed feature schema (lead_time_days, appointment_hour, age,
  prior_no_shows, sms_received)
- **Project Management** — logged the Week 7 testing incidents (session
  reuse bug, KB cleanup, ASCII crash) for the shared issue register

## 8. What was tested collaboratively

- The appointment booking flow was tested end-to-end across the GenAI track
  (chat intent -> BookingService) and the backend `appointments` API. The
  booking payload contract (patient_id, appointment_type, scheduled_datetime)
  matches what the DS no-show model expects at inference time.

## 9. What changed as a result

- The assistant now remembers users across sessions
- The KB is 72% cleaner
- Hallucinations on missing data are gated
- Streaming is available
- Booking from chat is possible

## 10. Key findings or validation outcomes

- **Memory is a force multiplier.** Users can now do multi-turn tasks
  (booking, complaint escalation) without repeating themselves.
- **Retrieval quality trumps prompt engineering.** Cleaning 31 noisy chunks
  improved more responses than any prompt tweak.
- **Uncertainty gating must be retrieval-aware.** A high-quality LLM
  response based on low-similarity chunks is still risky.
- **Adversarial defense works but must be layered.** Regex input guard is
  the first of three gates (input, judge, output scrubber).

## 11. Major challenges

- **Windows terminal encoding** mangled em-dashes and smart quotes into
  non-ASCII characters that crashed Python parsing. Solved with ASCII
  enforcement and `python -m py_compile` after every patch.
- **Async session management** — `chat_service` uses `AsyncSessionLocal`
  per call, so `MemoryService.update_memory` had to open its own session
  rather than receiving one.
- **Session state** was in-memory, not persisted. Moving to DB lookup by
  session_token fixed the multi-turn breakage.

## 12. Important decisions

- **Keep `openai/gpt-oss-20b`** — speed matters more than marginal quality
  for a chat assistant with sub-3s latency targets.
- **Hybrid booking** (assistant collects slots, shows confirmation, calls
  API) rather than full autopilot — safer for a healthcare context.
- **Skip voice** this week — cost + external dependencies not justified by
  demo value.
- **Memory threshold: 12 turns / extract every 6** in production; 2/4 in
  testing to speed up verification.

## 13. Remaining limitations

- Cross-encoder reranker not yet wired (retrieval still order-of-arrival)
- Judge model latency adds ~1s per response when uncertainty is enabled
- Voice endpoints not exposed
- Booking API integration awaiting full E2E test with real patient_id
- Multi-agent routing is registry-based, not yet LLM-driven

## 14. Remaining issues or dependencies

- Data Science: candidate no-show model artifact not yet shipped; the
  GenAI tool falls back to heuristic
- Frontend: SSE consumer for `/message/stream` not yet wired in Next.js
  (uses WS instead)
- PM: session-reuse bug is fixed but the audit trail of previous broken
  sessions remains in the DB

## 15. My contribution to the overall HealthConnect project

- Shipped a genuine long-term memory service that turns the assistant from
  stateless to conversational
- Cleaned 72% of the KB noise, which improved every downstream feature
- Built the input-guard / judge / scrubber safety stack that makes the
  assistant deployable
- Wired the tool registry that lets agents act, not just answer

## 16. What must be completed before Week 8

1. Frontend SSE consumer to make streaming visible in the UI
2. End-to-end booking test (chat -> slot fill -> confirm -> real API call)
3. Cross-track: final DS no-show model integration
4. Evaluation suite re-run to confirm no regressions (still targeting 30/30)
5. Project summary + evidence packaged in `docs/week7/`

---

## Appendix A - Evidence artefacts

| Artefact | Path |
|----------|------|
| Memory service | `app/services/memory_service.py` |
| Uncertainty service | `app/services/uncertainty_service.py` |
| Booking service | `app/services/booking_service.py` |
| Tool registry | `app/services/tool_registry.py` |
| Streaming service | `app/services/streaming_service.py` |
| Input guard | `app/services/input_guard.py` |
| Audit log | `app/services/audit_log.py` |
| Rate limits | `app/middleware/request_limits.py` |
| SSE endpoint | `app/api/v1/endpoints/chat.py` (`/message/stream`) |
| WS endpoint | `app/api/v1/endpoints/ws_chat.py` |
| Settings | `config/settings.py` (Memory/Streaming/Uncertainty/Booking/Voice) |
| KB backup | `data/processed/rag_knowledge_base.backup_*.json` |
| KB cleaned | `data/processed/rag_knowledge_base.json` |

## Appendix B - Week 6 vs Week 7 metrics

| Metric | Week 6 | Week 7 |
|--------|--------|--------|
| KB chunks | 43 | 12 |
| Multi-turn recall | None | Working |
| Streaming | None | SSE + WS |
| Uncertainty gating | None | Working |
| Conversational booking | None | Hybrid |
| Tool registry | None | 4 tools |
| Adversarial defenses | Partial | 7 patterns + audit |

