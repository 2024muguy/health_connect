# Week 6 GenAI — Evaluation Visualizations

All charts are generated from the Week 6 evidence files by
`scripts/generate_w6_visualizations.py`.

---

## 1. Overall Pass Rate: 22/30 → 30/30

![Overall pass rate](figures/01_overall_pass_rate.png)

---

## 2. Pass Rate by Category

![Pass rate by category](figures/02_by_category.png)

Escalation climbed from **25%** to **100%**. Safety climbed from **0%**
to **100%**. All other categories retained their 100% baseline.

---

## 3. Scenarios Fixed in Week 6

![Scenarios fixed](figures/03_fixed_by_category.png)

Eight scenarios moved from FAIL to PASS: 5 safety, 3 escalation.

---

## 4. Response Latency (Week 6 run)

![Latency histogram](figures/04_latency.png)

Median response time on the 30-scenario run. This informs the Week 7
latency budget (p50 < 4s target).

---

## 5. Safety & Escalation — Every Failure Fixed

![Safety and escalation](figures/05_safety_escalation.png)

Side-by-side: every safety and escalation scenario was failing in Week 5
and is passing in Week 6.

---

## 6. Assistant Coverage Radar

![Radar](figures/06_radar.png)

Six-dimension coverage: KB factual, KB boundary, escalation, safety,
multi-turn, consistency.
