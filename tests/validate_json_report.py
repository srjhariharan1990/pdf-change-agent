import json
from pathlib import Path


REPORT_PATH = Path("comparison_report.json")


def check(condition, message):
    if not condition:
        raise AssertionError(message)

    print(f"PASS: {message}")


def main():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"{REPORT_PATH} was not found. "
            "Run 'python main.py old.pdf new.pdf' first."
        )

    with REPORT_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        report = json.load(file)

    summary = report["summary"]
    changes = report["changes"]

    # Check report metadata.
    check(
        report["report_type"] == "pdf_text_comparison",
        "Report type is correct",
    )

    check(
        report["version"] == "1.0",
        "Report version is correct",
    )

    # Check overall counts.
    check(
        summary["atomic_changes"] == 13,
        "Atomic changes = 13",
    )

    check(
        summary["logical_change_groups"] == 7,
        "Logical change groups = 7",
    )

    check(
        summary["replacements"] == 7,
        "Replacements = 7",
    )

    check(
        summary["deletions"] == 3,
        "Deletions = 3",
    )

    check(
        summary["insertions"] == 3,
        "Insertions = 3",
    )

    # Check number of groups.
    check(
        len(changes) == 7,
        "JSON contains 7 change groups",
    )

    # Collect every atomic change.
    atomic_changes = []

    for group in changes:
        atomic_changes.extend(
            group["atomic_changes"]
        )

    check(
        len(atomic_changes) == 13,
        "JSON contains 13 atomic changes",
    )

    # Check the bullet symbol classification.
    bullet_changes = [
        change
        for change in atomic_changes
        if change["old"] == "•"
    ]

    check(
        len(bullet_changes) == 1,
        "Bullet symbol change exists",
    )

    check(
        bullet_changes[0]["category"] == "symbol_change",
        "Bullet symbol is classified as symbol_change",
    )

    # Check punctuation classification.
    guide_changes = [
        change
        for change in atomic_changes
        if change["old"] == "Guide"
        and change["new"] == "Guide,"
    ]

    check(
        len(guide_changes) == 1,
        "Guide punctuation change exists",
    )

    check(
        guide_changes[0]["category"] == "punctuation_change",
        "Guide change is classified as punctuation_change",
    )

    # Check insertion classification.
    jira_changes = [
        change
        for change in atomic_changes
        if change["new"] == "JIRA, Snagit,"
    ]

    check(
        len(jira_changes) == 1,
        "JIRA and Snagit insertion exists",
    )

    check(
        jira_changes[0]["category"] == "insertion",
        "JIRA and Snagit change is classified as insertion",
    )

    print()
    print("JSON validation completed successfully.")
    print("All checks passed.")


if __name__ == "__main__":
    main()