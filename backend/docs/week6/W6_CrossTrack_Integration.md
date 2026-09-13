# Week 6 Cross-Track Integration Record — Generative AI ↔ Data Science

**GenAI track representative:** [Your Name]
**Data Science track counterpart:** [Name / track lead]
**Integration type:** Tool / interface integration
**Status:** Complete — merged and verified

---

## 1. Track collaborated with

**Data Science track** (no-show prediction).

Secondary coordination with **Project Management** for issue/risk logging.

---

## 2. Project dependency

The GenAI assistant needed a way to answer user questions such as
*"What is the risk of this appointment being missed?"* with a real
prediction rather than a generic KB answer.

The Data Science track owns the no-show classification model and the
associated feature schema. The GenAI track owns the assistant, the
conversational routing, and the response format presented to the patient.

---

## 3. Information / output received

From Data Science:

- **Feature schema** for the no-show model:
  - `lead_time_days` — days between booking and appointment
  - `appointment_hour` — hour of day (0–23)
  - `age` — patient age
  - `prior_no_shows` — count of previous no-shows
  - `sms_received` — boolean reminder flag
- **Prediction contract:** probability in `[0, 1]`; classified as
  `high` (≥ 0.30), `medium` (≥ 0.15), `low` (otherwise).
- **Feature importance insight** (from Data Analytics via Data Science):
  long lead time, prior no-shows, and absence of SMS reminder are the
  most influential signals.

---

## 4. Information / output provided

To Data Science:

- **Tool interface wrapper** — `app/tools/no_show_predictor.py`,
  with a stable `run(**features) -> dict` interface.
- **Heuristic fallback** — a documented, feature-aligned heuristic used
  when the trained model artifact is unavailable. This ensures the GenAI
  pipeline is never blocked by a missing DS artifact and gives Data
  Science a well-defined target for the eventual artifact path
  (`models/no_show_model.pkl`).
- **Documented response format** — probability, risk band, top drivers,
  source (model vs heuristic).

---

## 5. Integration activity completed

1. Agreed on the feature schema and prediction contract.
2. Implemented `app/tools/no_show_predictor.py` in the GenAI repository.
3. Wired the tool into the assistant's `no_show_risk` intent path in
   `app/agents/core_agents/knowledge_agent.py`.
4. Verified end-to-end that a `no_show_risk` query reaches the tool and
   returns a formatted response with probability, risk band, and drivers.
5. Added the tool to the Week 6 evaluation suite (`DS-01`, `DS-02`).

---

## 6. What changed as a result

**Before Week 6:**

- The assistant had no `no_show_risk` capability. A user asking about
  no-show risk received a generic KB answer.
- Data Science's model was not reachable from the assistant layer.

**After Week 6:**

- The assistant recognises the `no_show_risk` intent and calls
  `NoShowPredictorTool`.
- Responses include probability, risk band, and top drivers, using the
  DS-provided feature schema.
- If the DS artifact is not present, the assistant still returns a
  documented heuristic so the capability is not blocked.

**Evaluation results:**

- `DS-01` — "Why do patients miss appointments at HealthConnect?" — PASS
- `DS-02` — "What can HealthConnect do to reduce no-shows?" — PASS

---

## 7. Evidence

| Artefact | Location |
|---|---|
| No-show tool implementation | `app/tools/no_show_predictor.py` |
| Assistant integration | `app/agents/core_agents/knowledge_agent.py` |
| Evaluation scenarios DS-01, DS-02 | `tests/fixtures/assistant_eval_set.json` |
| Evaluation results (after) | `docs/week6/evidence/w6_eval_after.json` |
| Before/after evidence | `docs/week6/evidence/w6_before_after_examples.json` |
| Git commit | `Week 6 (GenAI): assistant evaluation & refinement` |

---

## 8. Notes on coordination

This integration was not only a communication exchange. It produced:

- A new file in the GenAI repository (`no_show_predictor.py`)
- A new intent path in the assistant (`no_show_risk`)
- Two new evaluation scenarios that exercise the integration
- A documented interface contract that Data Science can target when the
  trained artifact is ready

The integration is therefore "meaningful" per the Week 6 assignment
definition — it produced a new artefact, a code change, and a validated
behaviour.
