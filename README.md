<h1 align="center">MonkeyType for terminal</h1>

<p align="center">
  A Monkeytype-style typing practice game for the terminal, written in Python.<br />
  Type against the clock or a word count, then see your net WPM and accuracy.
</p>

<p align="center">
  <a href="#installation">Install</a>
  ·
  <a href="#running-it">Run it</a>
  ·
  <a href="#controls">Controls</a>
</p>

The game shows a stream of words. You type each word and submit it. Mismatched letters, missing letters and extra letters all count as errors. When a run ends, you see raw WPM, net WPM, accuracy and consistency, and the run is saved as a highscore if it beats your best for that mode.

It runs as `main.py` from the repository folder. Where curses is available, you get a full-screen view with a live header. Everywhere else, it falls back to plain line prompts. Linux and macOS need only Python 3.11 or newer. Windows also needs `windows-curses`. There is no account, and the code makes no network calls.

## What you get

- **Live full-screen typing view.** The header shows elapsed time, net WPM, accuracy and errors. The current word gets a caret, correct letters turn green, and wrong letters turn red.
- **Errors counted per character.** A mismatch, a missing letter and an extra letter each count as one error. Net WPM subtracts errors from correct characters, so a fast run with typos scores lower than a clean run at the same speed.
- **Highscores only on improvement.** Each mode, such as `timed-60-p0-n0`, keeps its own top 25 runs. A run is saved when it beats your best net WPM, or when it is the first run in that mode.
- **Punctuation and numbers.** `--punct 0.1` adds one of `, . ? ! ;` to about 10 percent of words. `--numbers` replaces about 15 percent of words with a single digit.
- **Sound on each submitted word.** A correct word plays `sounds/correct.wav`. Any other word plays `sounds/wrong.wav`. Windows uses the built-in `winsound` module. On Linux and macOS, install `simpleaudio` to hear the sounds. Without it, the game stays silent.
- **Remembers your last settings.** Mode, punctuation, numbers and word list are saved when you quit. The menu starts from them next time.
- **Word lists for each level.** Easy, medium, hard, programming and Alice in Wonderland are in the difficulty menu. Any text file works as your own list with `--list`.

## Installation

Clone the repository and run everything from inside it. The difficulty menu finds its word lists relative to the current folder.

```sh
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git
cd MonkeyType-for-terminal
```

| Platform | You need |
| --- | --- |
| **Windows** | Python 3.11 or newer, plus `windows-curses` |
| **Linux** | Python 3.11 or newer. The curses module comes with Python. |
| **macOS** | Python 3.11 or newer. The curses module comes with Python. |

The code uses `datetime.UTC`, which needs Python 3.11 or newer. Check your version with `python3 --version`.

### Windows

Install the curses backend. Without it, the game runs in plain line mode.

```sh
pip install windows-curses
```

### Linux and macOS

The core game has no packages to install. For sound, install `simpleaudio`.

```sh
pip install simpleaudio
```

If pip refuses with an externally-managed-environment error, create a virtual environment first with `python3 -m venv venv` and `source venv/bin/activate`.

## Running it

Run these from the repository root.

```sh
python3 main.py                                   # opens the menu
python3 main.py --timed 60                        # 60 seconds, straight into a session
python3 main.py --words 50 --punct 0.1 --numbers  # 50 words with punctuation and numbers
python3 main.py --list data/wordlists/alice_words.txt --timed 60
python3 main.py --show-highscores                 # print stored highscores and exit
python3 demo.py                                   # 25 words, difficulty menu first
```

On Windows, use `python` in place of `python3`.

Flags:

| Flag | Meaning |
| --- | --- |
| `--timed SECONDS` | Timed session. Cannot be combined with `--words`. |
| `--words COUNT` | Word-count session. |
| `--punct FLOAT` | Chance from 0 to 1 that a word gets punctuation. |
| `--numbers` | Replace some words with a digit. |
| `--list PATH` | Use this text file as the word list. |
| `--show-highscores` | Print the top 25 runs for each mode and exit. |

## Controls

### Menu

- `1` opens the timed options. `1`, `2` and `3` pick 15, 30 or 60 seconds. `4` asks for a custom length. `S` starts and `B` goes back.
- `2` starts a word-count session. `3` shows highscores. `4` sets punctuation. `5` toggles numbers. `6` opens the difficulty menu.
- `S` starts a timed session with the length you picked. On the first run, the length is 15 seconds.
- `Q` quits.

### Typing view

- Type the word, then press Space to submit it. Enter does nothing in this view.
- Submitting before you finish the word counts the missing letters as errors. Pressing Space with nothing typed counts the whole word as errors.
- Backspace removes a letter from the screen, but the error it was fixing still counts.
- `q` quits when the current word is empty.
- A timed session ends when the clock runs out. A word-count session ends after the last word.

### Plain mode

Plain mode runs when curses is missing or the curses view fails. Type the word and press Enter. `/quit` ends the run early, and the stats print at the end.

### End screen

`R` or Enter restarts with the same settings. `M` opens the mode menu, where you can change the length, punctuation, numbers or difficulty. `Q` quits.

## Scores and metrics

```
raw WPM  = (characters typed / 5) / minutes
net WPM  = max(0, correct characters - errors) / 5 / minutes
accuracy = correct characters / characters typed
```

Each submitted word counts its trailing space as a correct character. Consistency is 1 minus the coefficient of variation of your per-word times, clamped from 0 to 1. It needs at least two timed words, and it stays hidden until then.

### Highscores

Highscores are grouped by mode key. The key encodes the length, punctuation and numbers, so `timed-60-p0-n0` and `timed-60-p0-n1` are separate leaderboards. Runs rank by net WPM, then accuracy, then older first. Each mode keeps its top 25.

## Files the game writes

- `highscores.json` in the folder you run from. If that folder is not writable, the game uses `~/.typing_game_highscores.json`.
- `~/.typing_game/config.json` with your last-used settings, written when you quit.

## Custom word lists

- Pass any text file with `--list path/to/file.txt`. Words split on whitespace, so punctuation stays attached to each word.
- To add a list to the difficulty menu, add an entry to `wordlist_map` in `_choose_difficulty` in `typing_game/engine.py`. `demo.py` keeps its own copy of that menu.
- The game loads a word list once per run. Changing difficulty later in the same run keeps the first list, so restart the program to switch.
- Choosing `6` in the difficulty menu keeps the current list.
- `convert_book.py` converts only `data/wordlists/alice_sample.txt` into `alice_words.txt`. It also rewrites `easy.txt` and `medium.txt` from lists in the script, so run it only if you want that.

The Alice word lists come from Project Gutenberg's *Alice's Adventures in Wonderland*.

## Troubleshooting

- **Plain line mode on Windows.** Install `windows-curses` with `pip install windows-curses`.
- **Curses view drops to plain mode.** Set `TYPING_GAME_DEBUG=1` to print the error to stderr. On Windows, use `set TYPING_GAME_DEBUG=1`.
- **"Word list not found" in the difficulty menu.** Run the game from the repository root. The menu resolves `data/wordlists/` from the current folder.

## Code map

| File | What it does |
| --- | --- |
| `main.py` | Entry point. Parses flags and runs the menu. |
| `demo.py` | 25-word practice with its own difficulty menu. |
| `typing_game/engine.py` | Curses and plain typing loops, the end screen and the difficulty menu. |
| `typing_game/metrics.py` | WPM, accuracy and consistency. |
| `typing_game/storage.py` | Reads and writes `highscores.json`. |
| `typing_game/config.py` | Settings, validation and the saved config file. |
| `typing_game/words.py` | Loads word lists and adds punctuation and numbers. |
| `typing_game/ui.py` | Curses setup, the highlighted word and the progress bar. |
| `typing_game/sound.py` | Plays the correct and wrong sounds. |
| `convert_book.py` | Alice converter. See Custom word lists. |

`plan.txt` is the original build plan. Code comments refer to its section numbers.

## License

MIT. See [LICENSE](LICENSE).
