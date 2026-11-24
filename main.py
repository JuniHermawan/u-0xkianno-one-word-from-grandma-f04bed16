#!/usr/bin/env python3
"""One Word From Grandma — make.fun entry (program/v1).

Writes exactly one word — the single word the entrant's grandma would
text about AI — to /output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt
when set). No trailing newline: the file is the word and nothing else.

The word is chosen at run time by a deterministic pairwise proxy that
mechanises the published judge brief's decision rule over hand-scored
rubrics (see NOTES.md / calibrate.py):

  Criteria, most important first:
  1. reads as the single word a grandma would text about AI;
  2. sounds like a real grandmother's texting voice, warm and a little
     baffled, the way she would type it to a grandchild;
  3. funny in one word, the joke landing without caption or context;
  4. tied to AI, robots or machines rather than fitting any subject;
  5. a fresh pick rather than the obvious one, still instantly readable.

  Judge rule: the first criterion where two words differ decides,
  unless a later one differs by much more (>= 2 bigger), in which case
  the biggest later difference decides. Margin = the deciding
  difference (1-5); the winner of a call scores 0.5 + margin/10.
  Every candidate plays every other candidate and every control; the
  pick is the highest pairwise win rate, ties broken by hand rubric,
  then by shorter text (the final tie-break favours fewer bytes).

All candidate words below are original, written for this entry in this
session; none copies the house texts. The winning word scored 24/25 on
the hand rubric and a 0.704 pairwise win rate over 53 words in v3.
"""

import os

# ---------------------------------------------------------------------------
# Candidates. Tag, word, hand rubric [c1, c2, c3, c4, c5] (each 0-5).
# Rubrics were scored by hand BEFORE the proxy ran, in three versions:
# v1 = A-Y + controls, v2 adds AA-AL, v3 adds AM-AT.
# ---------------------------------------------------------------------------
CANDIDATES = [
    # --- v1 ---
    ("A",  "Robit",       [5, 5, 5, 5, 4]),  # typo of robot; the typo IS the joke
    ("B",  "Doohickey",   [4, 5, 4, 2, 4]),  # peak grandma word, weak AI tie
    ("C",  "Witchcraft",  [4, 4, 5, 3, 5]),  # she thinks AI is witchcraft
    ("D",  "Chatterbox",  [4, 5, 4, 4, 4]),  # grandma word for the chatbot
    ("E",  "Contraption", [4, 4, 4, 4, 4]),  # grandma word for a machine
    ("F",  "Toaster",     [3, 4, 5, 3, 5]),  # she thinks the AI is a toaster
    ("G",  "Chatty",      [4, 4, 4, 4, 4]),  # she nicknames ChatGPT "Chatty"
    ("H",  "Tinman",      [3, 3, 4, 5, 5]),  # Wizard of Oz robot, grandma-era
    ("I",  "Calculator",  [3, 4, 4, 3, 4]),  # "just a fancy calculator"
    ("J",  "Smarty",      [3, 4, 4, 3, 4]),  # grandma calls AI a smarty
    ("K",  "Gizmo",       [3, 4, 3, 3, 3]),  # grandma gadget word
    ("L",  "Thingy",      [3, 5, 4, 1, 3]),  # THE grandma word, fits anything
    ("M",  "Beepboop",    [3, 3, 4, 5, 3]),  # robot noises, meme-obvious
    ("N",  "Robo",        [4, 3, 3, 5, 3]),  # diminutive robot, a bit obvious
    ("O",  "Sparky",      [3, 4, 4, 3, 5]),  # she names the robot Sparky
    ("P",  "Rusty",       [3, 4, 4, 3, 5]),  # she names the robot Rusty
    ("Q",  "Hocuspocus",  [3, 4, 4, 3, 4]),  # AI as hocus-pocus
    ("R",  "Encyclopedia",[3, 4, 4, 3, 4]),  # AI as the encyclopedia
    ("S",  "Typewriter",  [3, 4, 4, 3, 5]),  # AI as a fancy typewriter
    ("T",  "Rosie",       [2, 4, 3, 3, 5]),  # Jetsons robot maid, needs the ref
    ("U",  "Knowitall",   [3, 4, 4, 3, 4]),  # AI the know-it-all
    ("V",  "Doodad",      [3, 4, 4, 2, 4]),  # grandma gadget word
    ("W",  "Whatchamacallit", [3, 5, 4, 1, 4]),  # peak grandma, fits anything
    ("X",  "Thingamajig", [3, 5, 4, 2, 3]),  # grandma word, weak AI tie
    ("Y",  "Blinky",      [3, 3, 3, 4, 4]),  # she names it Blinky (lights)
    # --- v2 challengers ---
    ("AA", "Compooter",   [5, 5, 5, 4, 4]),  # classic grandma typo of computer
    ("AB", "Telebision",  [5, 5, 4, 3, 4]),  # grandma typo of television
    ("AC", "Interweb",    [4, 4, 4, 3, 4]),  # she calls it the interweb
    ("AD", "Googles",     [4, 4, 4, 2, 4]),  # "the Googles"
    ("AE", "Alexa",       [4, 3, 3, 4, 2]),  # real AI she talks to, obvious
    ("AF", "Siri",        [4, 3, 3, 4, 2]),  # same as Alexa
    ("AG", "Robott",      [5, 5, 4, 5, 3]),  # double-t typo of robot
    ("AH", "Rebot",       [5, 4, 4, 5, 4]),  # vowel-swap typo of robot
    ("AI", "Roboot",      [5, 4, 4, 5, 3]),  # double-o typo of robot
    ("AJ", "Wifis",       [4, 4, 4, 3, 4]),  # grandma pluralises the wifi
    ("AK", "Bleepbloop",  [3, 3, 4, 5, 3]),  # robot noises, meme-obvious
    ("AL", "Whirlygig",   [3, 4, 3, 3, 4]),  # old word for a spinning thing
    # --- v3 challengers ---
    ("AM", "Artifical",   [4, 4, 4, 4, 4]),  # typo of artificial (intelligence)
    ("AN", "MrRobit",     [4, 4, 5, 5, 5]),  # she addresses it as Mr. Robit
    ("AO", "Robbie",      [3, 4, 4, 4, 4]),  # she names the robot Robbie
    ("AP", "Beeper",      [3, 4, 3, 4, 4]),  # robot beep + grandma word
    ("AQ", "Clankety",    [3, 4, 4, 4, 4]),  # old-fashioned robot-sound word
    ("AR", "Whatsit",     [3, 5, 4, 2, 4]),  # grandma word for the thing
    ("AS", "Dingbat",     [2, 4, 4, 2, 4]),  # grandma insult, weak AI tie
    ("AT", "Overlords",   [3, 3, 4, 4, 3]),  # robot overlords joke
    # --- controls (obvious / weak) ---
    ("Z1", "Robot",       [4, 2, 2, 5, 1]),
    ("Z2", "Wow",         [2, 2, 1, 1, 2]),
    ("Z3", "AI",          [3, 1, 1, 5, 1]),
    ("Z4", "Amazing",     [2, 2, 1, 1, 2]),
    ("Z5", "Scary",       [2, 2, 2, 2, 2]),
    ("Z6", "LOL",         [2, 5, 4, 1, 2]),
    ("Z7", "Hello",       [1, 2, 1, 1, 2]),
    ("Z8", "Skynet",      [2, 1, 2, 5, 2]),
]


def decide(a, b):
    """Pairwise verdict per the judge's rule. Returns (winner, margin):
    winner 1 if a wins, -1 if b wins, 0 on an exact tie."""
    diffs = [x - y for x, y in zip(a, b)]
    first = next((i for i, d in enumerate(diffs) if d != 0), None)
    if first is None:
        return 0, 0
    fd = abs(diffs[first])
    best_later = None
    for j in range(first + 1, 5):
        if abs(diffs[j]) >= fd + 2:
            if best_later is None or abs(diffs[j]) > abs(diffs[best_later]):
                best_later = j
    idx = first if best_later is None else best_later
    d = diffs[idx]
    return (1 if d > 0 else -1), min(5, abs(d))


def win_rate(word_scores, all_scores):
    total, games = 0.0, 0
    for other in all_scores:
        if other is word_scores:
            continue
        win, margin = decide(word_scores, other)
        total += 0.5 if win == 0 else (0.5 + margin / 10.0 if win == 1
                                       else 0.5 - margin / 10.0)
        games += 1
    return total / games


def pick():
    scores = [c[2] for c in CANDIDATES]
    best = None
    for tag, word, rubric in CANDIDATES:
        wr = win_rate(rubric, scores)
        key = (round(wr, 3), sum(rubric), -len(word))
        if best is None or key > best[0]:
            best = (key, tag, word, wr, sum(rubric))
    return best


def main():
    _key, tag, word, wr, rubric = pick()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(word)
    os.chmod(path, 0o644)
    # Gate self-check: UTF-8, 1-30 chars, non-whitespace, exactly one word.
    assert 1 <= len(word) <= 30, "gate: length"
    assert word.strip() and len(word.split()) == 1, "gate: one word"
    print(f"pick {tag}: {word!r} winrate={wr:.3f} rubric={rubric}/25 "
          f"chars={len(word)}")


if __name__ == "__main__":
    main()
