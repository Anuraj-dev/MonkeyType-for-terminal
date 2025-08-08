# Typing Game (Monkeytype‑inspired)

A lightweight terminal typing practice tool supporting timed and word‑count modes, optional punctuation & numbers, persistent highscores, and a fallback plain mode when `curses` is unavailable.

## Features

- Timed mode (e.g. 60s) and word‑count mode
- Optional punctuation injection & number substitution
- Live stats (prototype real‑time loop) or plain line input fallback
- Metrics: Raw (gross) WPM, Net WPM, Accuracy, Errors, Chars
- Highscore persistence per mode (JSON; top N configurable)
- Previous best comparison & new highscore indication
- CLI with flags (`--timed`, `--words`, `--punct`, `--numbers`, `--list`, `--show-highscores`)
- Interactive menu when no CLI mode args provided
- Cross‑platform (Windows uses optional `windows-curses` package)

## Install

Create and activate a virtual environment (recommended) then install dev deps if desired:

```bash
pip install -r requirements.txt
```

On Windows for full-screen UI:

```bash
pip install windows-curses
```

If you skip installing curses support the game runs in plain (line) mode.

## Usage

Run via module or root CLI script:

```bash
python main.py --timed 60
python main.py --words 50 --punct 0.1 --numbers
python main.py --show-highscores
```

If you provide no mode switches you will see the interactive menu.

### CLI Flags

| Flag                | Description                                       |
| ------------------- | ------------------------------------------------- |
| `--timed SECONDS`   | Timed session (mutually exclusive with `--words`) |
| `--words COUNT`     | Fixed number of words                             |
| `--punct FLOAT`     | Punctuation probability 0..1 (e.g. 0.1)           |
| `--numbers`         | Enable occasional number replacement              |
| `--list PATH`       | Custom word list file path                        |
| `--show-highscores` | Display highscores and exit                       |

### Highscores

Stored in `highscores.json` (local project) or a home fallback file. Each mode key encodes settings (e.g. `timed-60-p0-n1`). Only the top _N_ (default 25) entries per mode are retained, ordered by:

1. Net WPM (descending)
2. Accuracy (descending)
3. Timestamp (ascending, older first)

### Metrics Formulas

Let `chars_typed = C`, `correct_chars = G`, `errors = E`, `elapsed_minutes = M`.

Raw (Gross) WPM = `(C / 5) / M`

Net WPM = `((G - E) / 5) / M` (floored at zero internally)

Accuracy = `G / C` (0 if `C == 0`).

These are standard simplified typing metrics (5 chars = 1 word heuristic).

## Development

Run tests:

```bash
pytest -q
```

Type checking:

```bash
mypy .
```

Lint:

```bash
ruff check .
```

Set `TYPING_GAME_DEBUG=1` to enable debug logs during development.

## Roadmap & Plan

Detailed milestone tracking lives in `plan.txt` (Sections 1–24). Performance refinements and advanced features (consistency metric, adaptive difficulty, themes, etc.) are queued for future iterations.

## Windows Notes

Install `windows-curses` for full-screen real‑time mode. Without it, the application falls back automatically to a plain line‑based interface.

## License

MIT (add a LICENSE file if distributing).

## Future Enhancements (Planned)

- Allocation reduction in real-time loop
- Robust terminal restore via try/finally
- Consistency metric & historical charts
- Theming & quote/custom text modes

See `plan.txt` for the complete list.
