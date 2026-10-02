# PDF Change Agent

A deterministic Python tool that compares the searchable text of two PDF documents and reports exactly what changed.

This project is designed to help technical writers, documentation engineers, QA teams, and reviewers quickly identify changes between two versions of a PDF document.

## What Does This Project Do?

The PDF Change Agent compares:

- **Old PDF** — the previous version of a document
- **New PDF** — the updated version

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

The tool produces both:

1. **Atomic changes** — individual edits detected by the comparison engine
2. **Logical change groups** — related nearby edits grouped together for easier review

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

Detects changes involving symbols such as:

```text
- -> –
- -> —
```

### 6. Context

The report displays surrounding text so that the reviewer can understand the change without manually searching the PDF.

### 7. Page information

The report identifies the page associated with each detected change.

### 8. Automated tests

The project contains automated tests covering:

- Identical PDFs
- Word replacements
- Insertions
- Deletions
- Punctuation changes
- Real PDF comparison

Current test result:

```text
Passed: 6/6
🎉 ALL TESTS PASSED!
```

## How It Works

The comparison process is:

```text
Old PDF
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
Group related changes
   |
   v
Generate human-readable report
```

## Technology Used

- Python
- PyMuPDF
- Python `difflib`
- Regular expressions
- Unicode text processing
- Python dataclasses
- Automated test scripts

## Project Structure

```text
pdf-change-agent/
│
├── tests/
│   ├── create_test_word_change.py
│   ├── create_test_insertion.py
│   ├── create_test_deletion.py
│   ├── create_test_punctuation.py
│   ├── create_test_symbol.py
│   └── run_tests.py
│
├── .gitignore
├── README.md
├── main.py
└── requirements.txt
```

Local files such as `.venv/`, `old.pdf`, `new.pdf`, generated test PDFs, and backup files are excluded from the GitHub repository through `.gitignore`.

## Requirements

- Python 3.10 or newer
- PyMuPDF
- Windows, macOS, or Linux

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

## Customize the Report

The tool supports two optional parameters.

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

Expected result:

```text
TEST SUMMARY
============================================================
Passed: 6/6
🎉 ALL TESTS PASSED!
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

## Important Limitation

The current version compares **searchable text extracted from PDFs**.

Scanned PDFs that contain only images may not contain searchable text. Such documents require OCR before meaningful text comparison can be performed.

PDF text extraction can also depend on how the source PDF was generated, including its fonts and internal text encoding.

Therefore, the tool should be considered a deterministic **searchable-text comparison tool**, rather than a universal visual PDF comparison system.

## Why I Built This Project

Technical documentation often has multiple versions of the same document.

Manually comparing PDFs can be time-consuming, especially when reviewing:

- Product documentation releases
- Configuration guides
- User guides
- Release documentation
- Corrected documentation
- Documentation bug fixes
- Minor wording and punctuation changes

This project explores how a technical writer or documentation engineer can automate part of that review process using Python.

## Future Enhancements

Possible future versions may include:

- HTML reports
- JSON reports
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

## Project Status

**Current status: Working prototype**

The deterministic comparison engine and automated tests are working successfully against the project's current test cases and real PDFs.

The next development stages will focus on making the tool easier to use, easier to test, and suitable for a professional GitHub portfolio.

## Author

Built as a practical learning and portfolio project exploring:

- Technical Documentation
- Python
- Document Automation
- AI-assisted Documentation
- Software Testing
- AI Agent Development