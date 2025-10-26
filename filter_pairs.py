#!/usr/bin/env python3
"""
Find two-word solutions for NYT Letter Boxed from a filtered word list.

Assumes your word list already enforces per-word rules (length >= 3, only the 12 letters,
no doubles, no same-side adjacencies). This script:
  - Takes the same 12-letter input (3 per side, in sequence; non-letters ignored).
  - Reads the filtered list (default: _valid_words.txt).
  - Finds ordered pairs (A, B) such that:
        last(A) == first(B)   [chain rule]
        set(A + B) covers all 12 letters at least once
  - Optionally includes reverse direction pairs as well (default is both directions).

Usage:
  python find_pairs_letterboxed.py LETTERS \
      --wordlist valid_words.txt \
      --sort combined_len \
      -o pairs.txt

Output format (default): "WORD1 WORD2" per line (ordered pair).
"""

import argparse
from collections import defaultdict
from pathlib import Path
from typing import List, Set, Tuple

def normalize_letters(s: str) -> str:
    return ''.join(ch.lower() for ch in s if ch.isalpha())

def split_sides(twelve: str) -> List[str]:
    if len(twelve) != 12:
        raise ValueError(f"Expected 12 letters after normalization; got {len(twelve)}.")
    return [twelve[0:3], twelve[3:6], twelve[6:9], twelve[9:12]]

def load_words(path: Path) -> List[str]:
    words = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip()
            if not w:
                continue
            if not w.isalpha():
                continue
            words.append(w.lower())
    return words

def find_pairs(words: List[str], letters_set: Set[str]) -> List[Tuple[str, str]]:
    # Index by starting letter
    by_start = defaultdict(list)
    for w in words:
        by_start[w[0]].append(w)

    pairs = []
    for a in words:
        a_end = a[-1]
        # Candidate continuations B must start with a_end
        for b in by_start.get(a_end, ()):
            # quick coverage check
            if letters_set.issubset(set(a) | set(b)):
                # Accept ordered pair (a, b)
                pairs.append((a, b))
    return pairs

def main() -> int:
    ap = argparse.ArgumentParser(description="Find two-word Letter Boxed solutions from a filtered list.")
    ap.add_argument("letters", help="12 letters in sequence (3 per side). Non-letters ignored.")
    ap.add_argument("--wordlist", type=Path, default=Path("_valid_word_list.txt"),
                    help="Path to filtered word list. Default: _valid_word_list.txt")
    ap.add_argument("--sort", choices=["combined_len", "alpha"], default="combined_len",
                    help="Sort pairs by combined length (desc) or alphabetically. Default: combined_len")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="Optional output file; otherwise prints to stdout.")
    args = ap.parse_args()

    letters_norm = normalize_letters(args.letters)
    try:
        sides = split_sides(letters_norm)
    except ValueError as e:
        print(f"Input error: {e}")
        return 2

    letters_set = set(''.join(sides))
    words = load_words(args.wordlist)

    # Fast sanity: keep only words composed of allowed letters (in case list wasn't filtered)
    words = [w for w in words if set(w).issubset(letters_set) and len(w) >= 3]

    pairs = find_pairs(words, letters_set)

    if args.sort == "combined_len":
        pairs.sort(key=lambda ab: (-(len(ab[0]) + len(ab[1])), ab[0], ab[1]))
    else:
        pairs.sort(key=lambda ab: (ab[0], ab[1]))

    out_lines = [f"{a} {b}" for a, b in pairs]
    out_text = '\n'.join(out_lines)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out_text + ("\n" if out_text else ""), encoding="utf-8")
        print(f"Wrote {len(pairs)} pairs to {args.output}")
    else:
        print(out_text)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
