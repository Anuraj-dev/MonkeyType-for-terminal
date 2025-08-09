"""Lightweight cross-platform sound playback for game feedback.

Design goals:
- Non-blocking playback on word commit.
- No hard dependency on external packages; best-effort.
- Works out-of-the-box on Windows using winsound.
- On non-Windows, tries simpleaudio if installed; otherwise no-op.

Public API:
- play_correct()
- play_wrong()
"""

from __future__ import annotations

import sys
from pathlib import Path
from functools import lru_cache

_SOUNDS_DIR: Path | None = None


def _project_root() -> Path:
    # typing_game/sound.py -> typing_game -> project root
    return Path(__file__).resolve().parent.parent


def _sounds_dir() -> Path:
    global _SOUNDS_DIR
    if _SOUNDS_DIR is None:
        _SOUNDS_DIR = _project_root() / "sounds"
    return _SOUNDS_DIR


@lru_cache(maxsize=2)
def _sound_path(kind: str) -> Path | None:
    name = "correct.wav" if kind == "correct" else "wrong.wav"
    p = _sounds_dir() / name
    return p if p.exists() else None


def _play_async(path: Path) -> None:
    """Best-effort, non-blocking playback.

    Windows: winsound (stdlib) async.
    Others: try simpleaudio; else silently no-op.
    """
    try:
        if sys.platform.startswith("win"):  # Windows
            import winsound  # type: ignore
            flags = winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
            # winsound will return immediately with SND_ASYNC
            winsound.PlaySound(str(path), flags)
            return
        # Non-Windows: try simpleaudio
        try:
            import simpleaudio as sa  # type: ignore
        except Exception:
            return  # no-op if not available
        try:
            wave_obj = sa.WaveObject.from_wave_file(str(path))
            wave_obj.play()  # returns immediately
        except Exception:
            pass
    except Exception:
        # Always swallow errors; sound is optional
        pass


def play_correct() -> None:
    p = _sound_path("correct")
    if p is not None:
        _play_async(p)


def play_wrong() -> None:
    p = _sound_path("wrong")
    if p is not None:
        _play_async(p)
