"""
CS 175 Team 69 (Cody He, Miguel Ruiz Licea, Kailee Tea Kaocharoen)

# solve in normal mode
    python main.py target --target crane

# solve in hard mode (guesses cannot use absent letters)
    python main.py --hard target --target crane

# full benchmark, show chart
    python main.py benchmark

# benchmark without plot
    python main.py benchmark --no-plot

# benchmark random sample of 200 words
    python main.py benchmark --sample 200

# interactive hint mode (enter feedback, solver suggests guesses)
    python main.py interactive

# calculate true optimal opener for the loaded word list (slow)
    python main.py find-opener
"""

import argparse
import random
import sys
from pathlib import Path

from word_list import load_word_list, WORDS
from solver import WordleSolver, OPENER, find_best_opener
from simulator import WordleGame, run_benchmark, MAX_GUESSES
from feedback import GuessFeedback, TileColor


def _print_stats(stats: dict) -> None:
    dist = stats["distribution"]
    max_count = max(dist.values(), default=1)

    print("\n╔══════════════════════════════════╗")
    print("║       Benchmark Results          ║")
    print("╠══════════════════════════════════╣")
    print(f"║  Words tested  : {stats['total']:<15} ║")
    print(f"║  Solved        : {stats['solved_count']:<15} ║")
    print(f"║  Success rate  : {stats['success_rate']:.1f}%{'':<9} ║")
    print(f"║  Mean guesses  : {stats['mean_guesses']:.4f}{'':<9} ║")
    print(f"║  Elapsed       : {stats['elapsed_s']:.1f}s{'':<11} ║")
    print("╠══════════════════════════════════╣")
    print("║  Guess distribution:             ║")
    for k, v in dist.items():
        print(f"║   {k} guesses: {v:>5}  {'':<12} ║")
    print("╚══════════════════════════════════╝")

    if stats["failed"]:
        preview = ", ".join(stats["failed"][:15])
        suffix = (
            f" ... (+{len(stats['failed'])-15} more)"
            if len(stats["failed"]) > 15
            else ""
        )
        print(f"\nFailed words: {preview}{suffix}")


def _plot_distribution(stats: dict, opener: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[!] matplotlib not installed.")
        return

    dist = stats["distribution"]
    keys = list(dist.keys())
    vals = list(dist.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4ade80" if k <= 3 else "#facc15" if k <= 5 else "#f87171" for k in keys]
    bars = ax.bar(keys, vals, color=colors, edgecolor="white", linewidth=0.8)
    ax.bar_label(bars, padding=3)

    ax.set_xlabel("Number of guesses", fontsize=12)
    ax.set_ylabel("Words solved", fontsize=12)
    ax.set_title(
        f"Wordle Solver - Guess Distribution\n"
        f"Opener: {opener}  |  "
        f"Mean: {stats['mean_guesses']:.3f}  |  "
        f"Success: {stats['success_rate']:.1f}%",
        fontsize=13,
    )
    ax.set_xticks(keys)
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()

    out = Path("benchmark_results.png")
    plt.savefig(out, dpi=150)
    print(f"\nPlot saved -> {out.resolve()}")
    plt.show()


def cmd_target(args: argparse.Namespace, word_list: list[str]) -> None:
    target = args.target.upper()
    if target not in set(word_list):
        print(f"[!] '{target}' is not in the word list.")
        sys.exit(1)

    solver = WordleSolver(word_list, hard_mode=args.hard)
    game = WordleGame(word_list, target)

    print(f"\nTarget : {target}")
    print(f"Mode   : {'hard' if args.hard else 'normal'}\n")

    result = game.play(solver, verbose=True)

    if result.solved:
        print(f"Solved in {result.num_guesses} guess(es).")
    else:
        print(f"Failed to solve '{target}' within {MAX_GUESSES} guesses.")


def cmd_benchmark(args: argparse.Namespace, word_list: list[str]) -> None:
    sample = None
    if args.sample and args.sample < len(word_list):
        sample = random.sample(word_list, args.sample)
        print(f"Sampling {args.sample} words from the full list of {len(word_list)}.")

    print(f"Opener : {OPENER}")
    print(f"Mode   : {'hard' if args.hard else 'normal'}")
    print(f"Words  : {len(sample) if sample else len(word_list)}\n")

    solver = WordleSolver(word_list, hard_mode=args.hard)
    stats = run_benchmark(word_list, solver, show_progress=True, sample=sample)

    _print_stats(stats)

    if not args.no_plot:
        _plot_distribution(stats, OPENER)


def cmd_interactive(args: argparse.Namespace, word_list: list[str]) -> None:
    solver = WordleSolver(word_list, hard_mode=args.hard)
    solver.reset()

    color_map = {"G": TileColor.GREEN, "Y": TileColor.YELLOW, "X": TileColor.GRAY}

    print("\nInteractive mode")
    print("─────────────────────────────────────────")
    print("Enter feedback as 5 characters:")
    print("G = green   Y = yellow   X = grey")
    print("─────────────────────────────────────────\n")

    for turn in range(1, MAX_GUESSES + 1):
        guess = solver.next_guess()
        print(f"Turn {turn}  ->  Guess: {guess}")

        while True:
            raw = input("Feedback (e.g. XYGXG or 'q' to quit): ").strip().upper()
            if raw == "Q":
                print("Goodbye!")
                return
            if len(raw) == 5 and all(c in "GYX" for c in raw):
                break
            print("[!] Enter exactly 5 characters from G / Y / X.")

        fb = GuessFeedback(
            guess=guess,
            colors=[color_map[c] for c in raw],
        )
        solver.observe(fb)

        if fb.is_win():
            print(f"\nSolved in {turn} guess(es)!")
            return

        print(f"Candidates remaining: {solver.num_candidates}\n")

    print(f"\nCould not solve within {MAX_GUESSES} guesses.")


def cmd_find_opener(args: argparse.Namespace, word_list: list[str]) -> None:
    print(f"\nWord list size: {len(word_list)}")
    print("Warning: this may take several minutes...\n")
    word, h = find_best_opener(word_list)
    print(f"\nBest opener: {word}  ({h:.4f} bits of entropy)")
    print(f"Update OPENER in solver.py to '{word}' to use it.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--words",
        default=str(WORDS),
        metavar="FILE",
        help="Path to word list file",
    )
    parser.add_argument(
        "--hard",
        action="store_true",
        help="Hard mode",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_target = sub.add_parser("target", help="Solve a specific target word")
    p_target.add_argument(
        "--target",
        required=True,
        metavar="WORD",
        help="The secret word to solve",
    )

    p_bench = sub.add_parser(
        "benchmark", help="Run over the full word list and report statistics"
    )
    p_bench.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip the matplotlib chart",
    )
    p_bench.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="Evaluate a random sample of N words instead of the full list",
    )

    sub.add_parser(
        "interactive",
        help="Get guess suggestions; you supply the colour feedback manually",
    )

    sub.add_parser(
        "find-opener",
        help="Compute the true entropy optimal opener",
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    word_list = load_word_list(args.words)
    if not word_list:
        print("[!] Word list is empty or could not be loaded.")
        sys.exit(1)

    dispatch = {
        "target": cmd_target,
        "benchmark": cmd_benchmark,
        "interactive": cmd_interactive,
        "find-opener": cmd_find_opener,
    }
    dispatch[args.command](args, word_list)


if __name__ == "__main__":
    main()
