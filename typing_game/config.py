"""Configuration models and validation utilities.

Section 2 bootstrap: defines ModeConfig and validation helpers.
Further configuration loading / CLI merge logic will be added in later milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

__all__ = [
	"ModeConfig",
	"validate_mode_config",
]


@dataclass(slots=True)
class ModeConfig:
	"""Defines how a typing session should run.

	Exactly one of timed_seconds or word_count must be provided.
	punctuation_prob in [0,1].
	"""

	timed_seconds: Optional[int] = None
	word_count: Optional[int] = None
	punctuation_prob: float = 0.0
	numbers: bool = False
	wordlist_path: Path | None = None
	top_n_highscores: int = 25

	def mode_kind(self) -> str:
		if self.timed_seconds is not None:
			return "timed"
		if self.word_count is not None:
			return "words"
		return "invalid"


def validate_mode_config(cfg: ModeConfig) -> None:
	"""Raise ValueError if cfg is invalid.

	Rules:
	  * Exactly one of timed_seconds / word_count must be set.
	  * Positive values for whichever is set.
	  * punctuation_prob in [0,1].
	  * top_n_highscores > 0.
	"""

	timed_set = cfg.timed_seconds is not None
	words_set = cfg.word_count is not None
	if timed_set == words_set:  # both True or both False
		raise ValueError("Exactly one of timed_seconds or word_count must be specified")
	if cfg.timed_seconds is not None and cfg.timed_seconds <= 0:
		raise ValueError("timed_seconds must be > 0")
	if cfg.word_count is not None and cfg.word_count <= 0:
		raise ValueError("word_count must be > 0")
	if not (0.0 <= cfg.punctuation_prob <= 1.0):
		raise ValueError("punctuation_prob must be between 0 and 1 inclusive")
	if cfg.top_n_highscores <= 0:
		raise ValueError("top_n_highscores must be > 0")
	# Wordlist existence will be validated later when loading; allow None for default.
