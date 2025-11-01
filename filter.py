#!/usr/bin/env python3
"""
Filter a word list for NYT Letter Boxed–style validity using a single regex.

Rules enforced:
  - Words must be length >= 3
  - Only letters from the given 12 (3 per side, in sequence)
  - No double letters (no 'aa', 'bb', ...)
  - No two adjacent letters from the same side (no '[side]{2}')

Usage:
  python filter_letterboxed.py LETTERS \
      --wordlist enable1.txt \
      --min-length 3 \
      --sort length \
      -o valid_words.txt

Where LETTERS is a 12-character string giving the square in reading order,
3 letters per side. Example: 'abcdefghiJKL' (case-insensitive). Non-letters
(e.g., hyphens/spaces) are ignored so 'abc-def-ghi-jkl' also works.

Exit codes:
  0 on success, 2 on input validation failure.

Attribution:
    Word list is the ENABLE word list, public domain:
    https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Pattern, Iterable

ALPHA_RE = re.compile(r"[A-Za-z]")

def normalize_letters(s: str) -> str:
    """Keep only A–Z; return lowercase string."""
    return ''.join(ch.lower() for ch in s if ALPHA_RE.fullmatch(ch))

def split_sides(twelve: str) -> List[str]:
    """Return four sides of length 3 from a 12-letter string."""
    if len(twelve) != 12:
        raise ValueError(f"Expected 12 letters after normalization; got {len(twelve)}.")
    return [twelve[0:3], twelve[3:6], twelve[6:9], twelve[9:12]]

def build_letterboxed_regex(sides: List[str], case_insensitive: bool = True) -> Pattern:
    """
    Create a compiled regex that enforces:
      - word length >= 3
      - only letters from the 12 given (union of the four sides)
      - no double letters (no 'aa', 'bb', etc.)
      - no two adjacent letters from the same side (no '[side_i]{2}')
    Returns a compiled regex Pattern. Use .fullmatch(word) to test a word.
    """
    # Normalize sides to lowercase, deduplicate within each side, sort for stable class
    norm_sides = [''.join(sorted(set(s.lower()))) for s in sides]
    allowed = ''.join(sorted(set(''.join(norm_sides))))
    # Character class for allowed letters
    allowed_cls = f"[{re.escape(allowed)}]"
    # Negative lookahead: no double letters anywhere
    no_double = r"(?!.*([a-z])\1)"
    # Negative lookaheads: no two adjacent from the same edge
    edge_lookaheads = ''.join([f"(?!.*[{re.escape(edge)}]{{2}})" for edge in norm_sides])
    # Assemble
    pattern = rf"^{no_double}{edge_lookaheads}{allowed_cls}{{3,}}$"
    flags = re.IGNORECASE if case_insensitive else 0
    return re.compile(pattern, flags)

def load_words(path: Path) -> Iterable[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            yield w

def main() -> int:
    ap = argparse.ArgumentParser(description="Filter a word list for Letter Boxed validity using a regex.")
    ap.add_argument("letters", help="12 letters in sequence (3 per side). Non-letters ignored.")
    ap.add_argument("--wordlist", type=Path, default=Path("enable1.txt"),
                    help="Path to input word list (one word per line). Default: enable1.txt")
    ap.add_argument("--min-length", type=int, default=3,
                    help="Minimum word length to keep. Default: 3")
    ap.add_argument("--sort", choices=["length", "alpha"], default="length",
                    help="Sort output by 'length' (desc, then alpha) or 'alpha'. Default: length")
    ap.add_argument("-o", "--output", type=Path, default="_valid_word_list.txt",
                    help="Optional output file. If omitted, prints to stdout and saves to _valid_word_list.txt.")
    ap.add_argument("--case-sensitive", action="store_true",
                    help="Make matching case-sensitive (default is case-insensitive).")
    args = ap.parse_args()

    letters_norm = normalize_letters(args.letters)
    try:
        sides = split_sides(letters_norm)
    except ValueError as e:
        print(f"Input error: {e}", file=sys.stderr)
        return 2

    # Warn if duplicates in the 12 letters (NYT usually uses distinct letters).
    if len(set(letters_norm)) != 12:
        print("Note: the 12-letter set contains duplicates. Proceeding anyway.", file=sys.stderr)

    rx = build_letterboxed_regex(sides, case_insensitive=not args.case_sensitive)

    # Allowed set for quick pre-check (speeds things up)
    allowed_set = set(''.join(sides))

    valid = []
    for raw in load_words(args.wordlist):
        w = raw.strip()
        if not w:
            continue
        # Fast pre-checks before regex (optional but helps on large lists)
        if len(w) < args.min_length:
            continue
        if not all(ch.lower() in allowed_set for ch in w if ch.isalpha()):
            continue
        # Enforce alpha-only words (no hyphens/apostrophes for this game)
        if not w.isalpha():
            continue
        if rx.fullmatch(w):
            valid.append(w)

    if args.sort == "length":
        valid.sort(key=lambda x: (-len(x), x.lower()))
    else:
        valid.sort(key=lambda x: x.lower())

    out_text = '\n'.join(valid)
    print(out_text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out_text + ("\n" if out_text else ""), encoding="utf-8")
        print(f"Wrote {len(valid)} words to {args.output}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
