"""CLI entrypoint.

Implements Section 13 of the plan:
 - argparse with --timed / --words / --list / --punct / --numbers / --show-highscores
 - Interactive menu if no mode args supplied
 - Dispatch to engine

Later milestones will add curses real-time UI; this CLI presently runs the line-based prototype engine.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .config import default_config, merge_cli_args, ModeConfig
from .engine import interactive_loop, run_session, end_screen
from .storage import get_top_highscores, load_highscores
from .metrics import make_mode_key


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="typing-game", description="Terminal typing game (prototype)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--timed", type=int, help="Timed mode: seconds")
    mode.add_argument("--words", type=int, help="Word-count mode: number of words")
    p.add_argument("--list", dest="list", help="Custom word list file path")
    p.add_argument("--punct", type=float, help="Punctuation probability 0..1")
    p.add_argument("--numbers", action="store_true", help="Enable occasional number substitution")
    p.add_argument("--show-highscores", action="store_true", help="Show highscores then exit")
    return p


def print_highscores(limit: int = 10):  # pragma: no cover - output
    store = load_highscores()
    if not store:
        print("No highscores yet.")
        return
    print("=== Highscores ===")
    for mode_key, entries in store.items():
        print(f"[{mode_key}]")
        ordered = get_top_highscores(mode_key, limit=limit)
        for i, e in enumerate(ordered, 1):
            print(f" {i:2d}. {e.wpm:6.2f} WPM (net) acc {e.accuracy*100:5.1f}% raw {e.raw_wpm:6.2f} errors {e.errors} {e.timestamp}")
    print("==================")


def interactive_menu():  # pragma: no cover - user interaction
    cfg = default_config()
    while True:
        print("\nTyping Game Menu")
        print("1) Timed 60s")
        print("2) Words 50")
        print("3) Show highscores")
        print("Q) Quit")
        choice = input("> ").strip().lower()
        if choice == "1":
            cfg = ModeConfig(timed_seconds=60, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path)
            res = run_session(cfg)
            end_screen(res)
        elif choice == "2":
            cfg = ModeConfig(word_count=50, punctuation_prob=cfg.punctuation_prob, numbers=cfg.numbers, wordlist_path=cfg.wordlist_path)
            res = run_session(cfg)
            end_screen(res)
        elif choice == "3":
            print_highscores()
        elif choice.startswith("q"):
            break
        else:
            print("Invalid option.")


def main(argv: Optional[list[str]] = None):  # pragma: no cover - integration
    parser = build_parser()
    args = parser.parse_args(argv)
    cfg = default_config()

    if args.show_highscores:
        print_highscores()
        return

    # If neither timed nor words provided → interactive menu
    if args.timed is None and args.words is None:
        interactive_menu()
        return

    cfg = merge_cli_args(cfg, args)
    res = run_session(cfg)
    end_screen(res)


if __name__ == "__main__":  # manual launch support
    main()
