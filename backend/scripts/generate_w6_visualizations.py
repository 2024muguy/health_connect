"""HealthConnect Week 6 (GenAI) - Visualizations.
Output: docs/week6/figures/*.png
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "figure.dpi": 140, "savefig.dpi": 140, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
})

FIG = Path("docs/week6/figures")
FIG.mkdir(parents=True, exist_ok=True)

before = json.load(open("reports/w6_eval_before.json"))
after  = json.load(open("reports/w6_eval_after.json"))
diff   = json.load(open("reports/w6_eval_diff.json"))

PRIMARY = "#1f6feb"
PASS_C  = "#2da44e"
FAIL_C  = "#cf222e"
NEUTRAL = "#57606a"


def chart_01():
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    labels = ["Week 5\n(baseline)", "Week 6\n(refined)"]
    passed = [before["passed"], after["passed"]]
    failed = [before["total"] - before["passed"],
              after["total"] - after["passed"]]
    x = np.arange(len(labels)); w = 0.55
    ax.bar(x, passed, w, label="Passed", color=PASS_C)
    ax.bar(x, failed, w, bottom=passed, label="Failed", color=FAIL_C)
    for i, (pa, fa) in enumerate(zip(passed, failed)):
        total = pa + fa
        ax.text(i, pa/2, f"{pa}", ha="center", va="center",
                color="white", fontweight="bold", fontsize=13)
        if fa:
            ax.text(i, pa + fa/2, f"{fa}", ha="center", va="center",
                    color="white", fontweight="bold", fontsize=13)
        ax.text(i, total + 0.7, f"{pa}/{total}  ({pa/total*100:.1f}%)",
                ha="center", fontsize=10, color=NEUTRAL)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Scenarios")
    ax.set_title("Assistant Pass Rate - Week 5 vs Week 6")
    ax.set_ylim(0, 34)
    ax.legend(loc="lower right", frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "01_overall_pass_rate.png", bbox_inches="tight")
    plt.close()
    print("OK 01_overall_pass_rate.png")


def chart_02():
    cats = sorted(before["by_category"].keys())
    bc = [before["by_category"][c]["pass"] / before["by_category"][c]["total"] * 100 for c in cats]
    ac = [after["by_category"][c]["pass"]  / after["by_category"][c]["total"]  * 100 for c in cats]
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    x = np.arange(len(cats)); w = 0.38
    b1 = ax.bar(x - w/2, bc, w, label="Week 5", color=NEUTRAL, alpha=0.7)
    b2 = ax.bar(x + w/2, ac, w, label="Week 6", color=PRIMARY)
    for bars in (b1, b2):
        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2, h + 2, f"{h:.0f}%",
                    ha="center", fontsize=9, color=NEUTRAL)
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=15, ha="right")
    ax.set_ylabel("Pass rate (%)")
    ax.set_title("Pass Rate by Category - Before vs After")
    ax.set_ylim(0, 115)
    ax.axhline(100, color=PASS_C, linestyle="--", linewidth=0.8, alpha=0.5)
    ax.legend(frameon=False, loc="lower right")
    plt.tight_layout()
    plt.savefig(FIG / "02_by_category.png", bbox_inches="tight")
    plt.close()
    print("OK 02_by_category.png")


def chart_03():
    fixed_by_cat = {}
    for sid in diff["fixed"]:
        for r in before["results"]:
            if r["id"] == sid:
                cat_name = r["category"]
                fixed_by_cat[cat_name] = fixed_by_cat.get(cat_name, 0) + 1

    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    if fixed_by_cat:
        names = list(fixed_by_cat.keys())
        vals = [fixed_by_cat[k] for k in names]
        bars = ax.barh(names, vals, color=PASS_C)
        for b, v in zip(bars, vals):
            ax.text(v + 0.1, b.get_y() + b.get_height()/2, str(v),
                    va="center", fontsize=11, fontweight="bold", color=NEUTRAL)
        ax.set_xlabel("Scenarios fixed")
        ax.set_title(f"Scenarios Fixed in Week 6 - total {diff['delta']}")
        ax.set_xlim(0, max(vals) + 1)
    plt.tight_layout()
    plt.savefig(FIG / "03_fixed_by_category.png", bbox_inches="tight")
    plt.close()
    print("OK 03_fixed_by_category.png")


def chart_04():
    lat = [r["elapsed_s"] for r in after["results"] if "elapsed_s" in r]
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.hist(lat, bins=12, color=PRIMARY, edgecolor="white")
    ax.axvline(np.median(lat), color=FAIL_C, linestyle="--", linewidth=1.4,
               label=f"median = {np.median(lat):.1f}s")
    ax.axvline(np.mean(lat), color="#bf8700", linestyle=":", linewidth=1.4,
               label=f"mean = {np.mean(lat):.1f}s")
    ax.set_xlabel("Response time (s)")
    ax.set_ylabel("Number of scenarios")
    ax.set_title("Response Latency Distribution - Week 6 (30 scenarios)")
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "04_latency.png", bbox_inches="tight")
    plt.close()
    print("OK 04_latency.png")


def chart_05():
    safety_ids = [r["id"] for r in after["results"] if r["category"] == "safety"]
    esc_ids    = [r["id"] for r in after["results"] if r["category"] == "escalation"]
    all_ids    = safety_ids + esc_ids
    before_pass = {r["id"]: r["pass"] for r in before["results"]}
    after_pass  = {r["id"]: r["pass"] for r in after["results"]}

    fig, ax = plt.subplots(figsize=(8.5, 3.6))
    x = np.arange(len(all_ids)); w = 0.38
    b_vals = [1 if before_pass[i] else 0 for i in all_ids]
    a_vals = [1 if after_pass[i]  else 0 for i in all_ids]
    ax.bar(x - w/2, b_vals, w, color=NEUTRAL, alpha=0.7, label="Week 5")
    ax.bar(x + w/2, a_vals, w, color=PASS_C, label="Week 6")
    for i, (bv, av) in enumerate(zip(b_vals, a_vals)):
        ax.text(i - w/2, bv + 0.03, "PASS" if bv else "FAIL",
                ha="center", fontsize=8, color=NEUTRAL, rotation=90)
        ax.text(i + w/2, av + 0.03, "PASS" if av else "FAIL",
                ha="center", fontsize=8, color=PASS_C, rotation=90)
    ax.set_xticks(x); ax.set_xticklabels(all_ids)
    ax.set_yticks([]); ax.set_ylim(0, 1.3)
    ax.set_title("Safety & Escalation Scenarios - Every Failure Fixed")
    ax.legend(frameon=False, loc="upper right", ncol=2)
    plt.tight_layout()
    plt.savefig(FIG / "05_safety_escalation.png", bbox_inches="tight")
    plt.close()
    print("OK 05_safety_escalation.png")


def chart_06():
    cats_radar = sorted(before["by_category"].keys())
    bc_r = [before["by_category"][c]["pass"] / before["by_category"][c]["total"] * 100 for c in cats_radar]
    ac_r = [after["by_category"][c]["pass"]  / after["by_category"][c]["total"]  * 100 for c in cats_radar]
    angles = np.linspace(0, 2*np.pi, len(cats_radar), endpoint=False).tolist()
    bc_r += bc_r[:1]; ac_r += ac_r[:1]; angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 5.5), subplot_kw=dict(polar=True))
    ax.plot(angles, bc_r, color=NEUTRAL, linewidth=1.8, label="Week 5")
    ax.fill(angles, bc_r, color=NEUTRAL, alpha=0.15)
    ax.plot(angles, ac_r, color=PASS_C, linewidth=2.2, label="Week 6")
    ax.fill(angles, ac_r, color=PASS_C, alpha=0.20)
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats_radar)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], color=NEUTRAL, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_title("Assistant Coverage Radar - Week 5 vs Week 6", pad=18)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), frameon=False)
    plt.tight_layout()
    plt.savefig(FIG / "06_radar.png", bbox_inches="tight")
    plt.close()
    print("OK 06_radar.png")


if __name__ == "__main__":
    chart_01()
    chart_02()
    chart_03()
    chart_04()
    chart_05()
    chart_06()
    print(f"\nAll figures saved to {FIG}")
