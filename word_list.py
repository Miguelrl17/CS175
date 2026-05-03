import os
import string
from pathlib import Path

WORDS = Path(r"valid-wordle-words.txt")

def load_word_list(filepath) :
    words = []
    if filepath and Path(filepath).exists():
        with open(filepath, "r") as f:
            raw = f.read().strip().split("\n")
        words = [w.strip().upper() for w in raw]
    else:
        if filepath:
            print(f"[WordList] '{filepath}' not found — using embedded list.")
    return _validate(words)


def _validate(words: list[str]) -> list[str]:
    seen: set[str] = set()
    valid: list[str] = []
    for w in words:
        w = w.strip().upper()
        if (
            len(w) == 5
            and all(c in string.ascii_uppercase for c in w)
            and w not in seen
        ):
            seen.add(w)
            valid.append(w)
    return valid

if __name__ == "__main__":
    words = load_word_list(WORDS)
    print(f"Sample: {words[:10]}")