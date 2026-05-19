import time
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


def run_benchmark(
    answer_list: list[str],
    solver: WordleSolver,
    verbose: bool = False,
    show_progress: bool = True,
    sample: list[str] | None = None,
) -> dict:
    targets = sample if sample is not None else answer_list
    n = len(targets)
    results: list[GameResult] = []
    failed: list[str] = []
    t0 = time.time()

    for i, target in enumerate(targets):
        if show_progress and (i % 50 == 0 or i == n - 1):
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (n - i - 1) / rate if rate > 0 else 0
            print(
                f"\r[{i+1}/{n}]  {(i+1)/n*100:5.1f}%  "
                f"elapsed {elapsed:6.1f}s  ETA {eta:5.1f}s   ",
                end="",
                flush=True,
            )

        game = WordleGame(answer_list, target)
        result = game.play(solver, verbose=verbose)
        results.append(result)

        if not result.solved:
            failed.append(target)

    if show_progress:
        print()

    solved_results = [r for r in results if r.solved]
    guess_counts = [r.num_guesses for r in solved_results]
    distribution = {k: guess_counts.count(k) for k in range(1, MAX_GUESSES + 1)}

    return {
        "total": n,
        "solved_count": len(solved_results),
        "failed": failed,
        "success_rate": len(solved_results) / n * 100 if n > 0 else 0.0,
        "mean_guesses": sum(guess_counts) / len(guess_counts) if guess_counts else 0.0,
        "distribution": distribution,
        "results": results,
        "elapsed_s": time.time() - t0,
    }
