# Typing Game (Enhanced with Smart Features)

A powerful terminal typing practice tool with intelligent error detection, smart highscore management, and multiple difficulty levels. Supports both timed and word-count modes with real-time feedback and comprehensive statistics.

**🔗 Repository:** https://github.com/Anuraj-dev/MonkeyType-for-terminal

## ✨ Key Features

### 🎯 **Smart Typing Analysis**

- **Accurate Error Detection**: Counts omissions, mismatches, and extra characters
- **Real-time Feedback**: Live WPM, accuracy, and error tracking
- **Word-by-word Analysis**: Detailed breakdown of typing mistakes

### 🏆 **Intelligent Highscore System**

- **Smart Storage**: Only saves highscores when you actually improve
- **Performance Tracking**: Shows improvement deltas (+X.XX WPM or -X.XX WPM)
- **First-time Friendly**: Always saves your first attempt for comparison

### 📚 **Multiple Difficulty Levels**

- **Easy**: Short common words (the, and, for...)
- **Medium**: Moderate length words (about, before, which...)
- **Hard**: Complex words (sophisticated, implementation...)
- **Programming**: Technical terms (polymorphism, encapsulation...)
- **Book Content**: Practice with real literature (Alice in Wonderland included)
- **Custom Books**: Add your own 10-page books for practice

### ⚙️ **Flexible Game Modes**

- **Timed Mode**: Practice for a set duration (e.g., 60 seconds)
- **Word Count Mode**: Type a specific number of words
- **Mixed Content**: Optional punctuation and numbers
- **Progressive Difficulty**: Easy menu-driven difficulty selection

### 🖥️ **Cross-Platform Support**

- **Real-time Mode**: Full-screen curses interface with live updates
- **Fallback Mode**: Plain text interface when curses unavailable
- **Windows Support**: Automatic `windows-curses` integration

## 🚀 Quick Start

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git
cd MonkeyType-for-terminal
```

2. **Install the package in editable mode:**

```bash
pip install -e .
```

3. **For Windows users (full-screen mode):**

```bash
pip install windows-curses
```

4. **For development:**

```bash
pip install -r requirements.txt
```

### Running the Game

**Interactive Mode (Recommended):**

```bash
python main.py          # Main game with menu
python demo.py          # Enhanced demo with difficulty selection
```

**Direct Command Line:**

```bash
python main.py --timed 60 --punct 0.1    # 60-second timed mode with punctuation
python main.py --words 50 --numbers      # 50-word mode with numbers
python main.py --show-highscores         # View your progress
```

### Adding Your Own Books

1. **Create a text file** with your book content:

```bash
# Paste your 10-page book into:
data/wordlists/my_book.txt
```

2. **Convert to typing format:**

```bash
python convert_book.py
```

3. **Play with your book** using the difficulty menu option!

## 🐧 **Linux Quick Start**

**One-command setup for Linux users:**

```bash
# Ubuntu/Debian - Complete setup
sudo apt update && sudo apt install python3 python3-pip python3-venv git -y
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git && cd MonkeyType-for-terminal
python3 -m venv venv && source venv/bin/activate
pip install -e . && python3 demo.py
```

**Fedora/CentOS:**

```bash
sudo dnf install python3 python3-pip git -y
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git && cd MonkeyType-for-terminal
python3 -m venv venv && source venv/bin/activate
pip install -e . && python3 demo.py
```

**Arch Linux:**

```bash
sudo pacman -S python python-pip git
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git && cd MonkeyType-for-terminal
python3 -m venv venv && source venv/bin/activate
pip install -e . && python3 demo.py
```

**Daily Usage (after setup):**

```bash
cd MonkeyType-for-terminal
source venv/bin/activate  # Activate environment
python3 demo.py          # Start typing practice!
```

## 🎮 How to Play

### Basic Controls

- **Type each word** exactly as shown
- **Press SPACE or ENTER** to submit each word
- **Use BACKSPACE** to correct mistakes
- **Type '/quit'** to exit early (plain mode)
- **Press 'q'** to quit (curses mode)

### Game Flow

1. **Choose your mode**: Timed (60s) or Word Count (25 words)
2. **Select difficulty**: From easy words to complex programming terms
3. **Start typing**: Words appear one by one with real-time feedback
4. **View results**: Get detailed statistics and improvement tracking
5. **Change settings**: Press 'M' after a session to modify difficulty/mode

### Difficulty Selection Menu

When you choose "Change difficulty" you'll see:

```
🎯 Choose Difficulty Level:
1. Easy (short common words)
2. Medium (moderate length words)
3. Hard (complex words)
4. Programming (technical terms)
5. Alice in Wonderland (book content)
6. Default (mixed)
```

## 📊 Enhanced Statistics

### Intelligent Error Detection

- **Character Mismatches**: Wrong letters typed
- **Omissions**: Characters you forgot to type
- **Extra Characters**: Typing beyond the word length
- **Real Accuracy**: Includes all types of errors for honest metrics

### Smart Highscore Management

- **Improvement Only**: Highscores saved only when you beat your previous best
- **Progress Tracking**: Clear indicators showing improvement or decline
- **Performance Delta**: See exactly how much you improved (+2.5 WPM!)
- **First Attempt**: Always saves your initial score for future comparison

### Comprehensive Metrics

- **Raw WPM**: Total typing speed including errors
- **Net WPM**: Speed adjusted for accuracy (penalizes mistakes)
- **Accuracy**: Percentage of correctly typed characters
- **Consistency**: Variation in your typing rhythm
- **Error Count**: Total mistakes made during session

## ⚙️ Advanced Configuration

### CLI Flags

| Flag                | Description                                       |
| ------------------- | ------------------------------------------------- |
| `--timed SECONDS`   | Timed session (mutually exclusive with `--words`) |
| `--words COUNT`     | Fixed number of words                             |
| `--punct FLOAT`     | Punctuation probability 0..1 (e.g. 0.1)           |
| `--numbers`         | Enable occasional number replacement              |
| `--list PATH`       | Custom word list file path                        |
| `--show-highscores` | Display highscores and exit                       |

### Available Word Lists

The game includes several pre-made difficulty levels:

- **`easy.txt`**: 36 short common words
- **`medium.txt`**: 36 moderate length words
- **`hard_words.txt`**: 54 complex vocabulary words
- **`programming.txt`**: 53 technical programming terms
- **`alice_words.txt`**: 283 words from Alice in Wonderland
- **`english_1k.txt`**: Original mixed word list

### Creating Custom Difficulty Levels

1. **Add words to a file** (one per line):

```
sophisticated
implementation
extraordinary
# ... more words
```

2. **Save in** `data/wordlists/my_difficulty.txt`

3. **Update the difficulty chooser** in `engine.py` to include your new list

### Book Content Support

The game can convert any book or text into typing practice:

1. **Paste book content** into `data/wordlists/book_name.txt`
2. **Run converter**: `python convert_book.py`
3. **Generated file**: `book_name_words.txt` (one word per line)
4. **Add to difficulty menu** for easy access

## 📈 Highscore System

### Smart Storage Logic

- **Improvement-Based**: Highscores only saved when you beat your previous best
- **No File Spam**: Prevents cluttering with poor performances
- **First-Time Saves**: Always records your initial attempt for comparison
- **Local Storage**: `highscores.json` in project directory (or home fallback)

### Highscore Ranking

Each mode creates a separate leaderboard (e.g., `timed-60-p0-n1`):

1. **Net WPM** (descending - primary ranking)
2. **Accuracy** (descending - tiebreaker)
3. **Timestamp** (ascending - older first for final ties)

### Progress Tracking

The enhanced end screen shows:

```
Previous Best Net WPM: 45.20
🎉 IMPROVEMENT: +3.15 WPM!
*** NEW HIGHSCORE SAVED! ***
```

Or for non-improvements:

```
📉 Below best by 2.10 WPM
💡 No highscore saved (no improvement)
```

## 🧮 Metrics Formulas

### Standard WPM Calculations

- **Raw (Gross) WPM** = `(total_chars_typed / 5) / minutes_elapsed`
- **Net WPM** = `((correct_chars - errors) / 5) / minutes_elapsed` (≥ 0)
- **Accuracy** = `correct_chars / total_chars_typed` (0 if no chars typed)

### Enhanced Error Detection

- **Character Errors**: Each wrong character counts as 1 error
- **Omission Errors**: Each missing character counts as 1 error
- **Total Characters**: Includes typed chars + omitted chars for accurate metrics
- **Consistency**: Standard deviation of per-word typing times

## 🔧 Development

### Running Tests

```bash
pytest tests/ -v     # Verbose test output
pytest tests/ -q     # Quick test run
```

### Project Structure

```
MonkeyType-for-terminal/
├── typing_game/           # Main package
│   ├── engine.py         # Game logic & sessions
│   ├── ui.py            # Terminal interface
│   ├── metrics.py       # WPM & accuracy calculations
│   ├── storage.py       # Highscore persistence
│   ├── config.py        # Configuration management
│   ├── modes.py         # Game mode factories
│   └── words.py         # Word loading & generation
├── data/wordlists/       # Difficulty levels & books
├── tests/               # Comprehensive test suite
├── main.py             # CLI entry point
├── demo.py             # Enhanced interactive demo
└── convert_book.py     # Book-to-wordlist converter
```

### Key Improvements Made

1. **Enhanced Error Detection**: Omissions now counted as errors
2. **Smart Highscore Logic**: Only saves actual improvements
3. **Difficulty Selection**: User-friendly menu replaces file paths
4. **Better End Screen**: Shows improvement deltas and feedback
5. **Enter Key Support**: Both Space and Enter work for word submission
6. **Book Content Support**: Easy conversion of any text to typing practice

### Debug Mode

Set environment variable for detailed logging:

```bash
set TYPING_GAME_DEBUG=1    # Windows
export TYPING_GAME_DEBUG=1 # Linux/Mac
python main.py
```

## 🖥️ Platform Support

### Windows

- **Install**: `pip install windows-curses` for full-screen mode
- **Fallback**: Automatic plain-text mode if curses unavailable
- **Tested**: Windows 10/11 with PowerShell and Command Prompt

### Linux/Mac

- **Built-in**: Native curses support included
- **Terminal**: Works in any terminal emulator
- **SSH**: Remote typing practice supported

#### 🐧 **Linux Installation & Setup**

**Prerequisites:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip git
# or for older versions: sudo yum install python3 python3-pip git

# Arch Linux
sudo pacman -S python python-pip git
```

**Step-by-Step Installation:**

```bash
# 1. Clone the repository
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git
cd MonkeyType-for-terminal

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Activate virtual environment

# 3. Install the typing game
pip install -e .

# 4. Install development dependencies (optional)
pip install -r requirements.txt
```

**Running on Linux:**

```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Run the game - these all work on Linux
python3 main.py                    # Interactive menu
python3 demo.py                    # Enhanced demo
python3 main.py --timed 60         # Direct timed mode
python3 main.py --show-highscores  # View progress

# Make executable (optional)
chmod +x main.py
./main.py                         # Direct execution
```

**Terminal Compatibility:**

- ✅ **GNOME Terminal** - Full curses support
- ✅ **Konsole** (KDE) - Full curses support
- ✅ **xterm** - Full curses support
- ✅ **Alacritty** - Full curses support
- ✅ **Terminator** - Full curses support
- ✅ **tmux/screen** - Full curses support
- ✅ **SSH sessions** - Works over SSH connections
- ⚠️ **Basic terminals** - Falls back to plain mode

**Linux-Specific Features:**

- **No additional packages needed** - curses built into Python
- **Better performance** - Native terminal integration
- **SSH support** - Practice typing over remote connections
- **Multiple displays** - Works with any X11/Wayland setup
- **Package managers** - Can be packaged for distributions

**Troubleshooting Linux Issues:**

```bash
# If you get "command not found: python"
python3 main.py  # Use python3 instead

# If curses doesn't work in your terminal
export TERM=xterm-256color  # Set proper terminal type
python3 main.py             # Try again

# If you get permission errors
chmod +x main.py demo.py convert_book.py  # Make scripts executable

# If virtual environment activation fails
python3 -m venv --clear venv  # Recreate virtual environment
source venv/bin/activate
```

**Advanced Linux Usage:**

```bash
# Run in background and resume later
python3 main.py &           # Background process
fg                          # Bring back to foreground

# Use with different Python versions
python3.9 main.py          # Specific Python version
python3.11 main.py         # Another version

# Create desktop shortcut (Ubuntu/GNOME)
cat > ~/Desktop/typing-game.desktop << EOF
[Desktop Entry]
Name=Typing Game
Exec=/path/to/MonkeyType-for-terminal/venv/bin/python /path/to/MonkeyType-for-terminal/main.py
Icon=utilities-terminal
Type=Application
Terminal=true
EOF
chmod +x ~/Desktop/typing-game.desktop

# Add to PATH for system-wide access
echo 'export PATH="$PATH:/path/to/MonkeyType-for-terminal"' >> ~/.bashrc
source ~/.bashrc
typing-game  # Now accessible from anywhere
```

**🚀 Why Linux is Perfect for This Typing Game:**

- ✅ **Native Performance**: No extra dependencies needed
- ✅ **Terminal Excellence**: Superior terminal capabilities
- ✅ **SSH Practice**: Practice typing over remote connections
- ✅ **Lightweight**: Minimal resource usage
- ✅ **Customizable**: Easy to modify and extend
- ✅ **Server Usage**: Run on headless servers for remote practice
- ✅ **Package Friendly**: Can be packaged for distribution repos

**Distribution Packaging (For Maintainers):**

```bash
# Debian/Ubuntu package structure
typing-game/
├── debian/
│   ├── control          # Package dependencies
│   ├── rules           # Build rules
│   └── typing-game.install
├── DEBIAN/
│   └── control         # Package metadata
└── usr/
    ├── bin/
    │   └── typing-game  # Main executable
    └── share/
        └── typing-game/ # Game data files
```

### Features by Mode

| Feature                | Curses Mode | Plain Mode |
| ---------------------- | ----------- | ---------- |
| Real-time WPM          | ✅          | ❌         |
| Live word highlighting | ✅          | ❌         |
| Progress bar           | ✅          | ❌         |
| Backspace editing      | ✅          | ✅         |
| All statistics         | ✅          | ✅         |
| Difficulty selection   | ✅          | ✅         |
| Highscore tracking     | ✅          | ✅         |

## 🎯 Example Sessions

### Easy Difficulty (Beginner)

```
[1] the: the
[2] and: and
[3] for: for
...
Net WPM: 25.4  Accuracy: 98.5%  🆕 First attempt!
```

### Programming Difficulty (Advanced)

```
[1] polymorphism: polymorphism
[2] encapsulation: encapulation  ← omission error
[3] inheritance: inheritance
...
Net WPM: 42.1  Accuracy: 91.2%  🎉 IMPROVEMENT: +3.8 WPM!
```

### Book Content (Alice in Wonderland)

```
[1] Alice: Alice
[2] was: was
[3] beginning: begining  ← spelling error
...
Net WPM: 38.7  Accuracy: 94.1%  📉 Below best by 1.2 WPM
```

## 🚀 Future Enhancements

### Planned Features

- **Adaptive Difficulty**: Automatic adjustment based on performance
- **Historical Charts**: Visual progress tracking over time
- **Custom Themes**: Color schemes and visual customization
- **Multiplayer Mode**: Race against friends online
- **Advanced Metrics**: Keystroke dynamics and rhythm analysis
- **Language Support**: Multiple language word lists
- **Quote Mode**: Practice with famous quotes and literature

### Contribution Ideas

- Add more programming language vocabularies
- Create themed word lists (medical, legal, academic)
- Implement word frequency analysis
- Add typing sound effects
- Create mobile-friendly web version

## 📄 License

MIT License - feel free to use, modify, and distribute!

## 🙏 Acknowledgments

- Inspired by Monkeytype and other typing practice tools
- Built with Python's `curses` library for terminal interfaces
- Alice in Wonderland text from Project Gutenberg
- Enhanced with intelligent error detection and progress tracking

---

**Ready to improve your typing?**

```bash
git clone https://github.com/Anuraj-dev/MonkeyType-for-terminal.git
cd MonkeyType-for-terminal
pip install -e .
python demo.py
```

Happy typing! ⌨️✨
