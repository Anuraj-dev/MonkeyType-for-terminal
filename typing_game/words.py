"""Word loading & generation utilities (stub)."""

from pathlib import Path

_WORD_CACHE: list[str] | None = None

DEFAULT_WORDLIST_PATH = Path(__file__).resolve().parent.parent / "data" / "wordlists" / "english_1k.txt"

def load_words(path: Path | None = None) -> list[str]:
    global _WORD_CACHE
    if _WORD_CACHE is None:
        p = path or DEFAULT_WORDLIST_PATH
        try:
            content = p.read_text(encoding="utf-8").split()
        except FileNotFoundError:
            content = ["example", "words", "missing", "list"]
        _WORD_CACHE = content
    return _WORD_CACHE
