#!/usr/bin/env python3
"""Document Accuracy & Validation Assistant.

Compares an AI-generated summary with a source document and writes a
validation report with page references. Standard library only.

Usage:
    python validate.py
    python validate.py --source SRC.txt --summary SUMMARY.md --out REPORT.md

Exit code: 0 = PASS, 1 = FAIL (mismatch or unsupported claim found).
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Field name -> regex (one capture group) that finds the value in the source.
FIELDS = {
    "Reporting year": r"year ended 31 December (\d{4})",
    "Revenue": r"Revenue:\s*(\$[\d,]+)",
    "Operating costs": r"Operating costs:\s*(\$[\d,]+)",
    "Net profit": r"Net profit:\s*(\$[\d,]+)",
    "Employees": r"Employees:\s*(\d+)",
    "Cash": r"Cash and cash equivalents:\s*(\$[\d,]+)",
    "Auditor": r"Auditor:\s*(.+)",
}
PRIOR_REVENUE = r"Revenue:.*?\(2024:\s*(\$[\d,]+)\)"

LABELS = {
    "MATCH": "Match",
    "MISMATCH": "Mismatch",
    "UNSUPPORTED": "Unsupported",
    "MANUAL": "Manual check",
}


def split_pages(text):
    """Return {page_number: page_text} using [Page N] markers."""
    parts = re.split(r"\[Page (\d+)\]", text)
    return {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}


def find_in_source(pages, pattern):
    """Return (value, page) of the first match, or (None, None)."""
    for page, text in pages.items():
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip(), page
    return None, None


def normalise(value):
    return re.sub(r"[$,\s]", "", value).lower()


def to_number(value):
    return float(re.sub(r"[$,]", "", value))


def summary_section(summary, name):
    """Return the bullet lines under '## name' in the summary."""
    m = re.search(rf"## {name}\n(.*?)(?=\n## |\Z)", summary, re.S)
    if not m:
        return []
    return [ln[2:].strip() for ln in m.group(1).splitlines() if ln.startswith("- ")]


def validate(source_text, summary_text):
    """Return (rows, counts). Each row: (field, source, ai, status, ref, note)."""
    pages = split_pages(source_text)
    rows = []
    counts = {k: 0 for k in LABELS}

    def add(field, src, ai, status, ref, note=""):
        counts[status] += 1
        rows.append((field, src, ai, status, ref, note))

    # 1. Key facts: exact comparison with the source.
    for line in summary_section(summary_text, "Key facts"):
        if ":" not in line:
            continue
        field, ai_value = [x.strip() for x in line.split(":", 1)]
        pattern = FIELDS.get(field)
        src_value, page = find_in_source(pages, pattern) if pattern else (None, None)
        if src_value is None:
            add(field, "not found", ai_value, "UNSUPPORTED", "-", "No evidence in source")
        elif normalise(src_value) == normalise(ai_value):
            add(field, src_value, ai_value, "MATCH", f"p.{page}")
        else:
            add(field, src_value, ai_value, "MISMATCH", f"p.{page}")

    # 2. Narrative claims: recalculated figures and names absent from the source.
    revenue, _ = find_in_source(pages, FIELDS["Revenue"])
    prior, _ = find_in_source(pages, PRIOR_REVENUE)
    growth = None
    if revenue and prior:
        growth = round((to_number(revenue) - to_number(prior)) / to_number(prior) * 100, 1)

    for line in summary_section(summary_text, "Narrative"):
        label = f"Claim: {line[:45]}"
        flagged = False
        for pct in re.findall(r"(\d+(?:\.\d+)?)%", line):
            flagged = True
            if growth is None:
                add(label, "cannot calculate", f"{pct}%", "UNSUPPORTED", "-",
                    "Source lacks the figures to check this")
            else:
                ok = abs(float(pct) - growth) <= 0.1
                add(label, f"{growth}% (calculated)", f"{pct}%",
                    "MATCH" if ok else "MISMATCH", "p.2",
                    f"({revenue} - {prior}) / {prior}")
        for word in (w.strip(".,;") for w in line.split()[1:]):
            if word.istitle() and word.lower() not in source_text.lower():
                flagged = True
                add(label, "not in source", word, "UNSUPPORTED", "-",
                    f"'{word}' never appears in the source")
        if not flagged:
            add(label, "-", "-", "MANUAL", "-",
                "No checkable figures; a person must read it against the source")
    return rows, counts


def render_report(rows, counts, source_name, summary_name):
    out = ["# Validation Report", "",
           f"Source: `{source_name}` | Checked: `{summary_name}`", "",
           "| Field | Source | AI result | Status | Source ref | Note |",
           "|---|---|---|---|---|---|"]
    for field, src, ai, status, ref, note in rows:
        out.append(f"| {field} | {src} | {ai} | {LABELS[status]} | {ref} | {note} |")
    out += ["", "## Summary"]
    out += [f"- {LABELS[k]}: {v}" for k, v in counts.items()]
    failed = counts["MISMATCH"] or counts["UNSUPPORTED"]
    out += ["", "Verdict: " + ("FAIL - corrections required before release"
                               if failed else "PASS (manual items still need a person)")]
    return "\n".join(out) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--source", default=ROOT / "data/source/acme_annual_report_2025.txt")
    p.add_argument("--summary", default=ROOT / "data/ai_output/ai_summary.md")
    p.add_argument("--out", default=ROOT / "reports/validation_report.md")
    a = p.parse_args(argv)
    source, summary, out = Path(a.source), Path(a.summary), Path(a.out)
    rows, counts = validate(source.read_text(), summary.read_text())
    report = render_report(rows, counts, source.name, summary.name)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report)
    print(report)
    return 1 if (counts["MISMATCH"] or counts["UNSUPPORTED"]) else 0


if __name__ == "__main__":
    sys.exit(main())
