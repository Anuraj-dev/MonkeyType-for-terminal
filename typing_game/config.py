"""Configuration models, loading, merging and persistence utilities.

Implements Section 6 of the project plan:
 - Default config loader
 - CLI merge function
 - Persistence of last used settings
 - Validation helpers (duration/word count, punctuation probability, wordlist existence)
 - get_or_create_config_path helper

The CLI layer (argparse) can pass either an ``argparse.Namespace`` or a
plain mapping to :func:`merge_cli_args` and receive a validated ``ModeConfig``.
Persistence is intentionally minimal JSON storing only primitive fields.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Any, Mapping
import json

# Public API re-export list

__all__ = [
	"ModeConfig",
	"validate_mode_config",
	"default_config",
	"merge_cli_args",
	"get_or_create_config_path",
	"load_last_config",
	"save_last_config",
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
	# Wordlist existence if provided
	if cfg.wordlist_path is not None and not cfg.wordlist_path.exists():
		raise ValueError(f"wordlist path does not exist: {cfg.wordlist_path}")


# ----------------------------- Defaults & Paths -----------------------------
def _project_root() -> Path:
	# typing_game/config.py -> typing_game -> project root (parent of package dir)
	return Path(__file__).resolve().parent.parent


def default_wordlist_path() -> Path | None:
	path = _project_root() / "data" / "wordlists" / "english_1k.txt"
	return path if path.exists() else None


def default_config() -> ModeConfig:
	"""Return a baseline ``ModeConfig`` used when no prior state exists.

	Defaults:
	 timed session 60s, no punctuation, no numbers, bundled word list, top 25 highscores.
	"""
	cfg = ModeConfig(
		timed_seconds=60,
		word_count=None,
		punctuation_prob=0.0,
		numbers=False,
		wordlist_path=default_wordlist_path(),
		top_n_highscores=25,
	)
	# Do not validate wordlist if missing (user could supply later); that's fine.
	if cfg.wordlist_path is not None:
		validate_mode_config(cfg)
	return cfg


def get_or_create_config_path(filename: str = "config.json") -> Path:
	"""Return path to persisted config file, ensuring parent directory exists.

	Uses user home directory ``~/.typing_game``.
	"""
	base = Path.home() / ".typing_game"
	base.mkdir(parents=True, exist_ok=True)
	return base / filename


# ------------------------------- Merge Helpers ------------------------------
def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
	if isinstance(obj, Mapping):  # dict-like
		return obj.get(name, default)
	return getattr(obj, name, default)


def merge_cli_args(base: Optional[ModeConfig], args: Any) -> ModeConfig:
	"""Merge CLI arg structure (Namespace or mapping) into a new ModeConfig.

	Accepted argument names (all optional):
	 timed (int seconds), words (int), punct (float), numbers (bool), list (str path)

	Rules:
	 - If neither timed nor words provided, keep existing from base (or default 60s)
	 - If both provided: error
	 - Providing one clears the other
	 - Punctuation probability must be within [0,1]
	 - Word list path validated if provided
	"""
	if base is None:
		base = default_config()

	timed = _get_attr(args, "timed", None)
	words = _get_attr(args, "words", None)
	punct = _get_attr(args, "punct", None)
	numbers_flag = _get_attr(args, "numbers", None)
	wordlist = _get_attr(args, "list", None)

	if timed is not None and words is not None:
		raise ValueError("Specify only one of --timed or --words")

	new = ModeConfig(
		timed_seconds=(timed if timed is not None else (None if words is not None else base.timed_seconds)),
		word_count=(words if words is not None else (None if timed is not None else base.word_count)),
		punctuation_prob=(punct if punct is not None else base.punctuation_prob),
		numbers=(numbers_flag if numbers_flag is not None else base.numbers),
		wordlist_path=(Path(wordlist) if wordlist is not None else base.wordlist_path),
		top_n_highscores=base.top_n_highscores,
	)
	# validate
	validate_mode_config(new)
	return new


# ------------------------------- Persistence --------------------------------
def _config_to_json(cfg: ModeConfig) -> dict[str, Any]:
	data = asdict(cfg)
	if cfg.wordlist_path is not None:
		data["wordlist_path"] = str(cfg.wordlist_path)
	return data


def save_last_config(cfg: ModeConfig, path: Optional[Path] = None) -> None:
	"""Persist config to JSON. Ignores errors silently (best-effort)."""
	if path is None:
		path = get_or_create_config_path()
	try:
		path.write_text(json.dumps(_config_to_json(cfg), indent=2), encoding="utf-8")
	except OSError:
		pass  # best effort


def load_last_config(path: Optional[Path] = None) -> ModeConfig:
	"""Load last config if present; otherwise return :func:`default_config`.

	Invalid / corrupt files fall back to default.
	"""
	if path is None:
		path = get_or_create_config_path()
	if not path.exists():
		return default_config()
	try:
		data = json.loads(path.read_text(encoding="utf-8"))
		cfg = ModeConfig(
			timed_seconds=data.get("timed_seconds"),
			word_count=data.get("word_count"),
			punctuation_prob=data.get("punctuation_prob", 0.0),
			numbers=data.get("numbers", False),
			wordlist_path=Path(data["wordlist_path"]) if data.get("wordlist_path") else default_wordlist_path(),
			top_n_highscores=data.get("top_n_highscores", 25),
		)
		validate_mode_config(cfg)
		return cfg
	except Exception:
		return default_config()

