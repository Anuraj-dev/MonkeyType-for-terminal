"""Highscore storage handling.

Section 5 implementation:
 - Path resolution with local file or user home fallback
 - Graceful load (missing / corrupt returns empty structure)
 - Insert logic sorted by WPM desc, tie accuracy desc
 - Truncate list per mode to top N (configurable)
 - Atomic write using temp file then replace
 - record_highscore(mode_key, entry) API returning bool if entry kept

Data format on disk (JSON):
{
  "modes": {
	  "<mode_key>": [
		  {"mode_key": str, "wpm": float, "accuracy": float, "raw_wpm": float,
			"errors": int, "total_chars": int, "timestamp": str}
	  ]
  }
}
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
import json
import os
from typing import Dict, List, Any

__all__ = [
	"HighScoreEntry",
	"get_highscores_path",
	"load_highscores",
	"save_highscores",
	"insert_entry",
	"record_highscore",
	"get_top_highscores",
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
		# Use 'Z' suffix for UTC to satisfy tests expecting trailing Z.
		iso = datetime.now(UTC).replace(tzinfo=UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
		return HighScoreEntry(
			mode_key=mode_key,
			wpm=round(wpm, 2),
			accuracy=round(accuracy, 4),
			raw_wpm=round(raw_wpm, 2),
			errors=errors,
			total_chars=total_chars,
			timestamp=iso,
		)

	def to_dict(self) -> dict[str, Any]:
		return {
			"mode_key": self.mode_key,
			"wpm": self.wpm,
			"accuracy": self.accuracy,
			"raw_wpm": self.raw_wpm,
			"errors": self.errors,
			"total_chars": self.total_chars,
			"timestamp": self.timestamp,
		}

	@staticmethod
	def from_dict(d: dict[str, Any]) -> "HighScoreEntry":
		return HighScoreEntry(**d)


def get_highscores_path(preferred: Path | None = None) -> Path:
	"""Return path to highscores.json, using preferred or fallback locations.

	Resolution order:
	  1. Explicit preferred path if provided.
	  2. Local working directory file 'highscores.json' if exists.
	  3. Local working directory (create later when saving).
	  4. User home fallback (~/.typing_game_highscores.json)
	"""
	if preferred is not None:
		return preferred
	local = Path.cwd() / "highscores.json"
	if local.exists():
		return local
	# choose local by default; only fallback to home if local unwritable
	try:
		parent = local.parent
		if parent.exists() and os.access(parent, os.W_OK):
			return local
	except OSError:
		pass
	return Path.home() / ".typing_game_highscores.json"


def _empty_store() -> dict[str, list[HighScoreEntry]]:
	return {}


def load_highscores(path: Path | None = None) -> dict[str, list[HighScoreEntry]]:
	p = get_highscores_path(path)
	if not p.exists():
		return _empty_store()
	try:
		raw = json.loads(p.read_text(encoding="utf-8"))
		modes = raw.get("modes", {}) if isinstance(raw, dict) else {}
		out: dict[str, list[HighScoreEntry]] = {}
		for k, lst in modes.items():
			if not isinstance(lst, list):
				continue
			entries: list[HighScoreEntry] = []
			for item in lst:
				if isinstance(item, dict):
					try:
						entries.append(HighScoreEntry.from_dict(item))
					except TypeError:
						continue
			out[k] = entries
		return out
	except Exception:
		return _empty_store()


def save_highscores(data: dict[str, list[HighScoreEntry]], path: Path | None = None) -> None:
	p = get_highscores_path(path)
	serializable = {
		"modes": {k: [e.to_dict() for e in lst] for k, lst in data.items()}
	}
	tmp = p.with_suffix(p.suffix + ".tmp")
	tmp.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
	tmp.replace(p)


def insert_entry(
	store: dict[str, list[HighScoreEntry]],
	entry: HighScoreEntry,
	top_n: int = 25,
) -> bool:
	"""Insert entry into store (in-place) maintaining ordering & truncation.

	Returns True if entry is kept (in top_n) for its mode.
	Ordering: WPM desc, then accuracy desc, then timestamp asc (older first).
	"""
	lst = store.setdefault(entry.mode_key, [])
	lst.append(entry)
	lst.sort(key=lambda e: (-e.wpm, -e.accuracy, e.timestamp))
	if len(lst) > top_n:
		trimmed = lst[:top_n]
		kept = entry in trimmed
		store[entry.mode_key] = trimmed
		return kept
	return True


def record_highscore(
	mode_key: str,
	entry: HighScoreEntry,
	path: Path | None = None,
	top_n: int = 25,
) -> bool:
	"""Add a highscore entry and persist.

	Returns True if entry ended up stored; False if discarded due to ranking.
	"""
	store = load_highscores(path)
	kept = insert_entry(store, entry, top_n=top_n)
	if kept:
		save_highscores(store, path)
	return kept


def get_top_highscores(mode_key: str, limit: int = 10, path: Path | None = None) -> list[HighScoreEntry]:
	"""Return up to `limit` highscores for the given mode key.

	Results are ordered using the same ordering logic as insertion.
	This is a read-only helper for display purposes.
	"""
	if limit <= 0:
		return []
	store = load_highscores(path)
	entries = store.get(mode_key, [])
	# Ensure ordering (in case file manually edited)
	ordered = sorted(entries, key=lambda e: (-e.wpm, -e.accuracy, e.timestamp))
	return ordered[:limit]
