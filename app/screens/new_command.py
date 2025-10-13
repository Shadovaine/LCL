#=================================================
# New Commnad Screen
#=================================================

from __future__ import annotations

#------------------Standard Library------------------
from typing import Any, Dict
from pathlib import Path as _Path
import yaml

#------------------Textual UI IMPORTS------------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static
from textual.containers import Horizontal

#------------------Optional IMPORTS------------------
try:
    from textual.widgets import TextArea
    HAVE_TEXTAREA = True
except Exception:
    HAVE_TEXTAREA = False
    TextArea = None # type: ignore

#------------------Local Library IMPORTS------------------
from ..validation import _validate_doc_minimal, _save_new_command

#------------------New Command Screen------------------
class NewCommandScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen { width: 90%; height: 90%; align: center middle; }
    #title    { width: 100%; content-align: center middle; margin-bottom: 1; }
    #editor   { height: 1fr; }
    #buttons  { height: auto; align: center middle; }
    #msg      { height: auto; color: yellow; padding: 0 1; }
    """
    def compose(self) -> ComposeResult:
        yield Static("New Command (Admin only)", id="title")
        # Big editor area
        if HAVE_TEXTAREA:
            self._editor = TextArea(id="editor")
        else:
            self._editor = Input(placeholder="Paste YAML here…", id="editor")  # type: ignore
        yield self._editor
        # Buttons
        with Horizontal(id="buttons"):
            yield Button("Validate", id="nc_validate")
            yield Button("Save", id="nc_save")
            yield Button("Cancel", id="nc_cancel")
        yield Static("", id="msg")

    def on_mount(self):
        # Load template if present
        tpl = self._load_template()
        self._set_text(tpl)

    def _load_template(self) -> str:
        # Try to read templates/command_templates.yml
        for root in (_Path.cwd(), _Path(__file__).resolve().parent):
            cand = root / "templates" / "command_templates.yml"
            if cand.is_file():
                try:
                    return cand.read_text(encoding="utf-8")
                except Exception:
                    pass
        # default minimal template
        return (
            "name: \n"
            "category: \n"
            "description: |\n"
            "  \n"
            "usage: \n"
            "# syntax: \n"
            "options: []  # list of {flag, description}\n"
            "examples: [] # list of strings\n"
            "related_commands: []\n"
        )

    def _get_text(self) -> str:
        return getattr(self._editor, "text", None) or getattr(self._editor, "value", "")

    def _set_text(self, text: str) -> None:
        if hasattr(self._editor, "text"):
            self._editor.text = text
        else:
            self._editor.value = text  # type: ignore

    def _set_msg(self, text: str, ok: bool = False):
        msg = self.query_one("#msg", Static)
        msg.update(("[green]✓ " if ok else "[yellow]") + text)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        if bid == "nc_cancel":
            self.dismiss(None)
            return

        raw = self._get_text()
        try:
            data = yaml.safe_load(raw)
        except Exception as e:
            self._set_msg(f"YAML parse error: {e}")
            return

        if not isinstance(data, dict):
            self._set_msg("Top-level must be a mapping (YAML dict).")
            return

        if bid == "nc_validate":
            issues = _validate_doc_minimal(data)
            if issues:
                self._set_msg("Validation issues:\n- " + "\n- ".join(issues))
            else:
                self._set_msg("Valid ✔", ok=True)

        elif bid == "nc_save":
            issues = _validate_doc_minimal(data)
            if issues:
                self._set_msg("Fix before save:\n- " + "\n- ".join(issues))
                return
            ok, msg = _save_new_command(data)
            if ok:
                # Reload and close
                self.app.reload_from_disk()
                self._set_msg(f"Saved to {msg}", ok=True)
                self.dismiss(None)
            else:
                self._set_msg(msg)

