# PDF Change Agent

A deterministic Python tool that compares the searchable text of two PDF documents and reports exactly what changed.

This project is designed to help technical writers, documentation engineers, QA teams, and reviewers quickly identify changes between two versions of a PDF document.

## What Does This Project Do?

The PDF Change Agent compares:

- **Old PDF** - the previous version of a document
- **New PDF** - the updated version

It identifies:

- Word replacements
- Text insertions
- Text deletions
- Punctuation changes
- Symbol changes
- Changes across multiple pages
- Logical groups of nearby changes
- Page numbers associated with changes
- Surrounding context for each change

The tool produces:

1. **Atomic changes** - individual edits detected by the comparison engine
2. **Logical change groups** - related nearby edits grouped together for easier review
3. **JSON report** - structured machine-readable comparison results
4. **Markdown summary** - reviewer-friendly human-readable change report

## Example

For example, if a document changes from:

```text
I am a technical writer.
```

to:

```text
I am a documentation engineer.
```

The tool reports:

```text
Replace: 'technical' -> 'documentation'
Replace: 'writer.' -> 'engineer.'
```

For the project's real PDF comparison, the tool currently detects:

```text
Atomic changes: 13
Logical change groups: 7

Types: 7 replacements, 3 deletions, 3 insertions
```

## Key Features

### 1. Word-level comparison

Detects changes such as:

```text
technical -> documentation
```

### 2. Insertions

Detects newly added content:

```text
Insert: 'senior'
Insert: 'at Oracle.'
```

### 3. Deletions

Detects removed content:

```text
Delete: 'technical'
```

### 4. Punctuation changes

Detects changes such as:

```text
guide -> guide.
Guides. -> Guides,
```

### 5. Symbol changes

Detects changes involving symbols and different dash characters, including:

- Hyphen (`-`)
- En dash
- Em dash
- Other special symbols

### 6. Context

The report displays surrounding text so that the reviewer can understand the change without manually searching the PDF.

### 7. Page information

The report identifies the page associated with each detected change.

### 8. Logical change grouping

Nearby atomic changes are grouped into logical changes so that related edits can be reviewed together.

For example, a punctuation change followed by an inserted phrase can appear as one logical change group.

### 9. JSON report

The comparison engine generates:

```text
comparison_report.json
```

The JSON report contains:

- Comparison status
- PDF names
- Token counts
- Atomic change count
- Logical change group count
- Replacement count
- Deletion count
- Insertion count
- Detailed atomic changes
- Change categories
- Change descriptions

### 10. Markdown summary

The project also generates:

```text
comparison_summary.md
```

The Markdown report provides:

- Compared PDF names
- Overall result
- Summary counts
- Change locations
- Before context
- After context
- Individual changes
- Change categories
- Change descriptions
- Final change-count table

### 11. Automated validation

The project validates both the JSON report and Markdown summary in addition to testing the PDF comparison engine.

## How It Works

The comparison process is:

```text
Old PDF + New PDF
        |
        v
Extract searchable text
        |
        v
Tokenize text
        |
        v
Normalize tokens for comparison
        |
        v
Compare old and new tokens
        |
        v
Detect atomic changes
        |
        v
Classify changes
        |
        v
Group related changes
        |
        v
Generate JSON report
        |
        v
Generate Markdown summary
        |
        v
Run automated validation
```

## Technology Used

- Python
- PyMuPDF
- Python `difflib`
- Regular expressions
- Unicode text processing
- Python dataclasses
- JSON
- Markdown
- Automated test scripts

## Project Structure

```text
pdf-change-agent/
|
+-- tests/
|   +-- create_test_word_change.py
|   +-- create_test_insertion.py
|   +-- create_test_deletion.py
|   +-- create_test_punctuation.py
|   +-- create_test_symbol.py
|   +-- run_tests.py
|   +-- validate_json_report.py
|   +-- validate_summary.py
|
+-- .gitignore
+-- README.md
+-- main.py
+-- generate_summary.py
+-- requirements.txt
+-- comparison_report.json
+-- comparison_summary.md
```

Local files such as `.venv/`, `old.pdf`, `new.pdf`, generated test PDFs, and backup files are excluded from the GitHub repository through `.gitignore`.

## Requirements

- Python 3.10 or newer
- PyMuPDF
- Windows, macOS, or Linux

The project was developed and tested on Windows with Python 3.14.7.

## Installation

Create and activate a Python virtual environment.

### Windows PowerShell

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

## Run the PDF Comparison

Place the two PDFs in the project folder.

Use:

```powershell
python main.py old.pdf new.pdf
```

The first PDF represents the older version.

The second PDF represents the newer version.

For example:

```powershell
python main.py old.pdf new.pdf
```

The comparison engine writes:

```text
comparison_report.json
```

## Generate the Markdown Summary

After running the PDF comparison, generate the reviewer-friendly Markdown report:

```powershell
python generate_summary.py
```

This creates:

```text
comparison_summary.md
```

The workflow is therefore:

```text
old.pdf + new.pdf
        |
        v
python main.py old.pdf new.pdf
        |
        v
comparison_report.json
        |
        v
python generate_summary.py
        |
        v
comparison_summary.md
```

## Customize the Report

The comparison tool supports optional parameters.

### Change the amount of context

```powershell
python main.py old.pdf new.pdf --context 15
```

This displays more surrounding text for each change.

### Change the grouping distance

```powershell
python main.py old.pdf new.pdf --merge-gap 5
```

This changes how closely related edits are grouped.

You can combine both:

```powershell
python main.py old.pdf new.pdf --context 15 --merge-gap 5
```

## Run Automated Tests

From the project root:

```powershell
python tests\run_tests.py
```

The complete test suite currently contains **9 validation stages**:

1. Identical PDFs
2. Word replacement
3. Insertion
4. Deletion
5. Punctuation
6. Original real PDFs
7. JSON report validation
8. Markdown summary generation
9. Markdown summary validation

Current result:

```text
TEST SUMMARY
============================================================
Passed: 9/9
ALL TESTS PASSED!
```

## Current Test Coverage

| Test | Purpose | Status |
|---|---|---|
| Identical PDFs | Verify no false changes | PASS |
| Word replacement | Detect changed words | PASS |
| Insertion | Detect newly added text | PASS |
| Deletion | Detect removed text | PASS |
| Punctuation | Detect punctuation changes | PASS |
| Real PDFs | Validate against actual document changes | PASS |
| JSON validation | Validate structured comparison output | PASS |
| Markdown generation | Validate summary generation | PASS |
| Markdown validation | Validate reviewer-friendly summary | PASS |

## Current Real-PDF Test Result

The current real-PDF test compares:

```text
old.pdf
new.pdf
```

The comparison currently produces:

```text
Old PDF tokens: 376
New PDF tokens: 379

Atomic changes: 13
Logical change groups: 7

Replacements: 7
Deletions: 3
Insertions: 3
```

The 13 atomic changes are grouped into 7 logical change groups to make review easier.

## Important Limitation

The current version compares **searchable text extracted from PDFs**.

Scanned PDFs that contain only images may not contain searchable text. Such documents require OCR before meaningful text comparison can be performed.

PDF text extraction can also depend on how the source PDF was generated, including its fonts and internal text encoding.

Therefore, the current tool should be considered a deterministic **searchable-text comparison tool**, rather than a universal visual PDF comparison system.

It does not currently compare:

- Exact visual layout
- Font changes
- Images
- Graphical objects
- Page rendering differences
- Complex table-layout differences

## Why I Built This Project

Technical documentation often has multiple versions of the same document.

Manually comparing PDFs can be time-consuming, especially when reviewing:

- Product documentation releases
- Configuration guides
- User guides
- Release documentation
- Corrected documentation
- Documentation bug fixes
- Minor wording changes
- Punctuation changes

This project explores how a technical writer or documentation engineer can automate part of that review process using Python.

It also provides a foundation for eventually adding AI-assisted documentation workflows.

## Future Enhancements

Possible future versions may include:

- HTML reports
- CSV export
- Side-by-side change viewer
- PDF highlighting
- Better handling of tables
- OCR support
- Web-based interface
- AI-generated change summaries
- Change categorization
- Documentation impact analysis
- LLM-assisted review
- RAG-based documentation analysis
- Agent-based documentation workflows

These features are intentionally separate from the current deterministic comparison engine.

The deterministic comparison engine is being established first so that future AI functionality can be tested against a reliable baseline.

## Project Status

**Current status: Working deterministic prototype**

The searchable-text comparison engine is working successfully against the project's test cases and real PDFs.

The current automated test suite passes:

```text
9/9 tests
```

The project currently provides:

- Deterministic PDF text comparison
- Atomic change detection
- Logical change grouping
- Change categorization
- Page information
- Context extraction
- JSON report generation
- Markdown summary generation
- Automated validation

The next development stages will focus on improving the project incrementally while maintaining the deterministic comparison engine as a stable foundation.

## Author

Built as a practical learning and portfolio project exploring:

- Technical Documentation
- Python
- Document Automation
- Software Testing
- AI-assisted Documentation
- AI Agent Development