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
from typing import Iterable, Iterator, Callable

from .metrics import LiveStats, update_on_char, compute_raw_wpm, compute_net_wpm
from typing import Optional
from .metrics import elapsed_seconds
from .storage import HighScoreEntry, record_highscore, load_highscores
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

	previous_best_net_wpm: Optional[float] = None

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


def run_session(
	cfg: ModeConfig,
	*,
	input_func: Callable[[str], str] | None = None,
	time_func: Callable[[], float] | None = None,
) -> SessionResult:
	"""Run a typing session in plain stdin loop.

	Parameters:
		cfg: Mode configuration.
		input_func: (testing) function to obtain user input; defaults to built-in input.
		time_func: (testing) monotonic time function returning float seconds; defaults to time.monotonic.

	Returns:
		SessionResult summary of the session.
	"""
	validate_mode_config(cfg)
	if time_func is None:
		time_func = time.monotonic
	if input_func is None:
		input_func = input  # pragma: no cover - real interactive path
	started = time_func()
	stats = LiveStats(started_at=started, last_update=started)

	if cfg.timed_seconds is not None:
		mode = build_timed_mode(cfg.timed_seconds, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)
	else:
		mode = build_word_count_mode(cfg.word_count, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)

	words_iter = _iterate_mode_words(mode)
	targets: list[str] = []
	committed = 0

	while True:
		now = time_func()
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
		typed = input_func(prompt + ": ")
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
	# previous best lookup BEFORE recording new score
	prev_best: Optional[float] = None
	try:
		store = load_highscores()
		if key in store and store[key]:
			prev_best = max((e.wpm for e in store[key]), default=None)
	except Exception:
		pass
	entry = HighScoreEntry.create(key, net_wpm, acc, raw_wpm, stats.errors, stats.chars_typed)
	highscore_new = record_highscore(key, entry, top_n=cfg.top_n_highscores)
	return SessionResult(cfg, raw_wpm, net_wpm, acc, stats.errors, stats.chars_typed, elapsed, highscore_new, previous_best_net_wpm=prev_best)


def _clear_screen():  # pragma: no cover - simple utility
	import os
	cmd = "cls" if os.name == "nt" else "clear"
	try:
		os.system(cmd)
	except Exception:
		print("\n" * 3)


def end_screen(res: SessionResult):  # pragma: no cover - I/O convenience
	_clear_screen()
	print("=== Typing Session Summary ===")
	kind = res.mode_config.mode_kind()
	if kind == "timed":
		desc = f"Timed {res.mode_config.timed_seconds}s"
	else:
		desc = f"Words {res.mode_config.word_count}"
	print(f"Mode: {desc}")
	print(f"Elapsed: {res.elapsed:.1f}s  Raw WPM: {res.raw_wpm:.2f}  Net WPM: {res.net_wpm:.2f}")
	print(f"Accuracy: {res.accuracy*100:.2f}%  Errors: {res.errors}  Chars: {res.chars}")
	if res.previous_best_net_wpm is not None:
		print(f"Previous Best Net WPM: {res.previous_best_net_wpm:.2f}")
	if res.highscore_new:
		print("*** NEW HIGHSCORE! ***")
	print("==============================")


_fallback_banner_printed = False


def _maybe_print_fallback_banner():  # pragma: no cover - simple UX hint
	global _fallback_banner_printed
	if _fallback_banner_printed:
		return
	try:
		import curses  # type: ignore
	except Exception:
		print("[Plain Mode] Running without curses (limited live feedback).")
		print("Install 'windows-curses' on Windows for full UI later.")
	finally:
		_fallback_banner_printed = True


def _prompt_mode_change(current: ModeConfig) -> ModeConfig:  # pragma: no cover - user interaction
	print("Change mode:")
	print(" 1) Timed")
	print(" 2) Word-count")
	print(" 3) Toggle punctuation (current %.2f)" % current.punctuation_prob)
	print(" 4) Toggle numbers (currently %s)" % ("ON" if current.numbers else "OFF"))
	print(" 5) Change word list")
	choice = input("Select option (blank to cancel): ").strip()
	if choice == "1":
		val = input("Seconds: ").strip()
		try:
			secs = int(val)
			return ModeConfig(timed_seconds=secs, word_count=None, punctuation_prob=current.punctuation_prob, numbers=current.numbers, wordlist_path=current.wordlist_path, top_n_highscores=current.top_n_highscores)
		except ValueError:
			print("Invalid seconds")
	elif choice == "2":
		val = input("Word count: ").strip()
		try:
			wc = int(val)
			return ModeConfig(timed_seconds=None, word_count=wc, punctuation_prob=current.punctuation_prob, numbers=current.numbers, wordlist_path=current.wordlist_path, top_n_highscores=current.top_n_highscores)
		except ValueError:
			print("Invalid number")
	elif choice == "3":
		val = input("New punctuation probability 0..1: ").strip()
		try:
			p = float(val)
			if 0 <= p <= 1:
				current.punctuation_prob = p
		except ValueError:
			pass
	elif choice == "4":
		current.numbers = not current.numbers
	elif choice == "5":
		path = input("Word list path: ").strip()
		if path:
			from pathlib import Path
			p = Path(path)
			if p.exists():
				current.wordlist_path = p
	return current


def interactive_loop(initial_cfg: ModeConfig):  # pragma: no cover - user interaction
	_maybe_print_fallback_banner()
	cfg = initial_cfg
	while True:
		try:
			res = run_session(cfg)
		except KeyboardInterrupt:
			print("\n[Interrupted] Returning to menu.")
			break
		end_screen(res)
		choice = input("(R)estart / (M)ode change / (Q)uit? ").strip().lower()
		if choice.startswith("q"):
			break
		if choice.startswith("m"):
			cfg = _prompt_mode_change(cfg)
			continue
		# default restart same
		continue
