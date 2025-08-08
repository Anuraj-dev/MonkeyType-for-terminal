"""Terminal UI layer.

Section 8 implementation (bootstrap – non-interactive demo helpers):
 - Curses initialization + teardown (context manager)
 - Color pairs (correct, wrong, dim, caret)
 - Terminal size measurement helper
 - Render header (mode, list, time, WPM, accuracy, errors) (text builder)
 - Render word area (wrap aware) via pure wrapping + highlighting helpers
 - Highlight correct / incorrect / current caret position
 - Progress bar generator (time or words)
 - Throttle helper (>= 60ms)
 - Fallback plain mode if curses unavailable
 - Pure functions (wrap_words, build_progress_bar, highlight_word) unit-testable

NOTE: The actual game loop integration and on-screen dynamic refresh will be
implemented in the engine milestone; here we focus on structure & pure logic.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from types import ModuleType
from typing import Any, List, Sequence, Tuple, Optional

try:  # runtime optional import
	import curses  # type: ignore
except Exception:  # pragma: no cover - fallback path
	curses = None  # type: ignore[assignment]

__all__ = [
	"CursesSession",
	"UIThrottle",
	"wrap_words",
	"build_progress_bar",
	"highlight_word",
	"build_header_line",
	"normalize_key",
	"is_printable_char",
	"ResizeWatcher",
	"THEMES",
	"get_theme",
]

# ------------------------- Color / Attribute handling -------------------------

COLOR_CORRECT = 1
COLOR_WRONG = 2
COLOR_DIM = 3
COLOR_CARET = 4

# ------------------------------ Theme Registry ------------------------------

THEMES: dict[str, dict[str, int]] = {
	"default": {
		"correct": COLOR_CORRECT,
		"wrong": COLOR_WRONG,
		"dim": COLOR_DIM,
		"caret": COLOR_CARET,
	},
	# Future themes could remap color IDs after initializing curses pairs
}

def get_theme(name: str = "default") -> dict[str, int]:
	return THEMES.get(name, THEMES["default"])  # simple fallback


def _init_colors():  # pragma: no cover (depends on terminal)
	if not curses:
		return
	if not curses.has_colors():
		return
	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(COLOR_CORRECT, curses.COLOR_GREEN, -1)
	curses.init_pair(COLOR_WRONG, curses.COLOR_RED, -1)
	curses.init_pair(COLOR_DIM, curses.COLOR_CYAN, -1)
	curses.init_pair(COLOR_CARET, curses.COLOR_YELLOW, -1)


# ---------------------------- Context Manager ----------------------------

@dataclass
class CursesSession:
	"""Context manager to initialize curses and restore terminal on exit.

	Usage:
		with CursesSession() as scr:
			...
	"""

	screen: Any = None
	fallback: bool = False

	def __enter__(self):  # pragma: no cover (curses specific)
		if curses is None:
			self.fallback = True
			return None
		scr = curses.initscr()
		curses.noecho()
		curses.cbreak()
		scr.keypad(True)
		try:
			curses.curs_set(0)
		except Exception:
			pass
		_init_colors()
		self.screen = scr
		return scr

	def __exit__(self, exc_type, exc, tb):  # pragma: no cover
		if curses and self.screen is not None:
			try:
				curses.nocbreak()
				self.screen.keypad(False)
				curses.echo()
				curses.endwin()
			except Exception:
				pass


# ----------------------------- Throttle Helper -----------------------------

class UIThrottle:
	def __init__(self, min_interval_sec: float = 0.06):
		self.min_interval = min_interval_sec
		self._last = 0.0

	def should_render(self, now: float | None = None) -> bool:
		if now is None:
			now = time.monotonic()
		if now - self._last >= self.min_interval:
			self._last = now
			return True
		return False


# ---------------------------- Pure Helper Logic ----------------------------

def wrap_words(words: Sequence[str], width: int) -> List[str]:
	"""Greedy wrap words into lines not exceeding width (space separated).

	Returns list of line strings (no trailing spaces). Pure & testable.
	"""
	if width <= 0:
		return [" ".join(words)] if words else []
	lines: List[str] = []
	cur: List[str] = []
	cur_len = 0
	for w in words:
		wlen = len(w)
		sep = 1 if cur else 0
		if cur_len + sep + wlen > width and cur:
			lines.append(" ".join(cur))
			cur = [w]
			cur_len = wlen
		else:
			cur.append(w)
			cur_len += sep + wlen
	if cur:
		lines.append(" ".join(cur))
	return lines


def highlight_word(target: str, typed: str, caret: bool = True) -> List[Tuple[str, str]]:
	"""Return list of (segment, style) for a single word.

	style values: 'correct', 'wrong', 'caret' (for next char), 'pending'.
	Caret is placed at next character to type if caret flag True and word not complete.
	Better error visualization for mismatches and omissions.
	"""
	out: List[Tuple[str, str]] = []
	
	# Compare each position of typed vs target
	for i, ch in enumerate(typed):
		if i < len(target) and ch == target[i]:
			out.append((ch, "correct"))
		else:
			# Character is wrong (either mismatch or extra)
			out.append((ch, "wrong"))
	
	# Handle remaining characters in target
	if len(typed) < len(target):
		next_char = target[len(typed)]
		if caret:
			out.append((next_char, "caret"))
			remaining = target[len(typed)+1:]
			if remaining:
				out.append((remaining, "pending"))
		else:
			out.append((target[len(typed):], "pending"))
	
	return out


def build_progress_bar(progress: float, width: int, fill_char: str = "#") -> str:
	"""Build a textual progress bar where 0 <= progress <= 1."""
	progress = max(0.0, min(1.0, progress))
	if width <= 0:
		return ""
	filled = int(round(progress * width))
	return fill_char * filled + "-" * (width - filled)


def build_header_line(mode_desc: str, elapsed: float, wpm: float, accuracy: float, errors: int) -> str:
	return f"{mode_desc} | {elapsed:5.1f}s | WPM {wpm:5.1f} | Acc {accuracy*100:5.1f}% | Err {errors}"


# ---------------------------- Fallback Renderer ----------------------------

def fallback_render_snapshot(words: Sequence[str], current_index: int, typed_current: str) -> str:
	"""Return a simple multi-line fallback rendering string (plain mode)."""
	preview = []
	for i, w in enumerate(words[current_index: current_index + 10]):
		if i == 0:
			segments = highlight_word(w, typed_current)
			preview.append("".join(seg for seg, _ in segments))
		else:
			preview.append(w)
	return " ".join(preview)


def render_curses_example(screen, text: str, row: int = 0):  # pragma: no cover - demonstration
	if not curses or screen is None:
		print(text)
		return
	screen.erase()
	screen.addnstr(row, 0, text, curses.COLS - 1)
	screen.refresh()


# NOTE: Full interactive UI integration (input + dynamic layout) will be added
# in later engine/UI milestones.


# ----------------------- Input Normalization Utilities ----------------------

BACKSPACE_CODES = {8, 127}


def normalize_key(key: int) -> str | None:
	"""Normalize a curses key code / ordinal to semantic token or char.

	Returns one of:
	  - 'BACKSPACE'
	  - 'RESIZE'
	  - single-character string for printable characters
	  - None for ignored control keys
	"""
	if key in BACKSPACE_CODES:
		return "BACKSPACE"
	if curses and key == getattr(curses, "KEY_RESIZE", -9999):
		return "RESIZE"
	# Curses may return negative for special keys; ignore others for now
	if key < 0:
		return None
	if 32 <= key < 127:  # printable ASCII
		return chr(key)
	return None


def is_printable_char(ch: str) -> bool:
	return len(ch) == 1 and 32 <= ord(ch) < 127


# ---------------------------- Resize Watcher ----------------------------

class ResizeWatcher:
	"""Track terminal size changes with debounce.

	Poll-based approach for environments where KEY_RESIZE not relied upon.
	"""

	def __init__(self, debounce_sec: float = 0.15):
		self.debounce = debounce_sec
		self._last_emit = 0.0
		self._last_size: tuple[int, int] | None = None  # (rows, cols)

	def check(self) -> tuple[bool, tuple[int, int] | None]:  # pragma: no cover (needs terminal)
		if not curses:
			return False, None
		rows, cols = curses.LINES, curses.COLS
		size = (rows, cols)
		if self._last_size is None:
			self._last_size = size
			return True, size
		if size != self._last_size:
			now = time.monotonic()
			if now - self._last_emit >= self.debounce:
				self._last_size = size
				self._last_emit = now
				return True, size
		return False, None
