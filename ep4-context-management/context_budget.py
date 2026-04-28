#!/usr/bin/env python3
"""
context_budget.py — Claude Code session context budget simulator.

Estimates token usage across a Claude Code session and shows when compaction
is likely to trigger. Helps identify where the context budget goes and what
trimming CLAUDE.md or splitting sessions saves.

Usage:
    python context_budget.py --claude-md CLAUDE.md
    python context_budget.py --claude-md CLAUDE.md --turns 200 --avg-turn-tokens 1500
    python context_budget.py --claude-md CLAUDE.md --context-window 200000 --trigger-ratio 0.8

All token estimates use the chars/4 heuristic (good enough for planning purposes).
These are approximate. Actual compaction timing depends on Claude Code internals.
"""

import argparse
import os
import sys


def estimate_tokens(text: str) -> int:
    """Estimate token count using the chars/4 heuristic."""
    return max(1, len(text) // 4)


def load_file_tokens(path: str) -> int:
    """Return token estimate for a file, or 0 if the file does not exist."""
    if not os.path.isfile(path):
        return 0
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return estimate_tokens(f.read())
    except OSError:
        return 0


def format_number(n: int) -> str:
    return f"{n:,}"


def run(args: argparse.Namespace) -> None:
    claude_md_tokens = load_file_tokens(args.claude_md) if args.claude_md else 0

    context_window = args.context_window
    trigger_at = int(context_window * args.trigger_ratio)
    avg_turn = args.avg_turn_tokens
    turns = args.turns

    print()
    print("═" * 62)
    print("  Claude Code Context Budget Simulator")
    print("  (token estimates use the chars/4 heuristic)")
    print("═" * 62)
    print()

    # ── inputs ──────────────────────────────────────────────────────────────
    print("  Inputs")
    print("  ─────────────────────────────────────────────────────────")
    if args.claude_md:
        label = os.path.basename(args.claude_md) if args.claude_md else "—"
        exists = "✓" if os.path.isfile(args.claude_md) else "✗ (file not found)"
        print(f"  CLAUDE.md            {label} {exists}")
        print(f"  CLAUDE.md tokens     {format_number(claude_md_tokens)}")
    else:
        print("  CLAUDE.md            (not provided — use --claude-md to include)")
    print(f"  Context window       {format_number(context_window)} tokens")
    print(f"  Compaction trigger   {args.trigger_ratio:.0%}  ({format_number(trigger_at)} tokens)")
    print(f"  Avg tokens/turn      {format_number(avg_turn)}  (user + assistant + tools)")
    print(f"  Session turns        {turns}")
    print()

    # ── per-turn cost ────────────────────────────────────────────────────────
    turn_cost = claude_md_tokens + avg_turn  # CLAUDE.md is reloaded every turn

    print("  Per-turn cost")
    print("  ─────────────────────────────────────────────────────────")
    print(f"  CLAUDE.md (per turn) {format_number(claude_md_tokens)}  (reloaded every turn)")
    print(f"  Avg turn growth      {format_number(avg_turn)}  (conversation + tools)")
    print(f"  Total per turn       {format_number(turn_cost)}")
    print()

    # ── compaction trigger estimation ────────────────────────────────────────
    # Simplified model: context grows by avg_turn each turn, CLAUDE.md adds
    # to each turn's cost. Compaction triggers when cumulative growth hits trigger_at.
    # This is an approximation — Claude Code tracks sliding window of recent turns
    # plus the full CLAUDE.md each time.
    #
    # Formula: cumulative ≈ claude_md_tokens × turns + avg_turn × (turns × (turns+1) / 2)
    # (triangular sum for conversation growth; CLAUDE.md is flat per turn)
    # We solve for the turn count where cumulative >= trigger_at.

    compaction_turn = None
    cumulative = 0
    for t in range(1, turns + 1):
        cumulative += claude_md_tokens + avg_turn
        if cumulative >= trigger_at and compaction_turn is None:
            compaction_turn = t

    print("  Compaction estimate")
    print("  ─────────────────────────────────────────────────────────")
    if compaction_turn:
        print(f"  Est. compaction at   turn ~{compaction_turn}")
        compactions = turns // compaction_turn if compaction_turn else 0
        print(f"  Sessions of {turns} turns  ~{compactions} compaction(s)")
    else:
        total_session = claude_md_tokens * turns + avg_turn * turns
        print(f"  No compaction        {turns}-turn session uses ~{format_number(total_session)} tokens")
        print(f"                       (below {format_number(trigger_at)} trigger threshold)")
    print()

    # ── CLAUDE.md savings ─────────────────────────────────────────────────────
    savings_25 = int(claude_md_tokens * 0.25)
    savings_50 = int(claude_md_tokens * 0.50)

    print("  CLAUDE.md trim savings (across full session)")
    print("  ─────────────────────────────────────────────────────────")
    print(f"  Current cost         {format_number(claude_md_tokens)} × {turns} turns"
          f" = {format_number(claude_md_tokens * turns)} tokens")
    if savings_25 > 0:
        print(f"  Trim 25% → save      {format_number(savings_25 * turns)} tokens"
              f"  ({format_number(savings_25)} tokens freed per turn)")
    if savings_50 > 0:
        print(f"  Trim 50% → save      {format_number(savings_50 * turns)} tokens"
              f"  ({format_number(savings_50)} tokens freed per turn)")
    print()

    # ── session split savings ─────────────────────────────────────────────────
    if compaction_turn and compaction_turn < turns:
        remaining = turns - compaction_turn
        print("  Deliberate session split (vs. compaction-forced continuity)")
        print("  ─────────────────────────────────────────────────────────")
        print(f"  Split at turn        {compaction_turn}  (before first compaction)")
        print(f"  Next session starts  fresh: {format_number(claude_md_tokens)} tokens base")
        print(f"  Remaining turns      {remaining}  in new session")
        print(f"  Context saved        compaction summary overhead eliminated")
        print()

    print("  Note: These estimates assume a simplified linear growth model.")
    print("  Actual Claude Code compaction timing depends on its internal")
    print("  sliding-window accounting and may differ from these figures.")
    print()
    print("═" * 62)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Estimate Claude Code session context budget.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--claude-md",
        metavar="PATH",
        help="Path to CLAUDE.md file to measure",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=100,
        metavar="N",
        help="Estimated session length in turns (default: 100)",
    )
    parser.add_argument(
        "--avg-turn-tokens",
        type=int,
        default=1000,
        metavar="N",
        help="Avg tokens per turn: user msg + assistant response + tool outputs (default: 1000)",
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=200000,
        metavar="N",
        help="Context window size in tokens (default: 200000)",
    )
    parser.add_argument(
        "--trigger-ratio",
        type=float,
        default=0.8,
        metavar="RATIO",
        help="Compaction trigger as a fraction of context window (default: 0.8)",
    )

    args = parser.parse_args()

    if args.trigger_ratio <= 0 or args.trigger_ratio > 1.0:
        print("Error: --trigger-ratio must be between 0 and 1.0", file=sys.stderr)
        sys.exit(1)
    if args.turns <= 0:
        print("Error: --turns must be a positive integer", file=sys.stderr)
        sys.exit(1)
    if args.avg_turn_tokens <= 0:
        print("Error: --avg-turn-tokens must be a positive integer", file=sys.stderr)
        sys.exit(1)

    run(args)


if __name__ == "__main__":
    main()
