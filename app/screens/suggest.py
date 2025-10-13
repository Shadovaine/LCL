#=================================================
# Suggest Command Screen
#=================================================

from __future__ import annotations

#-------------------Standard Library-------------------
from typing import Any, Dict

#-------------------Textual UI-------------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static
from textual.containers import Horizontal

#-------------------Optional Library-------------------
try:
    from textual.widgets import TextArea
    HAVE_TEXTAREA = True
except Exception:
    HAVE_TEXTAREA = False
    TextArea = None # type: ignore

#-------------------Local Library-------------------
from ..suggestions import _save_suggestion

#-------------------Suggest Command Screen-------------------
class SuggestCommandScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen { width: 90%; height: 90%; align: center middle; }
    #title    { width: 100%; content-align: center middle; margin-bottom: 1; }
    #msg      { color: yellow; padding: 0 1; }
    #row      { layout: horizontal; height: auto; }
    #row > *  { width: 1fr; margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Suggest a Command", id="title")
        # simple structured fields
        with Horizontal(id="row"):
            self._name = Input(placeholder="Command name (e.g., rsync)", id="sug_name")
            self._category = Input(placeholder="Category (free text OK)", id="sug_cat")
        self._usage = Input(placeholder="Usage / Syntax (e.g., rsync -av src/ dst/)", id="sug_usage")
        # multi-line description uses TextArea if available
        if HAVE_TEXTAREA:
            self._desc = TextArea(id="sug_desc")
            self._desc.text = "Describe what this command does and why it’s useful..."
        else:
            self._desc = Input(placeholder="Short description…", id="sug_desc")  # type: ignore
        yield self._name
        yield self._category
        yield self._usage
        yield self._desc
        with Horizontal():
            yield Button("Submit", id="sug_submit")
            yield Button("Cancel", id="sug_cancel")
        yield Static("", id="msg")

    def _msg(self, text: str, ok: bool = False):
        self.query_one("#msg", Static).update(("[green]✓ " if ok else "[yellow]") + text)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        if bid == "sug_cancel":
            self.dismiss(None)
            return
        if bid == "sug_submit":
            name = self._name.value.strip()
            desc = (getattr(self._desc, "text", None) or getattr(self._desc, "value", "")).strip()
            if not name or not desc:
                self._msg("Please provide at least a name and a description.")
                return
            payload = {
                "name": name,
                "category": self._category.value.strip() or "Unsorted",
                "description": desc,
                "usage": self._usage.value.strip(),
            }
            try:
                path = _save_suggestion(payload)
                self._msg(f"Thanks! Saved to {path}", ok=True)
                self.dismiss(None)
            except Exception as e:
                self._msg(f"Failed to save: {e}")
