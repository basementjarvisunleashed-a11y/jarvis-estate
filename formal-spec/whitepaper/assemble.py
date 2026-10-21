#!/usr/bin/env python3
"""Assemble Paper IV (J.A.R.V.I.S. roadmap white paper) from section markdown files into a styled PDF."""
import re
import markdown
from weasyprint import HTML

SECTIONS_DIR = "/home/hatch/workspace/jarvis-formal-spec/whitepaper/sections"
OUT_MD = "/home/hatch/workspace/jarvis-formal-spec/whitepaper/jarvis-roadmap-white-paper.md"
OUT_PDF = "/home/hatch/workspace/jarvis-formal-spec/whitepaper/JARVIS-Roadmap-White-Paper.pdf"

FILES = [
    "01-front-matter.md",
    "02-introduction.md",
    "03-the-six-gaps.md",
    "04-target-end-state.md",
    "05-phase-0-glossary.md",
    "06-phase-0-state-machine.md",
    "07-phase-1-formal-proof.md",
    "08-phase-2-invariants.md",
    "09-phase-3-consistency.md",
    "10-phase-4-idempotency.md",
    "11-phase-5-security.md",
    "12-phase-6-router.md",
    "13-phase-7-evidence.md",
    "14-twelve-month-programme.md",
    "15-risks-and-minimum-viable.md",
    "16-done-and-appendices.md",
]

md_texts = []
for fn in FILES:
    with open(f"{SECTIONS_DIR}/{fn}", encoding="utf-8") as f:
        md_texts.append(f.read())

# Strip the provisional TOC from section 01 (replaced by generated TOC with page numbers)
cut = md_texts[0].find("## Provisional Table of Contents")
if cut != -1:
    head = md_texts[0][:cut].rstrip()
    # also drop a trailing horizontal rule if present
    head = re.sub(r"\n---\s*$", "", head)
    md_texts[0] = head + "\n"

# Concatenated markdown (task requirement)
with open(OUT_MD, "w", encoding="utf-8") as f:
    for i, t in enumerate(md_texts):
        f.write(t)
        if i < len(md_texts) - 1:
            f.write("\n\n---\n\n")

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])

section_html = []
toc_entries = []  # (anchor, title)
for i, (fn, t) in enumerate(zip(FILES, md_texts)):
    html = md.convert(t)
    md.reset()
    anchor = f"sec{i+1:02d}"
    # extract the first h1 text for the TOC
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else fn
    toc_entries.append((anchor, title))
    section_html.append(f'<div class="section" id="{anchor}">\n{html}\n</div>')

# Build generated TOC (sections 1..16; section 1 anchors to front matter)
toc_items = "\n".join(
    f'<li><a href="#{a}">{t}</a></li>' for a, t in toc_entries
)
toc_html = f'<div class="section toc-page" id="toc"><h1>Contents</h1><ol class="toc">{toc_items}</ol></div>'

body = section_html[0] + "\n" + toc_html + "\n" + "\n".join(section_html[1:])

CSS = """
@page {
  size: A4;
  margin: 2cm 2cm 2.2cm 2cm;
  @bottom-left { content: "From Doctrine to Proof \\2014 Paper IV of the J.A.R.V.I.S. Series"; font-size: 8pt; color: #666; font-family: Georgia, 'DejaVu Serif', serif; }
  @bottom-right { content: counter(page) " / " counter(pages); font-size: 8pt; color: #666; font-family: Georgia, 'DejaVu Serif', serif; }
}
@page :first {
  @bottom-left { content: none; }
  @bottom-right { content: none; }
}
html { font-family: Georgia, 'Times New Roman', 'DejaVu Serif', serif; font-size: 10pt; line-height: 1.42; color: #1a1a1a; }
h1 { font-size: 20pt; line-height: 1.22; margin: 0 0 0.55em 0; color: #0d1b2a; }
h2 { font-size: 14pt; margin: 1.3em 0 0.45em 0; color: #16283f; border-bottom: 1px solid #ccc; padding-bottom: 0.22em; }
h3 { font-size: 11.5pt; margin: 1.1em 0 0.35em 0; color: #1e3a5c; }
h4 { font-size: 10pt; margin: 0.9em 0 0.3em 0; }
p { margin: 0.55em 0; text-align: justify; hyphens: auto; }
.section { page-break-before: always; }
.section:first-child { page-break-before: avoid; }
.toc-page ol.toc { list-style: none; padding-left: 0; }
.toc-page ol.toc li { margin: 0.35em 0; font-size: 11pt; }
.toc-page ol.toc a { text-decoration: none; color: #1a1a1a; }
.toc-page ol.toc a::after { content: leader('.') target-counter(attr(href), page); color: #555; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 9pt; line-height: 1.4; }
thead { display: table-header-group; }
th, td { border: 1px solid #999; padding: 5px 7px; text-align: left; vertical-align: top; }
th { background: #eef1f5; font-weight: bold; }
tr { page-break-inside: avoid; }
pre { background: #f4f4f2; border: 1px solid #ddd; padding: 10px 12px; font-size: 8.5pt; line-height: 1.45; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
code { font-family: 'DejaVu Sans Mono', 'Courier New', monospace; font-size: 0.88em; }
blockquote { border-left: 3px solid #8aa0b8; margin: 0.8em 0; padding: 0.2em 0 0.2em 1em; color: #333; }
blockquote p { text-align: left; }
ul, ol { margin: 0.5em 0; padding-left: 1.6em; }
li { margin: 0.25em 0; }
hr { border: none; border-top: 1px solid #bbb; margin: 1.2em 0; }
strong { color: #111; }
.title-block { text-align: center; margin: 3cm 0 2cm 0; }
"""

full_html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>From Doctrine to Proof — The J.A.R.V.I.S. Formal Validation Programme</title>
<style>{CSS}</style></head>
<body>{body}</body></html>"""

HTML(string=full_html).write_pdf(OUT_PDF)
print("PDF written:", OUT_PDF)
