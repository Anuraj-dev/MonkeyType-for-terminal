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

import time
from dataclasses import dataclass
from typing import Callable, Iterator, Optional
from pathlib import Path

from .config import ModeConfig, validate_mode_config
from .metrics import (
	LiveStats,
	compute_net_wpm,
	compute_raw_wpm,
	elapsed_seconds,
	update_on_char,
	compute_consistency,
)
from .modes import build_timed_mode, build_word_count_mode, mode_key
from .storage import HighScoreEntry, load_highscores, record_highscore
from .ui import (
	CursesSession,
	build_header_line,
	build_progress_bar,
	highlight_word,
	draw_highlighted_word,
	normalize_key,
	wrap_words,
)
from .utils import debug_log
from .sound import play_correct, play_wrong

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
	consistency: float = 0.0

def _commit_word(stats: LiveStats, target: str, typed: str):
	# update per-character stats for entire word + trailing space
	for i, ch in enumerate(typed):
		correct = i < len(target) and ch == target[i]
		update_on_char(stats, correct)

	# Count omissions (characters not typed) as errors
	if len(typed) < len(target):
		omissions = len(target) - len(typed)
		for _ in range(omissions):
			update_on_char(stats, False)  # Each omitted character is an error

	# Play feedback sound based on overall word correctness
	is_correct = (typed == target)
	if is_correct:
		play_correct()
	else:
		play_wrong()
	# Space after word (unless last) counted when user entered space; already handled.


def _analyze_word_errors(target: str, typed: str) -> dict[str, int]:
	"""Analyze typing errors in a word for debugging/feedback.
	
	Returns dict with keys: 'correct', 'wrong', 'omissions', 'extras'
	"""
	correct = 0
	wrong = 0
	
	# Count character-by-character matches/mismatches
	min_len = min(len(target), len(typed))
	for i in range(min_len):
		if target[i] == typed[i]:
			correct += 1
		else:
			wrong += 1
	
	# Count omissions and extras
	omissions = max(0, len(target) - len(typed))
	extras = max(0, len(typed) - len(target))
	
	return {
		'correct': correct,
		'wrong': wrong,
		'omissions': omissions,
		'extras': extras
	}


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
		assert cfg.word_count is not None
		mode = build_word_count_mode(cfg.word_count, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)

	words_iter = _iterate_mode_words(mode)
	targets: list[str] = []
	committed = 0
	word_started_at = started

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
		# record duration for this word
		word_time = time_func() - word_started_at
		if word_time >= 0:
			stats.word_durations.append(word_time)
		word_started_at = time_func()
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
	
	# Only record highscore if it's an improvement or first attempt
	highscore_new = False
	if prev_best is None or net_wpm > prev_best:
		entry = HighScoreEntry.create(key, net_wpm, acc, raw_wpm, stats.errors, stats.chars_typed)
		highscore_new = record_highscore(key, entry, top_n=cfg.top_n_highscores)
	
	consistency = compute_consistency(stats)
	return SessionResult(cfg, raw_wpm, net_wpm, acc, stats.errors, stats.chars_typed, elapsed, highscore_new, previous_best_net_wpm=prev_best, consistency=consistency)


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
	if res.consistency > 0:
		print(f"Consistency: {res.consistency*100:.1f}%")
	
	# Show improvement feedback
	if res.previous_best_net_wpm is not None:
		improvement = res.net_wpm - res.previous_best_net_wpm
		print(f"Previous Best Net WPM: {res.previous_best_net_wpm:.2f}")
		if improvement > 0:
			print(f"🎉 IMPROVEMENT: +{improvement:.2f} WPM!")
		elif improvement < 0:
			print(f"📉 Below best by {abs(improvement):.2f} WPM")
		else:
			print("🎯 Matched your best!")
	else:
		print("🆕 First attempt for this mode!")

	# Sanity: only show saved banner if it actually beat the previous
	if res.highscore_new and (res.previous_best_net_wpm is None or res.net_wpm > res.previous_best_net_wpm):
		print("*** NEW HIGHSCORE SAVED! ***")
	elif res.previous_best_net_wpm is not None and res.net_wpm <= res.previous_best_net_wpm:
		print("💡 No highscore saved (no improvement)")
	print("==============================")


_fallback_banner_printed = False


def _maybe_print_fallback_banner():  # pragma: no cover - simple UX hint
	global _fallback_banner_printed
	if _fallback_banner_printed:
		return
	try:
		__import__("curses")  # type: ignore  # imported for side-effect check only
	except Exception:
		print("[Plain Mode] Running without curses (limited live feedback).")
		print("Install 'windows-curses' on Windows for full UI later.")
	finally:
		_fallback_banner_printed = True


def _choose_difficulty() -> Path | None:  # pragma: no cover - user interaction
	"""Let user choose difficulty level"""
	print("\n🎯 Choose Difficulty Level:")
	print("1. Easy (short common words)")
	print("2. Medium (moderate length words)")  
	print("3. Hard (complex words)")
	print("4. Programming (technical terms)")
	print("5. Alice in Wonderland (book content)")
	print("6. Default (mixed)")
	
	choice = input("\nEnter choice (1-6): ").strip()
	
	wordlist_map = {
		"1": "data/wordlists/easy.txt",
		"2": "data/wordlists/medium.txt", 
		"3": "data/wordlists/hard_words.txt",
		"4": "data/wordlists/programming.txt",
		"5": "data/wordlists/alice_words.txt",
		"6": None  # default
	}
	
	wordlist_path = wordlist_map.get(choice)
	if wordlist_path:
		from pathlib import Path
		path_obj = Path(wordlist_path)
		if path_obj.exists():
			print(f"✅ Selected {path_obj.name}")
			return path_obj
		else:
			print(f"❌ Word list not found: {wordlist_path}")
			return None
	return None


def _prompt_mode_change(current: ModeConfig) -> ModeConfig:  # pragma: no cover - user interaction
	print("Change mode:")
	print(" 1) Timed")
	print(" 2) Word-count")
	print(" 3) Toggle punctuation (current %.2f)" % current.punctuation_prob)
	print(" 4) Toggle numbers (currently %s)" % ("ON" if current.numbers else "OFF"))
	print(" 5) Change difficulty")
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
			prob = float(val)
			if 0 <= prob <= 1:
				current.punctuation_prob = prob
		except ValueError:
			pass
	elif choice == "4":
		current.numbers = not current.numbers
	elif choice == "5":
		new_wordlist = _choose_difficulty()
		if new_wordlist is not None:
			current.wordlist_path = new_wordlist
	return current


def interactive_loop(initial_cfg: ModeConfig):  # pragma: no cover - user interaction
	_maybe_print_fallback_banner()
	cfg = initial_cfg
	while True:
		try:
			# Prefer real-time curses loop if available
			res = _try_realtime_session(cfg)
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


# --------------------------- Real-time Curses Loop ---------------------------

def _try_realtime_session(cfg: ModeConfig) -> SessionResult:
	"""Attempt a real-time curses session; fall back to plain session on failure.

	This early version updates metrics per keystroke and does NOT roll back stats
	on backspace (limitation). Future refinement will reconcile per-word commit
	accuracy with live updates.
	"""
	try:
		__import__("curses")  # type: ignore  # imported for availability check
	except Exception:  # curses not available
		return run_session(cfg)
	try:
		return _run_session_curses(cfg)
	except Exception as e:  # safety fallback
		debug_log("curses loop failed, falling back", e)
		return run_session(cfg)


def _run_session_curses(cfg: ModeConfig) -> SessionResult:  # pragma: no cover - interactive
	validate_mode_config(cfg)
	if cfg.timed_seconds is not None:
		mode = build_timed_mode(cfg.timed_seconds, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)
	else:
		assert cfg.word_count is not None
		mode = build_word_count_mode(cfg.word_count, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path, top_n_highscores=cfg.top_n_highscores)

	# Initialize state
	started = time.monotonic()
	stats = LiveStats(started_at=started, last_update=started)
	words_iter = _iterate_mode_words(mode)
	targets: list[str] = []
	current_index = 0
	typed_current = ""
	word_started_at = started

	with CursesSession() as scr:
		# If fallback (scr is None) revert to plain
		if scr is None:
			return run_session(cfg)
		scr.nodelay(True)
		curses = __import__("curses")  # local ref
		while True:
			now = time.monotonic()
			# End conditions
			if cfg.timed_seconds is not None and elapsed_seconds(stats, now) >= cfg.timed_seconds:
				break
			if cfg.word_count is not None and current_index >= cfg.word_count:
				break
			# Ensure we have enough upcoming words
			while len(targets) <= current_index + 25:
				try:
					targets.append(next(words_iter))
				except StopIteration:
					break
			target = targets[current_index]

			# Input handling
			try:
				key = scr.getch()
			except Exception:
				key = -1
			if key != -1:
				token = normalize_key(key)
				if token == "BACKSPACE":
					if typed_current:
						typed_current = typed_current[:-1]
				elif token is None:
					pass
				elif token == "/":  # allow /quit prefix style
					# collect command quickly
					typed_current += "/"
				elif token == "q" and not typed_current:  # quick quit if no current typing
					break
				elif key == 10 or key == 13:  # Enter key (CR or LF)
					# commit word on Enter press
					_commit_word(stats, target, typed_current)
					update_on_char(stats, True)  # space char baseline
					current_index += 1
					# record per-word duration
					w_dur = time.monotonic() - word_started_at
					if w_dur >= 0:
						stats.word_durations.append(w_dur)
					word_started_at = time.monotonic()
					typed_current = ""
				elif token == " ":
					# commit word
					_commit_word(stats, target, typed_current)
					update_on_char(stats, True)  # space char baseline
					current_index += 1
					# record per-word duration
					w_dur = time.monotonic() - word_started_at
					if w_dur >= 0:
						stats.word_durations.append(w_dur)
					word_started_at = time.monotonic()
					typed_current = ""
				else:
					# normal char
					ch = token
					idx = len(typed_current)
					correct = idx < len(target) and ch == target[idx]
					update_on_char(stats, correct)
					typed_current += ch
					# auto commit if full length typed and next key not needed
					if len(typed_current) >= len(target):
						# Wait for space OR auto-commit? We'll wait for explicit space to mimic plain mode.
						pass

			# Rendering
			scr.erase()
			# Header
			elapsed = elapsed_seconds(stats, now)
			raw_wpm = compute_raw_wpm(stats, now)
			net_wpm = compute_net_wpm(stats, now)
			acc = stats.accuracy() * 100
			if cfg.timed_seconds is not None:
				prog = elapsed / cfg.timed_seconds if cfg.timed_seconds else 0
				mode_desc = f"Timed {cfg.timed_seconds}s"
			else:
				prog = current_index / cfg.word_count if cfg.word_count else 0
				mode_desc = f"Words {cfg.word_count}"
			bar = build_progress_bar(prog, max(10, min(30, curses.COLS - 60)))
			header = build_header_line(mode_desc, elapsed, net_wpm, stats.accuracy(), stats.errors)
			scr.addnstr(0, 0, header, curses.COLS - 1)
			scr.addnstr(1, 0, bar, curses.COLS - 1)

			# Word area: render upcoming words list
			display_words = [target] + targets[current_index + 1: current_index + 15]
			# For compact list view, render current word unstyled, we'll draw styled overlay below
			wrapped = wrap_words(display_words, max(20, curses.COLS - 2))
			for i, line in enumerate(wrapped[: curses.LINES - 4]):
				scr.addnstr(3 + i, 0, line, curses.COLS - 1)

			# Overlay: prominently show the current word with live caret and colors
			# Place it just above the word list area
			draw_highlighted_word(scr, 2, 0, target, typed_current)
			scr.refresh()
			# Sleep a tiny bit to reduce CPU spin
			time.sleep(0.01)

	# Final commit if user typed something but didn't press space (optional)
	if typed_current:
		_commit_word(stats, target, typed_current)
	# Build result (reuse code path via record)
	elapsed = elapsed_seconds(stats)
	raw_wpm = compute_raw_wpm(stats)
	net_wpm = compute_net_wpm(stats)
	acc = stats.accuracy()
	key = mode_key(cfg)
	prev_best: Optional[float] = None
	try:
		store = load_highscores()
		if key in store and store[key]:
			prev_best = max((e.wpm for e in store[key]), default=None)
	except Exception:
		pass
	# Only record highscore if it's an improvement or first attempt
	highscore_new = False
	if prev_best is None or net_wpm > prev_best:
		entry = HighScoreEntry.create(key, net_wpm, acc, raw_wpm, stats.errors, stats.chars_typed)
		highscore_new = record_highscore(key, entry, top_n=cfg.top_n_highscores)
	consistency = compute_consistency(stats)
	return SessionResult(cfg, raw_wpm, net_wpm, acc, stats.errors, stats.chars_typed, elapsed, highscore_new, previous_best_net_wpm=prev_best, consistency=consistency)
