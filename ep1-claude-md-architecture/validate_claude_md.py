"""validate_claude_md.py — Token budget analyser for CLAUDE.md files.

Reports estimated token count per section, total token cost, and the cumulative
cost across a multi-turn session. Uses character count / 4 as the token estimate
(no external dependencies required).

Usage:
    python validate_claude_md.py path/to/CLAUDE.md
    python validate_claude_md.py path/to/CLAUDE.md --turns 50
    python validate_claude_md.py path/to/CLAUDE.md --turns 50 --target-tokens 100

Example output:
    CLAUDE.md token budget report
    ==============================
    File: examples/api-project/CLAUDE.md

    Section breakdown:
      [structural] What this repository is     12 tokens
      [structural] Content map                 48 tokens
      [reference]  Reference                   62 tokens
      [behavioral] Behavioral                   4 tokens

    Total:  126 tokens/turn
    Target: 100 tokens/turn   ← OVER by 26 tokens

    Session cost (50 turns):
       126 tokens/turn x 50 turns = 6,300 tokens on instruction injection

    Optimised (100 tokens/turn x 50 turns):
       5,000 tokens — saves 1,300 tokens across this session.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ─── Classification ───────────────────────────────────────────────────────────

# Heading-based classification: if a heading exactly matches one of these labels,
# use that category directly. Case-insensitive.
HEADING_LABELS: dict[str, str] = {
    "structural": "structural",
    "reference": "reference",
    "behavioral": "behavioral",
    "behaviour": "behavioral",
    "behaviorial": "behavioral",
}

# Keyword fallback: if the heading does not match a known label, scan the heading
# text for these keywords and assign a category.
KEYWORD_MAP: dict[str, list[str]] = {
    "structural": [
        "what this",
        "content map",
        "file map",
        "layout",
        "stack",
        "overview",
        "structure",
        "directory",
        "files",
        "modules",
    ],
    "reference": [
        "how to",
        "workflow",
        "workflows",
        "step",
        "steps",
        "run",
        "deploy",
        "setup",
        "install",
        "usage",
        "commands",
    ],
    "behavioral": [
        "style",
        "always",
        "never",
        "prefer",
        "avoid",
        "rule",
        "rules",
        "convention",
        "conventions",
        "habit",
    ],
}


def classify_heading(heading: str) -> str:
    """Return the category for a heading. Falls back to 'other' if unknown."""
    normalised = heading.strip().lower()

    # Exact heading label match
    if normalised in HEADING_LABELS:
        return HEADING_LABELS[normalised]

    # Keyword scan
    for category, keywords in KEYWORD_MAP.items():
        if any(kw in normalised for kw in keywords):
            return category

    return "other"


# ─── Parsing ──────────────────────────────────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """Estimate token count: characters / 4, rounded up. No external deps."""
    return max(1, -(-len(text) // 4))  # ceiling division


def parse_sections(content: str) -> list[dict]:
    """
    Split content into sections by H2 headings (## Heading).
    Returns a list of dicts: {heading, category, text, tokens}.
    """
    # Split on H2 headings; keep the heading as the first item in each chunk.
    raw_sections = re.split(r"^(## .+)$", content, flags=re.MULTILINE)

    sections: list[dict] = []

    # raw_sections alternates: [preamble, heading1, body1, heading2, body2, ...]
    # First element is always the preamble (before any H2).
    preamble = raw_sections[0]
    if preamble.strip():
        preamble_tokens = estimate_tokens(preamble)
        sections.append(
            {
                "heading": "(preamble)",
                "category": "structural",  # file title / intro is always structural
                "text": preamble,
                "tokens": preamble_tokens,
            }
        )

    pairs = zip(raw_sections[1::2], raw_sections[2::2])
    for heading_line, body in pairs:
        heading_text = heading_line.lstrip("#").strip()
        full_text = heading_line + "\n" + body
        sections.append(
            {
                "heading": heading_text,
                "category": classify_heading(heading_text),
                "text": full_text,
                "tokens": estimate_tokens(full_text),
            }
        )

    return sections


# ─── Reporting ────────────────────────────────────────────────────────────────

CATEGORY_COLOURS = {
    "structural": "\033[32m",   # green
    "reference": "\033[34m",    # blue
    "behavioral": "\033[33m",   # yellow/orange
    "other": "\033[90m",        # grey
}
RESET = "\033[0m"


def colour(text: str, category: str) -> str:
    code = CATEGORY_COLOURS.get(category, "")
    return f"{code}{text}{RESET}" if code else text


def report(
    path: Path,
    sections: list[dict],
    turns: int,
    target_tokens: int,
) -> None:
    total = sum(s["tokens"] for s in sections)
    session_cost = total * turns
    optimised_cost = target_tokens * turns
    over = total - target_tokens

    print()
    print("CLAUDE.md token budget report")
    print("=" * 40)
    print(f"File: {path}")
    print()
    print("Section breakdown:")

    label_width = max(len(s["heading"]) for s in sections)
    for s in sections:
        cat_label = f"[{s['category']}]"
        heading_pad = s["heading"].ljust(label_width)
        token_str = f"{s['tokens']:>5} tokens"
        print(f"  {colour(cat_label, s['category']):<14}  {heading_pad}  {token_str}")

    print()
    if over > 0:
        status = colour(f"OVER target by {over} tokens", "behavioral")
    elif over < 0:
        status = colour(f"under target by {-over} tokens  ✓", "structural")
    else:
        status = colour("exactly at target  ✓", "structural")

    print(f"Total:  {total} tokens/turn")
    print(f"Target: {target_tokens} tokens/turn   <- {status}")
    print()
    print(f"Session cost ({turns} turns):")
    print(f"  {total} tokens/turn x {turns} turns = {session_cost:,} tokens on instruction injection")
    print()

    if over > 0:
        savings = session_cost - optimised_cost
        print(f"At target ({target_tokens} tokens/turn x {turns} turns):")
        print(
            f"  {optimised_cost:,} tokens — saves {savings:,} tokens across this session."
        )
        print()
        print("Suggestions:")
        behavioral_sections = [s for s in sections if s["category"] == "behavioral"]
        other_sections = [s for s in sections if s["category"] == "other"]
        if behavioral_sections:
            total_behavioral = sum(s["tokens"] for s in behavioral_sections)
            print(
                f"  - Behavioral sections: {total_behavioral} tokens — trim rules with "
                f"high blast-radius to hooks (see ep2-hooks/)."
            )
        if other_sections:
            print(
                f"  - Unclassified sections ({len(other_sections)}): consider labelling "
                f"headings as ## Structural / ## Reference / ## Behavioral."
            )
    print()


# ─── Entry point ──────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyse the token budget of a CLAUDE.md file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", help="Path to the CLAUDE.md file to analyse.")
    parser.add_argument(
        "--turns",
        type=int,
        default=50,
        help="Number of turns to project cost over (default: 50).",
    )
    parser.add_argument(
        "--target-tokens",
        type=int,
        default=100,
        dest="target_tokens",
        help="Target tokens per turn (default: 100).",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    sections = parse_sections(content)
    report(path, sections, turns=args.turns, target_tokens=args.target_tokens)


if __name__ == "__main__":
    main()
