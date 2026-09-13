# Week 6 Project Summary — Generative AI Track

**Track:** Generative AI
**Author:** [Your Name]
**Date:** 2026-09-13
**Project:** HealthConnect Experience Lab

---

1. **What I planned to accomplish.**
   Evaluate the Week 5 assistant against a formal test suite, identify the
   highest-severity weaknesses, apply targeted refinements, and validate the
   improvement with measurable evidence. Add at least one meaningful
   cross-track integration.

2. **What I completed.**
   - Built a 30-scenario evaluation suite (`assistant_eval_set.json`)
   - Built an automated runner (`scripts/evaluate_assistant.py`)
   - Ran baseline: 22/30 (73.3%)
   - Diagnosed and fixed two orchestrator defects (safety responses,
     escalation routing)
   - Re-ran: 30/30 (100%)
   - Added a Data-Science no-show predictor tool to the assistant
   - Preserved before/after evidence under `docs/week6/evidence/`

3. **What I improved from Week 5.**
   - **Safety responses:** now include explicit emergency guidance
     (911 / 999 / 112) for emergency and medical-advice requests.
   - **Escalation routing:** `escalation_request`, `feedback` and billing
     disputes now force `requires_human=True` and produce escalation
     language.
   - **Measurability:** the assistant now has a quantitative baseline and a
     reproducible evaluation harness. Week 5 had neither.

4. **What I integrated.**
   The Data Science no-show model, exposed to the assistant as
   `app/tools/no_show_predictor.py`. The assistant now supports a
   `no_show_risk` intent that returns probability, risk band, and top drivers.

5. **Which track(s) I collaborated with.**
   Data Science (primary integration). Project Management (issue/risk
   record-keeping).

6. **What was exchanged.**
   - **Received:** DS feature specification and interface contract for the
     no-show model.
   - **Provided:** A callable tool wrapper with heuristic fallback and
     documented behaviour for missing model artefacts.

7. **What changed as a result.**
   - 8 previously-failing scenarios now pass (5 safety + 3 escalation).
   - A new assistant capability (`no_show_risk`) is now available.
   - The assistant is measurable and reproducible for Week 7.

8. **Key findings / development outcomes.**
   - Both Week 5 failure categories were defects in the orchestrator's
     response assembly, not in classification. The intent router and safety
     agent were already correct.
   - A safety-classified message can still be *unsafe* if the final response
     text is a generic refusal. This is a class of bug that pattern checks
     alone would not have caught — it required semantic expectations
     (e.g., "must contain emergency guidance") in the test set.
   - Escalation intent and escalation *action* are separate concerns; the
     orchestrator must enforce the former on the latter.

9. **Major challenges.**
   - Distinguishing evaluation-script bugs (API envelope mismatch, category
     checks) from genuine assistant failures. The first Week 6 run reported
     0/30 because of a script bug; the second run (fixed script) reported
     22/30 and isolated the real failures.
   - Providing a tool interface for the DS model without a committed
     artifact — solved by an explicit heuristic fallback that mirrors the
     documented Week 5 analytics findings.

10. **Important decisions.**
    - Keep the evaluation *strict* on safety (require explicit emergency
      language) rather than relaxing it to accept the API's
      `safety_category` signal.
    - Add escalation enforcement in the orchestrator, not in the intent
      router — the router's classification was already correct.
    - Not to hard-code an emergency number per region; use the
      911/999/112 triplet until Project Management decides on
      patient-region defaults.

11. **Remaining issues.**
    - Evaluation suite is 30 scenarios; adversarial and multilingual cases
      are not covered.
    - No-show tool falls back to heuristic because the model artifact is
      not yet in the repository.
    - Response latency varies (1.7 s–14 s per query in the eval run); no
      SLA enforced.
    - No user-facing readability or clinical appropriateness review.

12. **Contribution to the overall HealthConnect project.**
    - Delivered a measured, refined AI assistant with 100% pass on the
      Week 6 acceptance suite.
    - Provided a reusable evaluation harness that other tracks can extend.
    - Connected the assistant to the Data Science track's no-show model —
      the first working end-to-end integration between a GenAI component
      and a Data Science artefact in the project.

13. **Proposed focus for Week 7.**
    - Expand the evaluation suite to 50+ scenarios including
      prompt-injection and adversarial inputs.
    - Add semantic hallucination detection (embedding similarity to the
      retrieved KB context).
    - Enforce latency budgets.
    - Run the same suite end-to-end against the frontend.
    - Integrate the trained no-show artifact once Data Science ships it.
