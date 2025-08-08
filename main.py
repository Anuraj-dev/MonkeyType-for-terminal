"""Root CLI entry point (Section 13).

Features:
 - argparse interface (--timed / --words are mutually exclusive)
 - optional modifiers: --punct, --numbers, --list WORDLIST
 - --show-highscores to list stored highscores and exit
 - falls back to an interactive menu when no action arguments supplied
 - persists last used configuration

Usage examples:
  python main.py --timed 60 --punct 0.1 --numbers
  python main.py --words 50
  python main.py --show-highscores
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from typing_game.config import (
	load_last_config,
	save_last_config,
	merge_cli_args,
	ModeConfig,
)
from typing_game.engine import interactive_loop
from typing_game.storage import get_top_highscores
from typing_game.metrics import make_mode_key


# ----------------------------- Highscore Helpers -----------------------------
def print_highscores(limit: int = 25):  # pragma: no cover - output helper
	print("=== Highscores (top) ===")
	entries = get_top_highscores(limit=limit)
	if not entries:
		print("(none recorded yet)")
		return
	for i, e in enumerate(entries, 1):
		print(f"{i:2d}. {e.mode_key:20s} net={e.net_wpm:.2f} raw={e.raw_wpm:.2f} acc={e.accuracy*100:.1f}% errors={e.errors}")


# ------------------------------- Interactive Menu ----------------------------
def interactive_menu(base_cfg: ModeConfig) -> ModeConfig:  # pragma: no cover - interactive
	while True:
		print("\n=== Typing Game Menu ===")
		print("1) Timed session")
		print("2) Word count session")
		print("3) Show highscores")
		print("4) Toggle punctuation (currently: %.2f)" % base_cfg.punctuation_prob)
		print(f"5) Toggle numbers (currently: {'ON' if base_cfg.numbers else 'OFF'})")
		print("6) Change word list (currently: %s)" % (base_cfg.wordlist_path or "<default/none>"))
		print("Q) Quit")
		choice = input("Select: ").strip().lower()
		if choice == "1":
			val = input("Seconds (e.g. 60): ").strip()
			try:
				secs = int(val)
				return ModeConfig(timed_seconds=secs, word_count=None, punctuation_prob=base_cfg.punctuation_prob, numbers=base_cfg.numbers, wordlist_path=base_cfg.wordlist_path, top_n_highscores=base_cfg.top_n_highscores)
			except ValueError:
				print("Invalid integer.")
		elif choice == "2":
			val = input("Word count (e.g. 50): ").strip()
			try:
				wc = int(val)
				return ModeConfig(timed_seconds=None, word_count=wc, punctuation_prob=base_cfg.punctuation_prob, numbers=base_cfg.numbers, wordlist_path=base_cfg.wordlist_path, top_n_highscores=base_cfg.top_n_highscores)
			except ValueError:
				print("Invalid integer.")
		elif choice == "3":
			print_highscores()
		elif choice == "4":
			val = input("New punctuation probability [0-1]: ").strip()
			try:
				p = float(val)
				if 0 <= p <= 1:
					base_cfg.punctuation_prob = p
				else:
					print("Out of range")
			except ValueError:
				print("Invalid float")
		elif choice == "5":
			base_cfg.numbers = not base_cfg.numbers
		elif choice == "6":
			path = input("Path to word list file: ").strip()
			if path:
				p = Path(path)
				if p.exists():
					base_cfg.wordlist_path = p
				else:
					print("File does not exist")
		elif choice in {"q", "quit", "exit"}:
			raise SystemExit(0)
		else:
			print("Unknown option")


# --------------------------------- Argparse ---------------------------------
def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Typing game CLI")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("--timed", type=int, help="Run a timed session (seconds)")
	group.add_argument("--words", type=int, help="Run a fixed word-count session")
	parser.add_argument("--punct", type=float, help="Punctuation probability [0-1]")
	parser.add_argument("--numbers", action="store_true", help="Enable number replacements")
	parser.add_argument("--list", metavar="WORDLIST", help="Path to custom word list file")
	parser.add_argument("--show-highscores", action="store_true", help="Display highscores and exit")
	return parser


def args_provided(ns: argparse.Namespace) -> bool:
	return any(
		getattr(ns, name) is not None
		for name in ["timed", "words", "punct", "list"]
	) or ns.numbers or ns.show_highscores


def run_from_args(ns: argparse.Namespace, last_cfg: ModeConfig):  # pragma: no cover - orchestration
	if ns.show_highscores:
		print_highscores()
		return
	# If no specific args (like --timed) passed, go interactive menu
	if not args_provided(ns):
		cfg = interactive_menu(last_cfg)
	else:
		cfg = merge_cli_args(last_cfg, ns)
	interactive_loop(cfg)
	# persist last used config (post any interactive menu tweaks)
	save_last_config(cfg)


def main():  # pragma: no cover - user interactive
	last_cfg = load_last_config()
	parser = build_parser()
	ns = parser.parse_args()
	run_from_args(ns, last_cfg)


if __name__ == "__main__":  # manual launch support
	main()
