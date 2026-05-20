def is_consistent(word, state) -> bool:
    word = word.upper()

    for pos, letter in state.green_letters.items():
        if word[pos] != letter:
            return False

    for letter, bad_positions in state.yellow_letters.items():
        if letter not in word:
            return False
        for pos in bad_positions:
            if word[pos] == letter:
                return False

    for letter, min_count in state.letter_min_count.items():
        if word.count(letter) < min_count:
            return False
    for letter, max_count in state.letter_max_count.items():
        if word.count(letter) > max_count:
            return False

    return True


def prune(candidates, state):
    return [w for w in candidates if is_consistent(w, state)]
