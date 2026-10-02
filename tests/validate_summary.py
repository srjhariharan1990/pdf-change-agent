from pathlib import Path


SUMMARY_PATH = Path("comparison_summary.md")


def check(condition, message):
    if not condition:
        raise AssertionError(message)

    print(f"PASS: {message}")


def main():
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"{SUMMARY_PATH} was not found. "
            "Run 'python generate_summary.py' first."
        )

    content = SUMMARY_PATH.read_text(
        encoding="utf-8"
    )

    # Check report title and result.
    check(
        "# PDF Change Summary" in content,
        "Summary title is present",
    )

    check(
        "**7 logical changes found.**" in content,
        "Logical change count is present",
    )

    # Check compared PDF names.
    check(
        "`old.pdf`" in content,
        "Old PDF name is present",
    )

    check(
        "`new.pdf`" in content,
        "New PDF name is present",
    )

    # Check summary counts.
    check(
        "Old PDF tokens: **376**" in content,
        "Old PDF token count is correct",
    )

    check(
        "New PDF tokens: **379**" in content,
        "New PDF token count is correct",
    )

    check(
        "Atomic changes: **13**" in content,
        "Atomic change count is correct",
    )

    check(
        "Logical change groups: **7**" in content,
        "Logical change group count is correct",
    )

    check(
        "Replacements: **7**" in content,
        "Replacement count is correct",
    )

    check(
        "Deletions: **3**" in content,
        "Deletion count is correct",
    )

    check(
        "Insertions: **3**" in content,
        "Insertion count is correct",
    )

    # Check detailed change sections.
    check(
        "## Detailed Changes" in content,
        "Detailed changes section is present",
    )

    check(
        content.count("### ") == 7,
        "Summary contains 7 change groups",
    )

    check(
        content.count("**Location**") == 7,
        "Location information exists for all 7 groups",
    )

    check(
        content.count("**Before**") == 7,
        "Before context exists for all 7 groups",
    )

    check(
        content.count("**After**") == 7,
        "After context exists for all 7 groups",
    )

    # Check important detected changes.
    check(
        "`professional` → `professional.`" in content,
        "Professional punctuation change is present",
    )

    check(
        "`within the organization.`" in content,
        "Deleted organization text is present",
    )

    check(
        "`Guides.` → `Guides,`" in content,
        "Guides punctuation change is present",
    )

    check(
        "`and Online Help content.`" in content,
        "Online Help insertion is present",
    )

    check(
        "`JIRA, Snagit,`" in content,
        "JIRA and Snagit insertion is present",
    )

    check(
        "`user manuals`" in content,
        "User manuals insertion is present",
    )

    # Check final count table.
    check(
        "## Change Counts" in content,
        "Change counts section is present",
    )

    check(
        "| **Total atomic changes** | **13** |" in content,
        "Final atomic change count is correct",
    )

    print()
    print("Summary validation completed successfully.")
    print("All checks passed.")


if __name__ == "__main__":
    main()