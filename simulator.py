from dataclasses import dataclass

from feedback import GuessFeedback, compute_feedback
from solver import WordleSolver

MAX_GUESSES: int = 6


@dataclass
class GameResult:
    target: str
    history: list[GuessFeedback]
    solved: bool

    @property
    def num_guesses(self) -> int:
        return len(self.history)

    def __str__(self) -> str:
        status = "Solved" if self.solved else "Failed"
        lines = [f"{status} Target: {self.target}  ({self.num_guesses} guesses)"]
        for fb in self.history:
            lines.append(f"{fb}")
        return "\n".join(lines)


class WordleGame:
    def __init__(self, answer_list: list[str], target: str) -> None:
        self.answer_list: list[str] = answer_list
        self._answer_set: set[str] = set(answer_list)
        self.target: str = target.upper()

    def play(self, solver: WordleSolver, verbose: bool = False) -> GameResult:
        solver.reset()
        history: list[GuessFeedback] = []

        for turn in range(1, MAX_GUESSES + 1):
            guess = solver.next_guess()
            fb = compute_feedback(guess, self.target)
            history.append(fb)

            if verbose:
                print(f"Turn {turn}: {fb}  (candidates left: {solver.num_candidates})")

            solver.observe(fb)

            if fb.is_win():
                break

        solved = history[-1].is_win()

        if verbose:
            status = "Solved" if solved else "FAILED"
            print(f"-> {status} '{self.target}' in {len(history)} guess(es).\n")

        return GameResult(target=self.target, history=history, solved=solved)
