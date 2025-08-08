"""Game engine core.

Section 9 partial implementation (non-curses prototype):
 - Initialize stats & timers
 - Word acquisition via mode abstraction
 - Input loop (blocking line-based for prototype)
 - Backspace handling (line-editing before submit)
 - Space triggers word commit (line parsing)
 - End conditions (timed vs word-count)
 - Early quit ("/quit")
 - Compute final metrics (raw/net WPM, accuracy)
 - Call highscore persistence
 - End screen summary + simple restart prompt

NOTE: This is a simplified version using plain stdin for early milestone; real-time
keystroke handling & curses integration will replace this in later milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable, Iterator

from .metrics import LiveStats, update_on_char, compute_raw_wpm, compute_net_wpm
from .metrics import elapsed_seconds
from .storage import HighScoreEntry, record_highscore
from .modes import build_timed_mode, build_word_count_mode, mode_key
from .config import ModeConfig, validate_mode_config
from .words import load_words

__all__ = [
	"run_session",
]


@dataclass
class SessionResult:
	mode_config: ModeConfig
	raw_wpm: float
	net_wpm: float
	accuracy: float
	errors: int
	chars: int
	elapsed: float
	highscore_new: bool


def _commit_word(stats: LiveStats, target: str, typed: str):
	# update per-character stats for entire word + trailing space
	for i, ch in enumerate(typed):
		correct = i < len(target) and ch == target[i]
		update_on_char(stats, correct)
	# Count omissions (characters not typed) as errors? For now: ignore omissions.
	# Space after word (unless last) counted when user entered space; already handled.


def _iterate_mode_words(mode) -> Iterator[str]:
	w = mode.words()
	if isinstance(w, Iterator):
		return w
	return iter(w)


def run_session(cfg: ModeConfig) -> SessionResult:
	"""Run a typing session in plain stdin loop.

	Returns SessionResult after completion or early quit.
	"""
	validate_mode_config(cfg)
	started = time.monotonic()
	stats = LiveStats(started_at=started, last_update=started)

	if cfg.timed_seconds is not None:
		mode = build_timed_mode(cfg.timed_seconds, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)
	else:
		mode = build_word_count_mode(cfg.word_count, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)

	words_iter = _iterate_mode_words(mode)
	targets: list[str] = []
	committed = 0

	while True:
		now = time.monotonic()
		if cfg.timed_seconds is not None and elapsed_seconds(stats, now) >= cfg.timed_seconds:
			break
		if cfg.word_count is not None and committed >= cfg.word_count:
			break
		# fetch next target if needed
		if committed >= len(targets):
			targets.append(next(words_iter))
		target = targets[committed]
		remaining_time = None
		if cfg.timed_seconds is not None:
			remaining_time = max(0, cfg.timed_seconds - elapsed_seconds(stats, now))
		prompt = f"[{committed+1}] {target}"
		if remaining_time is not None:
			prompt += f" ({remaining_time:.1f}s left)"
		typed = input(prompt + ": ")
		if typed.strip() == "/quit":
			break
		_commit_word(stats, target, typed)
		committed += 1
		# space char after word (simulate):
		update_on_char(stats, True)  # treat separating space as correct char for wpm baseline

	elapsed = elapsed_seconds(stats)
	raw_wpm = compute_raw_wpm(stats)
	net_wpm = compute_net_wpm(stats)
	acc = stats.accuracy()
	key = mode_key(cfg)
	entry = HighScoreEntry.create(key, net_wpm, acc, raw_wpm, stats.errors, stats.chars_typed)
	highscore_new = record_highscore(key, entry, top_n=cfg.top_n_highscores)
	return SessionResult(cfg, raw_wpm, net_wpm, acc, stats.errors, stats.chars_typed, elapsed, highscore_new)


def print_summary(res: SessionResult):  # pragma: no cover - I/O convenience
	print("\n--- Session Summary ---")
	print(f"Mode: {res.mode_config.mode_kind()}  Elapsed: {res.elapsed:.1f}s")
	print(f"Raw WPM: {res.raw_wpm:.2f}  Net WPM: {res.net_wpm:.2f}  Accuracy: {res.accuracy*100:.2f}%  Errors: {res.errors}  Chars: {res.chars}")
	if res.highscore_new:
		print("New highscore recorded!")


def interactive_loop(initial_cfg: ModeConfig):  # pragma: no cover - user interaction
	cfg = initial_cfg
	while True:
		res = run_session(cfg)
		print_summary(res)
		choice = input("(R)estart same / (Q)uit? ").strip().lower()
		if choice.startswith("q"):
			break
		# restart same config
		continue
