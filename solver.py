from collections import Counter
from functools import lru_cache

from feedback import GuessFeedback, GameState, compute_feedback as _raw_feedback
from pruner import prune, is_consistent

OPENER: str = "SALET"

TWO_PLY_THRESHOLD: int = 20  # when low candidates, simulate one move ahead


def compute_feedback(guess, target):
    return _raw_feedback(guess, target)


@lru_cache(maxsize=None)
def _pattern(guess: str, target: str) -> tuple:
    fb = _raw_feedback(guess, target)
    return tuple(c.value for c in fb.colors)


def _expected_remaining(guess: str, candidates: list[str]) -> float:
    counts = Counter(_pattern(guess, t) for t in candidates)
    return sum(n * n for n in counts.values()) / len(candidates)


class WordleSolver:
    def __init__(
        self,
        word_list: list[str],
        answers: list[str],
        hard_mode: bool = False,
    ) -> None:
        self.word_list: list[str] = word_list  # full 10k guess vocabulary
        self.answers: list[str] = answers  # 2k possible answers
        self.hard_mode: bool = hard_mode

        self._candidates: list[str] = []
        self._candidate_set: set[str] = set()
        self._state: GameState = GameState()
        self._turn: int = 0

    def reset(self) -> None:
        self._candidates = list(self.answers)  # candidates are always from answer list
        self._candidate_set = set(self._candidates)
        self._state = GameState()
        self._turn = 0

    def next_guess(self) -> str:
        self._turn += 1

        if self._turn == 1:
            return OPENER

        if len(self._candidates) <= 2:
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
            return [w for w in self.word_list if is_consistent(w, self._state)]
        return self.word_list

    def _two_ply_score(self, guess: str, candidates: list[str]) -> float:
        partition: dict[tuple, list[str]] = {}
        for t in candidates:
            p = _pattern(guess, t)
            partition.setdefault(p, []).append(t)

        total = len(candidates)
        expected = 0.0
        WIN = tuple("G" * 5)

        for pat, group in partition.items():
            weight = len(group) / total
            if pat == WIN or len(group) == 1:
                expected += weight * len(group)
            else:
                best_er = min(_expected_remaining(g, group) for g in candidates)
                expected += weight * best_er

        return expected

    def _best_guess(self, guess_pool: list[str]) -> str:
        best_word = guess_pool[0]

        use_two_ply = len(self._candidates) <= TWO_PLY_THRESHOLD
        pool = self._candidates if use_two_ply else guess_pool

        best_score = (float("inf"), 0)
        for word in pool:
            if use_two_ply:
                sc = self._two_ply_score(word, self._candidates)
            else:
                sc = _expected_remaining(word, self._candidates)
            score = (sc, -int(word in self._candidate_set))
            if score < best_score:
                best_score = score
                best_word = word

        return best_word


def find_best_opener(word_list: list[str], answers: list[str]) -> tuple[str, float]:
    print(
        f"Computing opener over {len(word_list)} guesses × {len(answers)} answers ..."
    )
    best_word, best_er = word_list[0], float("inf")
    for i, word in enumerate(word_list):
        er = _expected_remaining(word, answers)
        if er < best_er:
            best_er, best_word = er, word
        if (i + 1) % 500 == 0:
            print(f"{i+1}/{len(word_list)} best so far: {best_word} ({best_er:.4f})")
    return best_word, best_er


if __name__ == "__main__":
    import sys
    from word_list import load_word_list, load_answer_list, WORDS, ANSWERS

    if "--find-opener" in sys.argv:
        wl = load_word_list(WORDS)
        ans = load_answer_list(ANSWERS)
        word, h = find_best_opener(wl, ans)
        print(f"\nBest opener: {word}  ({h:.4f} bits)")
    else:
        print("Usage: python solver.py --find-opener")
