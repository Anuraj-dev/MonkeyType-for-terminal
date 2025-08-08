"""Word loading & generation utilities.

Implements section 3 tasks: loading, shuffling, generators for timed & word-count
with optional punctuation & numbers injection.
"""

from __future__ import annotations

from pathlib import Path
from random import Random
from typing import Generator

PUNCTUATION = [",", ".", "?", "!", ";"]
NUMBERS = [str(i) for i in range(10)]

_WORD_CACHE: list[str] | None = None

DEFAULT_WORDLIST_PATH = Path(__file__).resolve().parent.parent / "data" / "wordlists" / "english_1k.txt"

def load_words(path: Path | None = None) -> list[str]:
    global _WORD_CACHE
    if _WORD_CACHE is None:
        p = path or DEFAULT_WORDLIST_PATH
        try:
            content = p.read_text(encoding="utf-8").split()
        except FileNotFoundError:
            content = ["example", "words", "missing", "list"]
        _WORD_CACHE = content
    return _WORD_CACHE


def shuffled_words(rng: Random, words: list[str]) -> list[str]:
    """Return a new shuffled copy of words."""
    clone = list(words)
    rng.shuffle(clone)
    return clone


def maybe_inject_punctuation(rng: Random, word: str, probability: float) -> str:
    if probability <= 0:
        return word
    if rng.random() < probability:
        return word + rng.choice(PUNCTUATION)
    return word


def maybe_replace_with_number(rng: Random, word: str, enable_numbers: bool, probability: float = 0.15) -> str:
    if not enable_numbers:
        return word
    if rng.random() < probability:
        return rng.choice(NUMBERS)
    return word


def timed_word_stream(
    rng: Random,
    punctuation_prob: float = 0.0,
    numbers: bool = False,
    base_words: list[str] | None = None,
) -> Generator[str, None, None]:
    """Infinite generator of words for timed mode."""
    words = base_words or load_words()
    idx = 0
    bag = shuffled_words(rng, words)
    while True:
        if idx >= len(bag):
            bag = shuffled_words(rng, words)
            idx = 0
        w = bag[idx]
        idx += 1
        w = maybe_replace_with_number(rng, w, numbers)
        w = maybe_inject_punctuation(rng, w, punctuation_prob)
        yield w


def finite_word_stream(
    count: int,
    rng: Random,
    punctuation_prob: float = 0.0,
    numbers: bool = False,
    base_words: list[str] | None = None,
) -> list[str]:
    """Return a finite list of words for word-count mode."""
    words = base_words or load_words()
    out: list[str] = []
    if not words:
        return out
    bag = shuffled_words(rng, words)
    idx = 0
    while len(out) < count:
        if idx >= len(bag):
            bag = shuffled_words(rng, words)
            idx = 0
        w = bag[idx]
        idx += 1
        w = maybe_replace_with_number(rng, w, numbers)
        w = maybe_inject_punctuation(rng, w, punctuation_prob)
        out.append(w)
    return out


__all__ = [
    "load_words",
    "shuffled_words",
    "timed_word_stream",
    "finite_word_stream",
    "maybe_inject_punctuation",
    "maybe_replace_with_number",
]
