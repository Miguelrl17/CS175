import string
from pathlib import Path

WORDS = Path("word-list.txt")  # 10k guesses
ANSWERS = Path("answer-list.txt")  # 2k answers


def load_word_list(filepath) -> list[str]:
    return _load_and_validate(filepath, label="guess list")


def load_answer_list(filepath) -> list[str]:
    return _load_and_validate(filepath, label="answer list")


def _load_and_validate(filepath, label="word list") -> list[str]:
    path = Path(filepath)
    if not path.exists():
        print(f"[WordList] '{filepath}' not found — {label} will be empty.")
        return []
    with open(path, "r") as f:
        raw = f.read().strip().split("\n")
    words = [w.strip().upper() for w in raw]
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
    answers = load_answer_list(ANSWERS)
    print(f"Guess vocabulary : {len(words)} words")
    print(f"Answer list      : {len(answers)} words")
    print(f"Sample answers   : {answers[:10]}")
