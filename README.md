# AI Document Verification Assistant

[![tests](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)

A workflow that checks an AI-generated summary against its source document and flags every error with a page reference. It combines a **Claude Project** (extraction with citations) and an independent **Python validator** (no AI) so that one check can catch the mistakes of the other.

Built with Claude (Claude.ai) and Python. All sample data is fictional.

## Why
AI summaries can contain transposed digits, wrong periods, wrong calculations and invented facts. In accuracy-critical work every output must be checked against the source. This project shows a repeatable way to do that.

## How it works
1. **Claude Project** (`claude_project/project_instructions.md`): every extracted fact must have a page number and a short quote; anything missing is answered "NOT FOUND IN SOURCE" instead of guessed.
2. **Python validator** (`validate.py`): reads the source report and the summary, compares each key fact, recalculates derived figures such as growth rates, and flags names that do not appear in the source.
3. **Human review** (`docs/manual_review_log.md`): a person checks every flagged item against the source page and records corrections.

## Quick start
Requires Python 3.9+ and no other packages.

```bash
python validate.py                      # runs the sample and writes reports/validation_report.md
python validate.py --source my_report.txt --summary my_summary.md --out my_report_check.md
python -m unittest discover -s tests -v # run the tests
```

The script exits with code 1 when it finds a mismatch or unsupported claim, so it can gate a pipeline.

## Sample result
The sample summary in `data/ai_output/ai_summary.md` contains planted errors. The validator finds all of them:

| Field | Source | AI summary | Page | Result |
|---|---|---|---|---|
| Reporting year | 2025 | 2024 | 1 | Mismatch |
| Operating costs | $850,000 | $805,000 | 2 | Mismatch (transposed digits) |
| Cash | $615,000 | $651,000 | 4 | Mismatch (transposed digits) |
| Revenue growth | 10.9% (calculated) | 15% | 2 | Mismatch |
| New plant in Ohio | not in source | stated as a plan | - | Unsupported |

Four facts match and one narrative sentence is marked for manual reading. See `reports/validation_report.md`.

## Project structure
```
validate.py                      validator and command-line tool
data/source/                     fictional source report with [Page N] markers
data/ai_output/                  AI-style summary with planted errors
claude_project/                  instructions to paste into a Claude Project
docs/manual_review_log.md        template for the human verification log
reports/validation_report.md     generated report
tests/test_validate.py           unit tests
.github/workflows/tests.yml      runs the tests on every push
```

## Use it on your own documents
1. Save the source as text with `[Page N]` markers before each page.
2. Add a regex for each field you want to check to `FIELDS` in `validate.py`.
3. Write the summary with a `## Key facts` list (`- Field: value`) and a `## Narrative` list.

## Set up the Claude Project
1. Open claude.ai/projects and click **New Project**.
2. Paste `claude_project/project_instructions.md` into the project instructions.
3. Upload the source file as project knowledge.
4. Run the three prompts listed in the instructions file and compare the answers with `validate.py`.

## Limitations
- The validator only checks the fields defined in `FIELDS`; other facts need the Claude check or a person.
- Narrative sentences without figures or names are marked "Manual check", not passed.
- The name check is a simple keyword test and can miss subtle wording errors.
- Input must be text; PDF and table parsing are not built yet.

## Roadmap
- Read PDF and table input directly
- Confidence rating and reviewer sign-off in the report
- Weekly error log that feeds back into the Claude instructions

## Author
Tripti Singh. MIT License.
