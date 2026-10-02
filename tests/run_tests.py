from pathlib import Path
import subprocess
import sys


PROJECT_FOLDER = Path(__file__).parent.parent


def run_test(name, old_pdf, new_pdf, expected):
    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    command = [
        sys.executable,
        str(PROJECT_FOLDER / "main.py"),
        str(PROJECT_FOLDER / old_pdf),
        str(PROJECT_FOLDER / new_pdf),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ {name} FAILED")
        print(result.stderr)
        return False

    for expected_text in expected:
        if expected_text not in result.stdout:
            print(
                f"❌ Missing expected output: "
                f"{expected_text}"
            )
            return False

    print(f"✅ {name} PASSED")
    return True


def run_json_validation():
    name = "JSON Report Validation"

    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    command = [
        sys.executable,
        str(
            PROJECT_FOLDER
            / "tests"
            / "validate_json_report.py"
        ),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_FOLDER,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ {name} FAILED")
        print(result.stderr)
        return False

    if "All checks passed." not in result.stdout:
        print(
            "❌ JSON validation did not report "
            "successful completion."
        )
        return False

    print(f"✅ {name} PASSED")
    return True


def run_summary_generation():
    name = "Markdown Summary Generation"

    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    command = [
        sys.executable,
        str(
            PROJECT_FOLDER
            / "generate_summary.py"
        ),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_FOLDER,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ {name} FAILED")
        print(result.stderr)
        return False

    if (
        "Summary generated successfully:"
        not in result.stdout
    ):
        print(
            "❌ Summary generation did not report "
            "successful completion."
        )
        return False

    print(f"✅ {name} PASSED")
    return True


def run_summary_validation():
    name = "Markdown Summary Validation"

    print(f"\n{'=' * 60}")
    print(f"TEST: {name}")
    print(f"{'=' * 60}")

    command = [
        sys.executable,
        str(
            PROJECT_FOLDER
            / "tests"
            / "validate_summary.py"
        ),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_FOLDER,
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ {name} FAILED")
        print(result.stderr)
        return False

    if "All checks passed." not in result.stdout:
        print(
            "❌ Markdown summary validation did not "
            "report successful completion."
        )
        return False

    print(f"✅ {name} PASSED")
    return True


def main():
    tests = [
        (
            "Identical PDFs",
            "tests/test_same_old.pdf",
            "tests/test_same_new.pdf",
            [
                "Atomic changes: 0",
                "Logical change groups: 0",
                "Types: 0 replacements, 0 deletions, 0 insertions",
                "No text changes found.",
            ],
        ),
        (
            "Word replacement",
            "tests/test_word_old.pdf",
            "tests/test_word_new.pdf",
            [
                "Atomic changes: 2",
                "Logical change groups: 1",
                "Types: 2 replacements, 0 deletions, 0 insertions",
                "Replace: 'technical' -> 'documentation'",
                "Replace: 'writer.' -> 'engineer.'",
            ],
        ),
        (
            "Insertion",
            "tests/test_insertion_old.pdf",
            "tests/test_insertion_new.pdf",
            [
                "Atomic changes: 2",
                "Types: 0 replacements, 0 deletions, 2 insertions",
                "Insert:  'senior'",
                "Insert:  'at Oracle.'",
            ],
        ),
        (
            "Deletion",
            "tests/test_deletion_old.pdf",
            "tests/test_deletion_new.pdf",
            [
                "Atomic changes: 1",
                "Types: 0 replacements, 1 deletions, 0 insertions",
                "Delete:  'technical'",
            ],
        ),
        (
            "Punctuation",
            "tests/test_punctuation_old.pdf",
            "tests/test_punctuation_new.pdf",
            [
                "Atomic changes: 1",
                "Types: 1 replacements, 0 deletions, 0 insertions",
                "Replace: 'guide' -> 'guide.'",
            ],
        ),
        (
            "Original real PDFs",
            "old.pdf",
            "new.pdf",
            [
                "Atomic changes: 13",
                "Logical change groups: 7",
                "Types: 7 replacements, 3 deletions, 3 insertions",
                "Replace: 'professional' -> 'professional.'",
                "Delete:  'within the organization.'",
                "Replace: 'Guides.' -> 'Guides,'",
                "Insert:  'and Online Help content.'",
                "Delete:  '•'",
                "Replace: 'Guide' -> 'Guide,'",
                "Delete:  'and'",
                "Insert:  'JIRA, Snagit,'",
                "Insert:  'user manuals'",
                "Replace: '-' -> '–'",
                "Replace: '-' -> '—'",
            ],
        ),
    ]

    passed = 0

    for test in tests:
        if run_test(*test):
            passed += 1

    if run_json_validation():
        passed += 1

    if run_summary_generation():
        passed += 1

    if run_summary_validation():
        passed += 1

    total_tests = len(tests) + 3

    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Passed: {passed}/{total_tests}")

    if passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0

    print("❌ SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())