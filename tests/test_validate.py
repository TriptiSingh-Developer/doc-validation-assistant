import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import validate  # noqa: E402

SOURCE = (ROOT / "data/source/acme_annual_report_2025.txt").read_text()
SAMPLE = (ROOT / "data/ai_output/ai_summary.md").read_text()

CLEAN = """## Key facts
- Reporting year: 2025
- Revenue: $2,450,000
- Operating costs: $850,000
- Cash: $615,000

## Narrative
- Revenue grew 10.9% year on year.
"""


def by_field(rows, prefix):
    return [r for r in rows if r[0].startswith(prefix)]


class ValidatorTests(unittest.TestCase):
    def test_sample_counts(self):
        _, counts = validate.validate(SOURCE, SAMPLE)
        self.assertEqual(counts, {"MATCH": 4, "MISMATCH": 4, "UNSUPPORTED": 1, "MANUAL": 1})

    def test_transposed_digits_are_caught(self):
        rows, _ = validate.validate(SOURCE, SAMPLE)
        self.assertEqual(by_field(rows, "Operating costs")[0][3], "MISMATCH")
        self.assertEqual(by_field(rows, "Cash")[0][3], "MISMATCH")

    def test_wrong_year_is_caught_with_page(self):
        rows, _ = validate.validate(SOURCE, SAMPLE)
        row = by_field(rows, "Reporting year")[0]
        self.assertEqual((row[1], row[2], row[3], row[4]), ("2025", "2024", "MISMATCH", "p.1"))

    def test_growth_is_recalculated(self):
        rows, _ = validate.validate(SOURCE, SAMPLE)
        row = by_field(rows, "Claim: Revenue grew")[0]
        self.assertEqual(row[1], "10.9% (calculated)")
        self.assertEqual(row[3], "MISMATCH")

    def test_invented_entity_is_unsupported(self):
        rows, _ = validate.validate(SOURCE, SAMPLE)
        self.assertEqual(by_field(rows, "Claim: Management")[0][3], "UNSUPPORTED")

    def test_clean_summary_passes(self):
        _, counts = validate.validate(SOURCE, CLEAN)
        self.assertEqual(counts["MISMATCH"] + counts["UNSUPPORTED"], 0)
        self.assertEqual(counts["MATCH"], 5)


if __name__ == "__main__":
    unittest.main()
