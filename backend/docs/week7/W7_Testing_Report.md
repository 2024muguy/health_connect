# Week 7 Testing Report — Generative AI Track

Every Week 7 test documented as **Test → Finding → Fix → Retest → Evidence**.

---

## T1. Booking flow crashes on insert

| Field | Value |
|---|---|
| **Component** | AppointmentService |
| **Scenario** | Chat booking → `create_appointment` |
| **Expected** | Appointment row inserted, `APT-XXXX` returned |
| **Actual** | `AttributeError: 'str' object has no attribute 'hex'` |
| **Issue** | `patient_id` passed as Python `str` to a SQLAlchemy `UUID(as_uuid=True)` column |
| **Fix** | Coerce with `uuid.UUID(patient_id)` before constructing the ORM row |
| **Retest** | `APT-3EE571AA` created and visible in DB |

---

## T2. New conversation created on every turn

| Field | Value |
|---|---|
| **Component** | ChatService |
| **Scenario** | 15-turn conversation with a single `session_token` |
| **Expected** | One conversation row, history persists |
| **Actual** | 5 separate conversation rows for 15 turns — memory never fired |
| **Issue** | `_create_conversation` inserted without checking existing rows by session_token |
| **Fix** | Idempotent creation: lookup by `session_token` first, reuse or insert |
| **Retest** | Single row after 15 turns; rolling summary and facts persisted |

---

## T3. Memory block ignored by LLM

| Field | Value |
|---|---|
| **Component** | ConversationAgent system prompt |
| **Scenario** | "What is my name and what am I allergic to?" after prior facts |
| **Expected** | "Your name is David and you're allergic to aspirin" |
| **Actual** | KB chunk echoed instead |
| **Issue** | System prompt forbade using non-KB content |
| **Fix** | Rule 5 added: authorize prior-conversation block as authoritative for user facts |
| **Retest** | Correct answer returned across multiple runs |

---

## T4. Session_token UNIQUE constraint violation

| Field | Value |
|---|---|
| **Component** | ChatService `_ensure_conversation_db` |
| **Scenario** | SSE request triggering two writes with the same session_token |
| **Expected** | Reuse existing conversation |
| **Actual** | `sqlite3.IntegrityError: UNIQUE constraint failed: conversations.session_token` |
| **Fix** | Lookup by `session_token` before insert in `_ensure_conversation_db` |
| **Retest** | No more UNIQUE errors, SSE requests succeed |

---

## T5. Escalation not triggering on common phrasings

| Field | Value |
|---|---|
| **Component** | ChatService booking/escalation short-circuit |
| **Scenario** | "connect me" after out-of-scope question |
| **Expected** | `requires_human=True` |
| **Actual** | Polite repeat of the same offer |
| **Issue** | Escalation intent set was narrow; didn't include conversational phrasings |
| **Fix** | Expanded trigger set to 17+ phrasings |
| **Retest** | "connect me" and "why arent you connecting me" both return `requires_human=True` |

---

## T6. `_pending_escalations` NameError

| Field | Value |
|---|---|
| **Component** | ChatService `process_message` |
| **Scenario** | Turn 3 of escalation test |
| **Expected** | Continue escalation |
| **Actual** | `NameError: name 'pending' is not defined` |
| **Issue** | Partial patch replaced one reference, left another |
| **Fix** | Module-level `_PENDING_ESCALATIONS` dict; all references normalized |
| **Retest** | 6-turn escalation test: 5/6 correct (final fix in T7) |

---

## T7. Pending escalation cleared too eagerly

| Field | Value |
|---|---|
| **Component** | ChatService escalation short-circuit |
| **Scenario** | "yes" after escalation |
| **Expected** | Confirm escalation again |
| **Actual** | LLM asked "Would you like me to connect you?" |
| **Issue** | Flag popped immediately after escalation |
| **Fix** | Keep flag set; auto-expire only on bare confirmation (`yes`/`ok`/`sure`) |
| **Retest** | 6-turn test: 6/6 correct |

---

## T8. Weekday not parsed for booking

| Field | Value |
|---|---|
| **Component** | BookingService `_rule_extract` |
| **Scenario** | "saturday at 11am" |
| **Expected** | Resolve to next Saturday's ISO date |
| **Actual** | No date extracted |
| **Fix** | Added weekday resolver mapping to next occurrence |
| **Retest** | `date=2026-09-19`, `time=11:00` extracted |

---

## T9. SSE streaming returns 500

| Field | Value |
|---|---|
| **Component** | `/chat/message/stream` endpoint |
| **Scenario** | Any streaming query |
| **Expected** | SSE frames stream to browser |
| **Actual** | 500 — `AttributeError: 'NoneType' object has no attribute 'get'` |
| **Issue** | `retrieval_result.output` was `None` when 0 chunks retrieved |
| **Fix** | Guard `_out(r) = r.output or {}` in `orchestrator._assemble_response` |
| **Retest** | SSE returns 200 with `text/event-stream`, frames stream |

---

## T10. Frontend streaming never reached the browser

| Field | Value |
|---|---|
| **Component** | `src/lib/api.ts` → `sendMessageStream` |
| **Scenario** | Chat streaming UI |
| **Expected** | Chunks render progressively |
| **Actual** | Browser hit a Next.js rewrite URL that buffered SSE |
| **Fix** | Frontend calls backend directly: `${NEXT_PUBLIC_API_URL}/chat/message/stream` |
| **Retest** | `curl`, browser console, and app all see chunk-by-chunk output |

---

## T11. Response duplication in chat UI

| Field | Value |
|---|---|
| **Component** | Zustand `chat-store.addMessage` |
| **Scenario** | SSE chunks arriving one at a time |
| **Expected** | Single bubble that updates |
| **Actual** | Every chunk appended → bubble repeated 8× |
| **Fix** | `addMessage` replaces by `id` if already present |
| **Retest** | Single bubble types in progressively; no React key warning |

---

## T12. Terminal mojibake `â€"`

| Field | Value |
|---|---|
| **Component** | Windows Git Bash display |
| **Scenario** | Reading chat responses in terminal |
| **Expected** | Clean Unicode em dashes and narrow spaces |
| **Actual** | `â€"`, `â€¯` shown |
| **Investigation** | Python-native response capture shows `U+2013`, `U+202F` — correct |
| **Conclusion** | NON-ISSUE: terminal display artifact, not API bug |
| **Retest** | Browser shows clean Unicode |

---

## Summary

| Status | Count |
|---|---|
| Total tests | 12 |
| Real issues fixed | 10 |
| Non-issues verified | 1 |
| Documentation fixes | 1 |

Full raw evidence in `evidence/`.
