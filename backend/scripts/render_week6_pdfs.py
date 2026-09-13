"""Render Week 6 markdown files to PDF using markdown-pdf (Playwright/Chromium)."""
from pathlib import Path
import sys

try:
    from markdown_pdf import MarkdownPdf, Section
except ImportError:
    print("!! markdown-pdf not installed. Run: pip install markdown-pdf")
    sys.exit(1)

DOCS = Path("docs/week6")
OUTPUTS = [
    ("W6_GenAI_Evaluation_Package.md", "W6_GenAI_Evaluation_Package.pdf"),
    ("W6_Project_Summary.md",          "W6_Project_Summary.pdf"),
    ("W6_CrossTrack_Integration.md",   "W6_CrossTrack_Integration.pdf"),
    ("W6_Week7_Testing_Plan.md",       "W6_Week7_Testing_Plan.pdf"),
    ("W6_Visualizations.md",           "W6_Visualizations.pdf"),
]

CSS = """
body { font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;
       max-width: 850px; margin: 2em auto; line-height: 1.55; color: #24292f; }
h1 { border-bottom: 2px solid #1f6feb; padding-bottom: 6px; }
h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 4px; margin-top: 1.6em; }
h3 { margin-top: 1.3em; }
table { border-collapse: collapse; margin: 1em 0; width: 100%; }
th, td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }
th { background: #f6f8fa; }
code { background: #f6f8fa; padding: 2px 5px; border-radius: 3px;
       font-family: 'Consolas', monospace; font-size: 0.92em; }
pre code { display: block; padding: 10px; overflow-x: auto; }
blockquote { border-left: 4px solid #1f6feb; padding-left: 12px;
             color: #57606a; margin-left: 0; }
img { max-width: 100%; }
"""

for src_name, dst_name in OUTPUTS:
    src = DOCS / src_name
    dst = DOCS / dst_name
    if not src.exists():
        print(f"SKIP (not found): {src}")
        continue

    md_text = src.read_text(encoding="utf-8")

    pdf = MarkdownPdf(toc_level=2, optimize=True)
    pdf.add_section(Section(md_text, root=str(DOCS)), user_css=CSS)
    pdf.meta["title"] = src_name.replace(".md", "")
    pdf.meta["author"] = "HealthConnect GenAI Track - Week 6"
    pdf.save(str(dst))
    print(f"OK {dst}")

print("\nAll PDFs generated in docs/week6/")
