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

    for letter in state.gray_letters:
        green_count = sum(
            1 for l in state.green_letters.values() if l == letter)
        yellow_count = len(state.yellow_letters.get(letter, set()))
        confirmed = green_count + yellow_count

        if confirmed == 0 and letter in word:
            return False
        if confirmed > 0 and word.count(letter) > confirmed:
            return False

    return True


def prune(candidates, state):
    return [w for w in candidates if is_consistent(w, state)]
