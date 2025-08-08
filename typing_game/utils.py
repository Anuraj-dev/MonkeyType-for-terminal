"""Utility & performance helpers.

Section 15 additions:
 - Simple debug logger gated by env var TYPING_GAME_DEBUG=1
 - Diff rendering helper (line-based) to minimize output churn
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List

_DEBUG_ENABLED = os.environ.get("TYPING_GAME_DEBUG", "0") in {"1", "true", "True"}


def debug_log(*parts):  # pragma: no cover - side-effect
	if _DEBUG_ENABLED:
		msg = " ".join(str(p) for p in parts)
		sys.stderr.write(f"[DEBUG] {msg}\n")
		sys.stderr.flush()


@dataclass
class DiffResult:
	full: bool
	lines: List[str]
	changed_indices: List[int]


def compute_line_diff(prev: List[str] | None, new: List[str]) -> DiffResult:
	"""Compute which line indices changed.

	If previous is None or lengths diverge by >50%, mark full repaint.
	"""
	if prev is None:
		return DiffResult(full=True, lines=new, changed_indices=list(range(len(new))))
	if not prev or len(prev) == 0:
		return DiffResult(full=True, lines=new, changed_indices=list(range(len(new))))
	# heuristic: if size differs a lot, repaint fully
	if abs(len(prev) - len(new)) > max(3, len(new) // 2):
		return DiffResult(full=True, lines=new, changed_indices=list(range(len(new))))
	changed: List[int] = []
	for i, line in enumerate(new):
		if i >= len(prev) or prev[i] != line:
			changed.append(i)
	if len(prev) != len(new):  # extra trailing removal not handled incrementally
		return DiffResult(full=True, lines=new, changed_indices=changed)
	# If more than half lines changed, repaint all
	if len(changed) > len(new) // 2:
		return DiffResult(full=True, lines=new, changed_indices=changed)
	return DiffResult(full=False, lines=new, changed_indices=changed)


class LineDiffRenderer:
	"""Minimal line-diff renderer using ANSI cursor movement.

	Not a full-screen manager; intended as a lightweight optimization for the
	future curses-less fallback or for debugging performance.
	"""

	def __init__(self, stream=None):
		self._prev: List[str] | None = None
		self._stream = stream or sys.stdout
		# Detect dumb terminal
		self._ansi = os.environ.get("TERM", "dumb") != "dumb"

	def render(self, text: str):  # pragma: no cover - integration side-effect
		lines = text.splitlines()
		diff = compute_line_diff(self._prev, lines)
		if diff.full or not self._ansi:
			self._stream.write("\x1b[2J\x1b[H") if self._ansi else None
			self._stream.write("\n".join(lines) + "\n")
		else:
			# Move cursor to top
			self._stream.write("\x1b[H")
			for idx in diff.changed_indices:
				# Position and rewrite line
				self._stream.write(f"\x1b[{idx+1};1H")
				self._stream.write("\x1b[2K")  # clear line
				self._stream.write(lines[idx] + "\n")
		self._stream.flush()
		self._prev = lines
		debug_log("Rendered lines:", len(lines), "changed:", len(diff.changed_indices), "full:", diff.full)


__all__ = [
	"debug_log",
	"compute_line_diff",
	"DiffResult",
	"LineDiffRenderer",
]
