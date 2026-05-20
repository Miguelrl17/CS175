import time
from multiprocessing import Pool, cpu_count

from solver import WordleSolver
from simulator import GameResult, WordleGame, MAX_GUESSES

_worker_solver: WordleSolver | None = None


def _init_worker(word_list, answers, hard_mode):
    global _worker_solver
    _worker_solver = WordleSolver(word_list, answers, hard_mode=hard_mode)


def _play_one(args) -> GameResult:
    target, answer_list = args
    game = WordleGame(answer_list, target)
    return game.play(_worker_solver)  # type: ignore


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

    args = [(target, answer_list) for target in targets]
    initargs = (solver.word_list, solver.answers, solver.hard_mode)
    workers = max(1, cpu_count() - 1)

    with Pool(processes=workers, initializer=_init_worker, initargs=initargs) as pool:
        for i, result in enumerate(pool.imap_unordered(_play_one, args, chunksize=4)):
            results.append(result)
            if not result.solved:
                failed.append(result.target)

            if show_progress and (i % 10 == 0 or i == n - 1):
                elapsed = time.time() - t0
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (n - i - 1) / rate if rate > 0 else 0
                print(
                    f"\r[{i+1}/{n}]  {(i+1)/n*100:5.1f}%  "
                    f"elapsed {elapsed:6.1f}s  ETA {eta:5.1f}s   ",
                    end="",
                    flush=True,
                )

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
