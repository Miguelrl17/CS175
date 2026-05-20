# Wordle Bot

- read the module doc in main.py for usage
- matplotlib library is optional, only for drawing graphs after benchmarking
- check commit history if you want old performance graphs from prev iterations

Log (Iteration 1/2)

- Implemented initial entropy algorithm, mean guesses ~4.5 sampled over 100/200
- Was running benchmark tests over all possible words, not just wordle answer list
  (which meant the mean guesses is inflated higher, since humans playing Wordle don't need to guess AAHED)
- Once we switched to a proper available guesses/available answers list, benchmark went to ~3.58 guesses with 98% success rate (from 4.34 guesses with 92% success)
  - also had a VOCAB_THRESHOLD that controlled when we were allowed to "sacrifice" guess words for more letters, rather than just using words from available candidates. switched from 8->20 candidates left, but after the new answers list of ~2k came in this threshold became irrelevant
- also switched starting word from SLATE->TARES->CRANE
- the main algorithm is shannon entropy, basically on a single turn you try every single word as the next "guess". then for each "guess", you look through all the other possible "answers" and say "if this were the answer, what pattern would it create for this guess?"
  - then you sort them all in buckets based on the color pattern and calculate the entropy here. the "guess" with the best entropy (lots of small buckets) wins.
  - so basically were saying, which guess gives the smallest buckets? AKA if i do this guess, does it narrow down my possible answers by a lot?

- before we also considered using minmax/brute force search trees but that took too long, so we decided on entropy strategy instead
- can also consider creating a 2-move lookup table that precalculates the best 2 moves in advance, would make it even better
- the problem is also not entirely accurate to Wordle since the NY times has its own internal, private answers list. the answer list in this repo is from the original Wordle before being acquired by NYT (but should be similar). However, the words list (total available guesses) is pulled directly from NYT Wordle.

Log (Iteration 3)

- good results now (3.558 avg guesses, 99.7% success), explanation below
- bug: some words in the answer-list were missing from word-list, added them back
- switched opener to SALET
- two ply search on <= 20 candidates
  - basically, when there's 20 candidate answers left we simulate one more move ahead (same entropy algorithm, but we do it one more move ahead just to get a good 2 word follow up pair)
- fixed pruning logic: previously only considered which letters were in/not, ignored counts
  - this meant that we did not know if there was only 1 A in the answer, only that there are A's
  - so if we know there's only one A in the answer, ABASE is still used as a guess
  - so we added extra logic to count how many of each letter there are also, just more accurate pruning
- added multiprocessing parallelization to the benchmark command to make it faster (uses up all but 1 CPU core, beware your laptop fan)
