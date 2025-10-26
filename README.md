
# wordbox

CLI tools for exploring and solving the **New York Times Letter Boxed** puzzle.

An exercise in vibe coding and complex regex.

This repository contains two complementary Python scripts:

* `filter.py` — filters a dictionary to valid candidate words
* `filter_pairs.py` — finds two-word solutions from the filtered list

They are kept separate so that each can be used independently:
the first to **narrow possibilities** or **spark ideas**, the second to **solve**.

---

## 1. `filter.py` — Word List Filter

Filters a word list to include only words valid under Letter Boxed rules.

**Rules enforced**

* Words must be at least 3 letters long
* Only the 12 given letters are allowed (3 per side)
* No double letters (e.g. “cool”)
* No two adjacent letters from the same side

Use this to generate a smaller, valid word list — or to find inspiration when stuck.

**Example**

```bash
python filter.py abc-def-gui-rst \
    --wordlist enable1.txt \
    -o valid_words.txt
```

**Example output (excerpt)**

```
afield
beadle
beagle
flake
dice
```

Output is saved to `_valid_word_list.txt` unless `-o` is specified.

---

## 2. `filter_pairs.py` — Pair Finder (Solver)

Finds all valid two-word solutions from the filtered word list.

Each pair `(A, B)` satisfies:

* The last letter of `A` equals the first letter of `B`
* Together, `A` and `B` use all 12 letters at least once

This script is the solver, useful for confirming or discovering complete answers.

**Example**

```bash
python filter_pairs.py abc-def-gui-rst \
    --wordlist valid_words.txt \
    --sort combined_len \
    -o pairs.txt
```

**Example output**

```
gratifies subduces
driftages scrub
```

---

## Typical Workflow

1. **Filter a word list:**

   ```bash
   python filter.py "abc-def-ghi-jkl" -o valid_words.txt
   ```
2. **Find two-word solutions:**

   ```bash
   python filter_pairs.py "abc-def-ghi-jkl" --wordlist valid_words.txt
   ```

---

## Requirements

* Python 3.7 or later
* A plain-text word list, such as the [ENABLE word list](https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt)

Both scripts use only the Python standard library.

---

## Notes

* Input letters can include separators (e.g. `abc-def-ghi-jkl` or `ABC DEF GHI JKL`).
* The scripts print warnings if the 12 letters contain duplicates.
* Results can be sorted by length or alphabetically.
* Vibe coded using a combination of Google Gemini and GPT-5.

---

## License

Uses the ENABLE word list which is in the public domain.
See [https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt](https://raw.githubusercontent.com/dolph/dictionary/master/enable1.txt) for licensing and attribution.

