"""Metrics computation layer bootstrap models.

Implements LiveStats dataclass and make_mode_key helper (section 2).
Actual incremental metric updates added later.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .config import ModeConfig

__all__ = [
	"LiveStats",
	"make_mode_key",
]


@dataclass(slots=True)
class LiveStats:
	started_at: float
	last_update: float
	chars_typed: int = 0
	errors: int = 0
	correct_chars: int = 0
	finished: bool = False

	def accuracy(self) -> float:
		if self.chars_typed == 0:
			return 0.0
		return (self.correct_chars / self.chars_typed)


def make_mode_key(cfg: ModeConfig) -> str:
	"""Return a canonical key for a mode for highscore grouping.

	Format examples:
	  timed-60-p0-n0
	  words-50-p10-n1
	Where p is punctuation_prob * 100 (int), n is numbers flag 0/1.
	"""
	if cfg.timed_seconds is not None:
		base = f"timed-{cfg.timed_seconds}"
	else:
		base = f"words-{cfg.word_count}"
	p = int(round(cfg.punctuation_prob * 100))
	n = 1 if cfg.numbers else 0
	return f"{base}-p{p}-n{n}"
