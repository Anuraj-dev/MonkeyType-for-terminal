"""Highscore storage handling (bootstrap models).

Section 2: defines HighScoreEntry dataclass.
Persistence logic to be implemented later.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

__all__ = [
	"HighScoreEntry",
]


@dataclass(slots=True)
class HighScoreEntry:
	mode_key: str
	wpm: float
	accuracy: float  # 0..1
	raw_wpm: float
	errors: int
	total_chars: int
	timestamp: str  # ISO8601

	@staticmethod
	def create(mode_key: str, wpm: float, accuracy: float, raw_wpm: float, errors: int, total_chars: int) -> "HighScoreEntry":
		return HighScoreEntry(
			mode_key=mode_key,
			wpm=round(wpm, 2),
			accuracy=round(accuracy, 4),
			raw_wpm=round(raw_wpm, 2),
			errors=errors,
			total_chars=total_chars,
			timestamp=datetime.utcnow().isoformat(timespec="seconds") + "Z",
		)
