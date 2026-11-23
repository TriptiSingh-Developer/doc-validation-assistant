# Validation Report

Source: `acme_annual_report_2025.txt` | Checked: `ai_summary.md`

| Field | Source | AI result | Status | Source ref | Note |
|---|---|---|---|---|---|
| Reporting year | 2025 | 2024 | Mismatch | p.1 |  |
| Revenue | $2,450,000 | $2,450,000 | Match | p.2 |  |
| Operating costs | $850,000 | $805,000 | Mismatch | p.2 |  |
| Net profit | $412,000 | $412,000 | Match | p.3 |  |
| Employees | 148 | 148 | Match | p.3 |  |
| Cash | $615,000 | $651,000 | Mismatch | p.4 |  |
| Auditor | Harlow & Finch LLP | Harlow & Finch LLP | Match | p.4 |  |
| Claim: Revenue grew 15% year on year, a record resul | 10.9% (calculated) | 15% | Mismatch | p.2 | ($2,450,000 - $2,210,000) / $2,210,000 |
| Claim: Management plans to open a new plant in Ohio. | not in source | Ohio | Unsupported | - | 'Ohio' never appears in the source |
| Claim: Operating costs rose modestly while profit in | - | - | Manual check | - | No checkable figures; a person must read it against the source |

## Summary
- Match: 4
- Mismatch: 4
- Unsupported: 1
- Manual check: 1

Verdict: FAIL - corrections required before release
