"""Linux Command Library TUI Application"""

from .app import CommandApp, main

__all__ = ["CommandApp", "main"]

from typing import Optional  # at top

def __init__(self, commands):
    super(CommandApp, self).__init__()
    ...
    self._observer = None  # type: ignore # type: Optional[object]
