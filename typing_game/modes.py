"""Mode definitions & helpers.

Section 7 implementation providing factories and unified interface.
"""

from __future__ import annotations

from random import Random
from typing import Protocol

from .config import ModeConfig, validate_mode_config
from .metrics import make_mode_key
from .words import finite_word_stream, load_words, timed_word_stream

__all__ = [
	"build_timed_mode",
	"build_word_count_mode",
	"Mode",
	"mode_key",
]


class Mode(Protocol):  # minimal protocol for engine integration later
	config: ModeConfig

	def words(self):  # generator or iterable
		...

	def is_complete(self) -> bool:
		...


class _TimedMode:
	def __init__(self, cfg: ModeConfig, rng: Random):
		self.config = cfg
		self._rng = rng
		self._words_gen = timed_word_stream(
			rng,
			punctuation_prob=cfg.punctuation_prob,
			numbers=cfg.numbers,
			base_words=load_words(cfg.wordlist_path),
		)

	def words(self):  # infinite generator pass-through
		return self._words_gen

	def is_complete(self) -> bool:
		return False  # engine decides based on time


class _WordCountMode:
	def __init__(self, cfg: ModeConfig, rng: Random):
		self.config = cfg
		self._rng = rng
		assert cfg.word_count is not None
		self._words_list = finite_word_stream(
			cfg.word_count,
			rng,
			punctuation_prob=cfg.punctuation_prob,
			numbers=cfg.numbers,
			base_words=load_words(cfg.wordlist_path),
		)
		self._index = 0

	def words(self):
		# yield remaining words
		while self._index < len(self._words_list):
			yield self._words_list[self._index]
			self._index += 1

	def is_complete(self) -> bool:
		return self._index >= len(self._words_list)


def build_timed_mode(seconds: int, **kwargs) -> Mode:
	cfg = ModeConfig(timed_seconds=seconds, **kwargs)
	validate_mode_config(cfg)
	return _TimedMode(cfg, Random())


def build_word_count_mode(count: int, **kwargs) -> Mode:
	cfg = ModeConfig(word_count=count, **kwargs)
	validate_mode_config(cfg)
	return _WordCountMode(cfg, Random())


def mode_key(cfg: ModeConfig) -> str:
	return make_mode_key(cfg)
