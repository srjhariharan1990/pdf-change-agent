#!/usr/bin/env python3
"""Compare searchable text in two PDFs and report exact, grouped changes."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import pymupdf


TOKEN_PATTERN = re.compile(r"\S+")
DASHES = {"-", "–", "—", "−"}


@dataclass(frozen=True)
class Token:
    text: str
    page: int
    space_before: bool


@dataclass(frozen=True)
class AtomicChange:
    kind: str
    old_text: str
    new_text: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int


@dataclass
class ChangeGroup:
    old_start: int
    old_end: int
    new_start: int
    new_end: int
    changes: list[AtomicChange] = field(default_factory=list)


def tokenize_text(text: str, page_number: int = 1) -> list[Token]:
    """Keep punctuation attached to words so punctuation edits stay visible."""
    tokens: list[Token] = []
    previous_end = 0

    for match in TOKEN_PATTERN.finditer(text):
        separator = text[previous_end:match.start()]
        tokens.append(
            Token(
                text=match.group(),
                page=page_number,
                space_before=bool(separator),
            )
        )
        previous_end = match.end()

    return tokens


def extract_tokens(pdf_path: Path) -> list[Token]:
    """Extract whitespace-delimited text tokens and their PDF page numbers."""
    tokens: list[Token] = []

    with pymupdf.open(pdf_path) as document:
        if document.needs_pass:
            raise ValueError(f"The PDF is password-protected: {pdf_path}")

        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True)
            tokens.extend(tokenize_text(text, page_number))

    if not tokens:
        raise ValueError(
            f"No searchable text was found in {pdf_path}. "
            "If it is a scanned PDF, run OCR first."
        )

    return tokens


def render(tokens: list[Token]) -> str:
    """Rebuild readable text, including punctuation and original spacing."""
    parts: list[str] = []
    previous_page = None

    for token in tokens:
        if parts and (token.page != previous_page or token.space_before):
            parts.append(" ")
        parts.append(token.text)
        previous_page = token.page

    return "".join(parts)


def comparison_key(text: str) -> tuple[str, str]:
    """Align words despite edge punctuation; retain symbols as exact tokens."""
    if text in DASHES:
        return "dash", ""

    start = 0
    end = len(text)

    while start < end and unicodedata.category(text[start]).startswith("P"):
        start += 1

    while end > start and unicodedata.category(text[end - 1]).startswith("P"):
        end -= 1

    core = text[start:end]

    if core:
        return "word", core.casefold()

    return "symbol", text


def punctuation_only_difference(old_text: str, new_text: str) -> bool:
    """Return True when two tokens have the same word/symbol core."""
    old_start = 0
    old_end = len(old_text)

    while old_start < old_end and unicodedata.category(
        old_text[old_start]
    ).startswith("P"):
        old_start += 1

    while old_end > old_start and unicodedata.category(
        old_text[old_end - 1]
    ).startswith("P"):
        old_end -= 1

    new_start = 0
    new_end = len(new_text)

    while new_start < new_end and unicodedata.category(
        new_text[new_start]
    ).startswith("P"):
        new_start += 1

    while new_end > new_start and unicodedata.category(
        new_text[new_end - 1]
    ).startswith("P"):
        new_end -= 1

    old_core = old_text[old_start:old_end]
    new_core = new_text[new_start:new_end]

    return bool(old_core) and old_core.casefold() == new_core.casefold()


def punctuation_was_moved_into_insertion(
    old_tokens: list[Token],
    new_tokens: list[Token],
    old_index: int,
    new_index: int,
    opcodes: list[tuple[str, int, int, int, int]],
    opcode_index: int,
) -> bool:
    """
    Detect punctuation that moved from the end of an old token to the end
    of newly inserted text.

    Example:
        old: I am a technical writer.
        new: I am a senior technical writer at Oracle.

    The period did not disappear. It moved from writer. to Oracle.
    Therefore writer. -> writer is not a real change.
    """
    old_text = old_tokens[old_index].text
    new_text = new_tokens[new_index].text

    if not old_text or not new_text:
        return False

    punctuation = ""

    for character in reversed(old_text):
        if unicodedata.category(character).startswith("P"):
            punctuation = character + punctuation
        else:
            break

    if not punctuation:
        return False

    if old_text[:-len(punctuation)] != new_text:
        return False

    # Look at the next opcode. If new text was inserted immediately after
    # this token, check whether that inserted text ends with the same
    # punctuation.
    if opcode_index + 1 >= len(opcodes):
        return False

    next_tag, _, _, next_new_start, next_new_end = opcodes[opcode_index + 1]

    if next_tag != "insert":
        return False

    inserted_tokens = new_tokens[next_new_start:next_new_end]

    if not inserted_tokens:
        return False

    inserted_text = render(inserted_tokens)

    return inserted_text.endswith(punctuation)


def create_atomic_changes(
    old_tokens: list[Token],
    new_tokens: list[Token],
) -> list[AtomicChange]:
    """Find every edit, including punctuation and symbol-only differences."""
    old_keys = [comparison_key(token.text) for token in old_tokens]
    new_keys = [comparison_key(token.text) for token in new_tokens]

    matcher = SequenceMatcher(
        None,
        old_keys,
        new_keys,
        autojunk=False,
    )

    opcodes = matcher.get_opcodes()
    changes: list[AtomicChange] = []

    def add_change(
        kind: str,
        old_start: int,
        old_end: int,
        new_start: int,
        new_end: int,
    ) -> None:
        changes.append(
            AtomicChange(
                kind=kind,
                old_text=render(old_tokens[old_start:old_end]),
                new_text=render(new_tokens[new_start:new_end]),
                old_start=old_start,
                old_end=old_end,
                new_start=new_start,
                new_end=new_end,
            )
        )

    for opcode_index, (
        tag,
        old_start,
        old_end,
        new_start,
        new_end,
    ) in enumerate(opcodes):

        old_size = old_end - old_start
        new_size = new_end - new_start

        if tag == "equal":
            for offset in range(old_size):
                old_token = old_tokens[old_start + offset]
                new_token = new_tokens[new_start + offset]

                if old_token.text != new_token.text:
                    if punctuation_only_difference(
                        old_token.text,
                        new_token.text,
                    ):
                        if punctuation_was_moved_into_insertion(
                            old_tokens,
                            new_tokens,
                            old_start + offset,
                            new_start + offset,
                            opcodes,
                            opcode_index,
                        ):
                            continue

                    add_change(
                        "replace",
                        old_start + offset,
                        old_start + offset + 1,
                        new_start + offset,
                        new_start + offset + 1,
                    )

        elif tag == "replace":
            if old_size == new_size:
                for offset in range(old_size):
                    add_change(
                        "replace",
                        old_start + offset,
                        old_start + offset + 1,
                        new_start + offset,
                        new_start + offset + 1,
                    )
            else:
                if old_size:
                    add_change(
                        "delete",
                        old_start,
                        old_end,
                        new_start,
                        new_start,
                    )

                if new_size:
                    add_change(
                        "insert",
                        old_end,
                        old_end,
                        new_start,
                        new_end,
                    )

        elif tag == "delete":
            add_change(
                "delete",
                old_start,
                old_end,
                new_start,
                new_start,
            )

        elif tag == "insert":
            add_change(
                "insert",
                old_start,
                old_start,
                new_start,
                new_end,
            )

    return changes


def group_changes(
    changes: list[AtomicChange],
    merge_gap: int,
) -> list[ChangeGroup]:
    """Group nearby atomic edits without removing them from the report."""
    if not changes:
        return []

    ordered = sorted(
        changes,
        key=lambda item: (item.old_start, item.new_start),
    )

    groups: list[ChangeGroup] = []

    for change in ordered:
        if groups:
            current = groups[-1]

            old_gap = max(
                0,
                change.old_start - current.old_end,
            )

            new_gap = max(
                0,
                change.new_start - current.new_end,
            )

            if old_gap <= merge_gap and new_gap <= merge_gap:
                current.changes.append(change)

                current.old_start = min(
                    current.old_start,
                    change.old_start,
                )

                current.old_end = max(
                    current.old_end,
                    change.old_end,
                )

                current.new_start = min(
                    current.new_start,
                    change.new_start,
                )

                current.new_end = max(
                    current.new_end,
                    change.new_end,
                )

                continue

        groups.append(
            ChangeGroup(
                old_start=change.old_start,
                old_end=change.old_end,
                new_start=change.new_start,
                new_end=change.new_end,
                changes=[change],
            )
        )

    return groups


def get_context(
    tokens: list[Token],
    start: int,
    end: int,
    window: int,
) -> str:
    left = max(0, start - window)
    right = min(len(tokens), end + window)

    return render(tokens[left:right])


def page_label(
    tokens: list[Token],
    start: int,
    end: int,
) -> str:
    """Return changed page numbers, or the nearest page for an insertion."""
    page_tokens = tokens[start:end]

    if not page_tokens:
        anchor = start if start < len(tokens) else start - 1
        page_tokens = (
            tokens[anchor:anchor + 1]
            if anchor >= 0
            else []
        )

    pages = sorted(
        {token.page for token in page_tokens}
    )

    return (
        ", ".join(str(page) for page in pages)
        if pages
        else "—"
    )


def print_report(
    old_path: Path,
    new_path: Path,
    old_tokens: list[Token],
    new_tokens: list[Token],
    changes: list[AtomicChange],
    groups: list[ChangeGroup],
    window: int,
) -> None:
    counts = Counter(
        change.kind
        for change in changes
    )

    print("PDF TEXT COMPARISON")
    print(
        f"Old PDF: {old_path} "
        f"({len(old_tokens):,} tokens)"
    )

    print(
        f"New PDF: {new_path} "
        f"({len(new_tokens):,} tokens)"
    )

    print(
        f"Atomic changes: {len(changes)}"
    )

    print(
        f"Logical change groups: {len(groups)}"
    )

    print(
        "Types: "
        f"{counts['replace']} replacements, "
        f"{counts['delete']} deletions, "
        f"{counts['insert']} insertions"
    )

    if not changes:
        print("No text changes found.")
        return

    for number, group in enumerate(
        groups,
        start=1,
    ):
        print(
            f"\n{'=' * 72}\n"
            f"CHANGE GROUP {number}"
        )

        print(
            f"Pages: old "
            f"{page_label(old_tokens, group.old_start, group.old_end)}; "
            f"new "
            f"{page_label(new_tokens, group.new_start, group.new_end)}"
        )

        print("\nOLD CONTEXT:")
        print(
            get_context(
                old_tokens,
                group.old_start,
                group.old_end,
                window,
            )
            or "[No old text]"
        )

        print("\nNEW CONTEXT:")
        print(
            get_context(
                new_tokens,
                group.new_start,
                group.new_end,
                window,
            )
            or "[No new text]"
        )

        print("\nATOMIC CHANGES:")

        for change in group.changes:
            if change.kind == "replace":
                print(
                    f"  Replace: "
                    f"{change.old_text!r} -> "
                    f"{change.new_text!r}"
                )

            elif change.kind == "delete":
                print(
                    f"  Delete:  "
                    f"{change.old_text!r}"
                )

            else:
                print(
                    f"  Insert:  "
                    f"{change.new_text!r}"
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare searchable text in two PDFs "
            "and report changes."
        )
    )

    parser.add_argument(
        "old_pdf",
        type=Path,
        help="PDF before the changes",
    )

    parser.add_argument(
        "new_pdf",
        type=Path,
        help="PDF after the changes",
    )

    parser.add_argument(
        "--context",
        type=int,
        default=10,
        help=(
            "Surrounding tokens to show on each side "
            "(default: 10)"
        ),
    )

    parser.add_argument(
        "--merge-gap",
        type=int,
        default=8,
        help=(
            "Group edits up to this many unchanged "
            "tokens apart (default: 8)"
        ),
    )

    args = parser.parse_args()

    if args.context < 0 or args.merge_gap < 0:
        parser.error(
            "--context and --merge-gap must be zero or greater"
        )

    return args


def main() -> int:
    args = parse_args()

    try:
        old_tokens = extract_tokens(
            args.old_pdf
        )

        new_tokens = extract_tokens(
            args.new_pdf
        )

        changes = create_atomic_changes(
            old_tokens,
            new_tokens,
        )

        groups = group_changes(
            changes,
            args.merge_gap,
        )

        print_report(
            args.old_pdf,
            args.new_pdf,
            old_tokens,
            new_tokens,
            changes,
            groups,
            args.context,
        )

    except Exception as error:
        print(
            f"Error: {error}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())