"""Metrics computation layer.

Section 4 implementation:
 - Time source: uses time.monotonic()
 - Incremental update per character typed
 - Accuracy formula
 - Raw (gross) WPM & Net WPM (decision documented below)
 - Consistency placeholder (per-word durations list)
 - Divide-by-zero safeguards

WPM definitions:
	Gross (raw) WPM = (total_chars / 5) / minutes_elapsed
	Net WPM   = ((correct_chars - errors) / 5) / minutes_elapsed (floored at 0)
Rationale: gross reflects overall speed including mistakes; net penalizes errors.
Many platforms show both; we will compute both for later UI display.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .config import ModeConfig

__all__ = [
	"LiveStats",
	"make_mode_key",
	"update_on_char",
	"compute_raw_wpm",
	"compute_net_wpm",
	"elapsed_seconds",
	"compute_consistency",
]


@dataclass(slots=True)
class LiveStats:
	started_at: float
	last_update: float
	chars_typed: int = 0
	errors: int = 0
	correct_chars: int = 0
	finished: bool = False
	word_durations: list[float] = field(default_factory=list)  # consistency placeholder

	def accuracy(self) -> float:
		if self.chars_typed == 0:
			return 0.0
		return self.correct_chars / self.chars_typed


def elapsed_seconds(stats: LiveStats, now: Optional[float] = None) -> float:
	if now is None:
		now = time.monotonic()
	return max(0.0, now - stats.started_at)


def update_on_char(stats: LiveStats, correct: bool, now: Optional[float] = None) -> None:
	"""Update stats for a single typed character.

	Parameters
	----------
	stats : LiveStats (mutated in-place)
	correct : bool  True if character matches target
	now : float | None  Override time for deterministic testing
	"""
	if now is None:
		now = time.monotonic()
	stats.last_update = now
	stats.chars_typed += 1
	if correct:
		stats.correct_chars += 1
	else:
		stats.errors += 1


def _minutes(elapsed: float) -> float:
	return elapsed / 60.0 if elapsed > 0 else 0.0


def compute_raw_wpm(stats: LiveStats, now: Optional[float] = None) -> float:
	e = elapsed_seconds(stats, now)
	if e <= 0:
		return 0.0
	return (stats.chars_typed / 5.0) / _minutes(e)


def compute_net_wpm(stats: LiveStats, now: Optional[float] = None) -> float:
	e = elapsed_seconds(stats, now)
	if e <= 0:
		return 0.0
	effective = max(0, stats.correct_chars - stats.errors)
	return (effective / 5.0) / _minutes(e)


def compute_consistency(stats: LiveStats) -> float:
	"""Return a basic consistency score 0..1 based on per-word durations.

	Heuristic:
	 - Use coefficient of variation (stdev / mean) of word durations (seconds)
	 - Consistency = max(0, 1 - cv)
	 - If fewer than 2 durations, return 0.0 (insufficient data)

	This is an initial placeholder and can be refined (e.g. rolling windows,
	per-word wpm variance) in future enhancements.
	"""
	from statistics import pstdev
	if len(stats.word_durations) < 2:
		return 0.0
	mean = sum(stats.word_durations) / len(stats.word_durations)
	if mean <= 0:
		return 0.0
	stdev = pstdev(stats.word_durations)
	cv = stdev / mean if mean else 0.0
	return max(0.0, min(1.0, 1.0 - cv))


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
