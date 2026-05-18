import math
from collections import Counter
from functools import lru_cache

from feedback import GuessFeedback, GameState, compute_feedback as _raw_feedback
from pruner import prune

OPENER: str = "CRANE"

VOCAB_THRESHOLD: int = 8


@lru_cache(maxsize=None)
def _pattern(guess: str, target: str) -> tuple:
    fb = _raw_feedback(guess, target)
    return tuple(c.value for c in fb.colors)


def compute_feedback(guess, target):
    return _raw_feedback(guess, target)


def _entropy(guess: str, candidates: list[str]) -> float:
    counts: Counter = Counter(_pattern(guess, t) for t in candidates)
    total = len(candidates)
    return -sum((n / total) * math.log2(n / total) for n in counts.values())


class WordleSolver:
    def __init__(
        self,
        word_list: list[str],
        hard_mode: bool = False,
        vocab_threshold: int = VOCAB_THRESHOLD,
    ) -> None:
        self.word_list: list[str] = word_list
        self.hard_mode: bool = hard_mode
        self.vocab_threshold: int = vocab_threshold

        self._candidates: list[str] = []
        self._candidate_set: set[str] = set()
        self._state: GameState = GameState()
        self._turn: int = 0

    def reset(self) -> None:
        self._candidates = list(self.word_list)
        self._candidate_set = set(self._candidates)
        self._state = GameState()
        self._turn = 0

    def next_guess(self) -> str:
        self._turn += 1

        if self._turn == 1:
            return OPENER

        if len(self._candidates) == 1:
            return self._candidates[0]

        if not self._candidates:
            return OPENER

        guess_pool = self._choose_pool()
        return self._best_guess(guess_pool)

    def observe(self, feedback: GuessFeedback) -> None:
        self._state.update(feedback)
        self._candidates = prune(self._candidates, self._state)
        self._candidate_set = set(self._candidates)

    @property
    def num_candidates(self) -> int:
        return len(self._candidates)

    def _choose_pool(self) -> list[str]:
        if self.hard_mode:
            return self._candidates
        if len(self._candidates) <= self.vocab_threshold:
            return self.word_list
        return self._candidates

    def _best_guess(self, guess_pool: list[str]) -> str:
        best_word: str = guess_pool[0]
        best_score: tuple[float, int] = (-1.0, 0)

        for word in guess_pool:
            h = _entropy(word, self._candidates)
            score = (h, int(word in self._candidate_set))
            if score > best_score:
                best_score = score
                best_word = word

        return best_word


def find_best_opener(word_list: list[str]) -> tuple[str, float]:
    print(f"Computing opener entropy over {len(word_list)} words ...")
    best_word, best_h = word_list[0], -1.0
    for i, word in enumerate(word_list):
        h = _entropy(word, word_list)
        if h > best_h:
            best_h, best_word = h, word
        if (i + 1) % 500 == 0:
            print(
                f"{i+1}/{len(word_list)} best so far: {best_word} ({best_h:.4f} bits)"
            )
    return best_word, best_h


if __name__ == "__main__":
    import sys
    from word_list import load_word_list, WORDS

    if "--find-opener" in sys.argv:
        wl = load_word_list(WORDS)
        word, h = find_best_opener(wl)
        print(f"\nBest opener: {word}  ({h:.4f} bits)")
    else:
        print("Usage: python solver.py --find-opener")
