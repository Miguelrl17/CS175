
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TileColor(str, Enum):
    GREEN  = "G"
    YELLOW = "Y"
    GRAY   = "X"


@dataclass
class GuessFeedback:
    guess:  str
    colors: list[TileColor]

    def is_win(self) -> bool:
        return all(c == TileColor.GREEN for c in self.colors)

    def __str__(self) -> str:
        color_map = {TileColor.GREEN: "🟩", TileColor.YELLOW: "🟨", TileColor.GRAY: "⬜"}
        tiles = "".join(color_map[c] for c in self.colors)
        return f"{self.guess}  {tiles}"


@dataclass
class GameState:
    green_letters:  dict[int, str]       = field(default_factory=dict)
    yellow_letters: dict[str, set[int]]  = field(default_factory=dict)
    gray_letters:   set[str]             = field(default_factory=set)
    history:        list[GuessFeedback]  = field(default_factory=list)

    def update(self, feedback: GuessFeedback) -> None:
        self.history.append(feedback)
        confirmed_counts: dict[str, int] = {}

        for pos, (letter, color) in enumerate(zip(feedback.guess, feedback.colors)):
            if color == TileColor.GREEN:
                self.green_letters[pos] = letter
                confirmed_counts[letter] = confirmed_counts.get(letter, 0) + 1

            elif color == TileColor.YELLOW:
                if letter not in self.yellow_letters:
                    self.yellow_letters[letter] = set()
                self.yellow_letters[letter].add(pos)
                confirmed_counts[letter] = confirmed_counts.get(letter, 0) + 1

            elif color == TileColor.GRAY:
                if letter not in confirmed_counts:
                    self.gray_letters.add(letter)

    def guess_count(self) -> int:
        return len(self.history)

    def is_solved(self) -> bool:
        return bool(self.history) and self.history[-1].is_win()

    def __str__(self) -> str:
        lines = ["=== Game State ==="]
        for fb in self.history:
            lines.append(f"  {fb}")
        lines.append(f"  Green  : {self.green_letters}")
        lines.append(f"  Yellow : {dict(self.yellow_letters)}")
        lines.append(f"  Gray   : {sorted(self.gray_letters)}")
        return "\n".join(lines)


def compute_feedback(guess: str, target: str) -> GuessFeedback:
    guess  = guess.upper()
    target = target.upper()
    assert len(guess) == len(target) == 5

    colors: list[Optional[TileColor]] = [None] * 5
    remaining: list[Optional[str]]    = list(target)

    for i in range(5):
        if guess[i] == target[i]:
            colors[i]    = TileColor.GREEN
            remaining[i] = None 

    for i in range(5):
        if colors[i] is not None:
            continue 
        letter = guess[i]
        if letter in remaining:
            colors[i] = TileColor.YELLOW
            remaining[remaining.index(letter)] = None
        else:
            colors[i] = TileColor.GRAY

    return GuessFeedback(guess=guess, colors=colors)   # type: ignore[arg-type]
