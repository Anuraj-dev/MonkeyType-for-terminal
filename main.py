"""Project root CLI entry point.

Allows running with:  python -m typing_game  (package) or  python main.py (root).

Loads last saved configuration (or defaults) and starts interactive loop.
"""

from typing_game.config import load_last_config, save_last_config, ModeConfig
from typing_game.engine import interactive_loop


def main():  # pragma: no cover - user interactive
	cfg: ModeConfig = load_last_config()
	try:
		interactive_loop(cfg)
	finally:
		# persist last used config (unchanged for now) for future runs
		save_last_config(cfg)


if __name__ == "__main__":  # manual launch support
	main()
