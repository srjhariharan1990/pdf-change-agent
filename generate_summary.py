import json
from pathlib import Path


PROJECT_FOLDER = Path(__file__).parent
REPORT_FILE = PROJECT_FOLDER / "comparison_report.json"
SUMMARY_FILE = PROJECT_FOLDER / "comparison_summary.md"


def load_report():
    """Load the JSON comparison report."""
    if not REPORT_FILE.exists():
        raise FileNotFoundError(
            f"Report file not found: {REPORT_FILE}"
        )

    with REPORT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_file_name(file_path):
    """Return only the file name from a full path."""
    return Path(file_path).name


def get_readable_category(category):
    """Convert an internal category into reviewer-friendly text."""
    category_names = {
        "punctuation_change": "Punctuation change",
        "symbol_change": "Symbol change",
        "insertion": "Content addition",
        "deletion": "Content deletion",
        "word_change": "Word change",
        "replacement": "Content replacement",
    }

    return category_names.get(
        category,
        category.replace("_", " ").capitalize()
        if category
        else "Text change",
    )


def get_change_details(change):
    """Create a reviewer-friendly explanation."""
    change_type = change["type"]
    old_text = change.get("old", "")
    new_text = change.get("new", "")
    category = change.get("category", "")

    if category == "punctuation_change":
        if change_type == "replace":
            return (
                f"Changed punctuation from "
                f"'{old_text}' to '{new_text}'."
            )

        return "A punctuation mark was changed."

    if category == "symbol_change":
        if change_type == "replace":
            return (
                f"Changed the symbol from "
                f"'{old_text}' to '{new_text}'."
            )

        if change_type == "delete":
            return f"Removed the symbol '{old_text}'."

        if change_type == "insert":
            return f"Added the symbol '{new_text}'."

    if category == "insertion":
        return f"Added the text '{new_text}'."

    if category == "deletion":
        return f"Removed the text '{old_text}'."

    if category in {
        "word_change",
        "replacement",
    }:
        return f"Changed '{old_text}' to '{new_text}'."

    if change_type == "replace":
        return f"Changed '{old_text}' to '{new_text}'."

    if change_type == "delete":
        return f"Removed '{old_text}'."

    if change_type == "insert":
        return f"Added '{new_text}'."

    return "A text change was detected."


def format_atomic_change(change):
    """Format one atomic change for the Markdown report."""
    change_type = change["type"]
    old_text = change.get("old", "")
    new_text = change.get("new", "")
    category = change.get("category", "")

    readable_category = get_readable_category(category)
    details = get_change_details(change)

    lines = []

    if change_type == "replace":
        lines.append(
            f"- **Change:** `{old_text}` → `{new_text}`"
        )

    elif change_type == "delete":
        lines.append(
            f"- **Change:** Deleted `{old_text}`"
        )

    elif change_type == "insert":
        lines.append(
            f"- **Change:** Added `{new_text}`"
        )

    else:
        lines.append(
            f"- **Change:** `{old_text}` → `{new_text}`"
        )

    lines.append(
        f"  - **Type:** {readable_category}"
    )

    lines.append(
        f"  - **Details:** {details}"
    )

    return "\n".join(lines)


def get_group_title(group):
    """Create a meaningful title for a logical change group."""
    categories = []

    for change in group.get(
        "atomic_changes",
        [],
    ):
        category = change.get(
            "category",
            "",
        )

        readable_category = get_readable_category(
            category
        )

        if readable_category not in categories:
            categories.append(
                readable_category
            )

    if not categories:
        return "Text change"

    if len(categories) == 1:
        return categories[0]

    if len(categories) == 2:
        return (
            f"{categories[0]} and "
            f"{categories[1]}"
        )

    return (
        ", ".join(categories[:-1])
        + ", and "
        + categories[-1]
    )


def build_summary(report):
    """Build a human-readable Markdown summary."""
    summary = report["summary"]
    change_groups = report["changes"]

    old_pdf_name = get_file_name(
        report["old_pdf"]
    )

    new_pdf_name = get_file_name(
        report["new_pdf"]
    )

    lines = []

    lines.append("# PDF Change Summary")
    lines.append("")

    if report["status"] == "no_changes":
        lines.append("## Result")
        lines.append("")
        lines.append(
            "No text changes were found between "
            "the two PDFs."
        )
        lines.append("")
        return "\n".join(lines)

    lines.append("## Result")
    lines.append("")
    lines.append(
        f"**{summary['logical_change_groups']} "
        f"logical changes found.**"
    )
    lines.append("")

    lines.append("## Compared PDFs")
    lines.append("")
    lines.append(
        f"- **Old PDF:** `{old_pdf_name}`"
    )
    lines.append(
        f"- **New PDF:** `{new_pdf_name}`"
    )
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(
        f"- Old PDF tokens: **{summary['old_tokens']}**"
    )
    lines.append(
        f"- New PDF tokens: **{summary['new_tokens']}**"
    )
    lines.append(
        f"- Atomic changes: **{summary['atomic_changes']}**"
    )
    lines.append(
        f"- Logical change groups: "
        f"**{summary['logical_change_groups']}**"
    )
    lines.append(
        f"- Replacements: **{summary['replacements']}**"
    )
    lines.append(
        f"- Deletions: **{summary['deletions']}**"
    )
    lines.append(
        f"- Insertions: **{summary['insertions']}**"
    )
    lines.append("")

    lines.append("## Detailed Changes")
    lines.append("")

    for index, group in enumerate(
        change_groups,
        start=1,
    ):
        group_title = get_group_title(group)

        lines.append(
            f"### {index}. {group_title}"
        )
        lines.append("")

        old_pages = group.get(
            "old_pages",
            "",
        )

        new_pages = group.get(
            "new_pages",
            "",
        )

        lines.append("**Location**")
        lines.append("")

        if old_pages:
            lines.append(
                f"- **Old PDF:** Page {old_pages}"
            )
        else:
            lines.append(
                "- **Old PDF:** Page information unavailable"
            )

        if new_pages:
            lines.append(
                f"- **New PDF:** Page {new_pages}"
            )
        else:
            lines.append(
                "- **New PDF:** Page information unavailable"
            )

        lines.append("")

        old_context = group.get(
            "old_context",
            "",
        )

        new_context = group.get(
            "new_context",
            "",
        )

        if old_context:
            lines.append("**Before**")
            lines.append("")
            lines.append(
                f"> {old_context}"
            )
            lines.append("")

        if new_context:
            lines.append("**After**")
            lines.append("")
            lines.append(
                f"> {new_context}"
            )
            lines.append("")

        lines.append("**Changes**")
        lines.append("")

        atomic_changes = group.get(
            "atomic_changes",
            [],
        )

        for atomic_change in atomic_changes:
            lines.append(
                format_atomic_change(
                    atomic_change
                )
            )

        lines.append("")

    lines.append("## Change Counts")
    lines.append("")
    lines.append("| Change type | Count |")
    lines.append("|---|---:|")
    lines.append(
        f"| Replacements | "
        f"{summary['replacements']} |"
    )
    lines.append(
        f"| Deletions | "
        f"{summary['deletions']} |"
    )
    lines.append(
        f"| Insertions | "
        f"{summary['insertions']} |"
    )
    lines.append(
        f"| **Total atomic changes** | "
        f"**{summary['atomic_changes']}** |"
    )
    lines.append("")

    return "\n".join(lines)


def main():
    """Generate the Markdown summary."""
    try:
        report = load_report()
        summary = build_summary(report)

        with SUMMARY_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:
            file.write(summary)

        print(
            "Summary generated successfully:"
            f"\n{SUMMARY_FILE}"
        )

    except FileNotFoundError as error:
        print(f"ERROR: {error}")
        return 1

    except (
        json.JSONDecodeError,
        KeyError,
    ) as error:
        print(
            "ERROR: The JSON report is missing "
            "required information: "
            f"{error}"
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())