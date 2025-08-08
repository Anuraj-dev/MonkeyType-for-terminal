"""Typing Game package bootstrap.

Currently provides a minimal entrypoint stub. Real engine & UI will come in later milestones.
"""

__all__ = [
    "run",
]

def run():
    from .main import main
    main()
