from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

DOCS = Path("docs/week7")
FILES = [
    ("W7_Project_Summary.md", "W7_Project_Summary.pdf"),
    ("W7_Testing_Report.md",  "W7_Testing_Report.pdf"),
    ("W7_Visualizations.md",  "W7_Visualizations.pdf"),
]

CSS = """
body { font-family: -apple-system, 'Segoe UI', Roboto, sans-serif;
       max-width: 850px; margin: 2em auto; line-height: 1.55; color: #24292f; }
h1 { border-bottom: 2px solid #1f6feb; padding-bottom: 6px; }
h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 4px; margin-top: 1.6em; }
table { border-collapse: collapse; margin: 1em 0; width: 100%; }
th, td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }
th { background: #f6f8fa; }
code { background: #f6f8fa; padding: 2px 5px; border-radius: 3px; }
img { max-width: 100%; display: block; margin: 1em auto; }
blockquote { border-left: 4px solid #1f6feb; padding-left: 12px; color: #57606a; }
"""

for src, dst in FILES:
    srcp = DOCS / src
    dstp = DOCS / dst
    if not srcp.exists():
        print(f"SKIP {srcp}")
        continue
    md = srcp.read_text(encoding="utf-8")
    pdf = MarkdownPdf(toc_level=2, optimize=True)
    pdf.add_section(Section(md, root=str(DOCS)), user_css=CSS)
    pdf.meta["title"] = src.replace(".md", "")
    pdf.save(str(dstp))
    print(f"OK {dstp}")
