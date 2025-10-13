#=================================================
# HELP_MD, HelpScreen
#=================================================

from __future__ import annotations

#--------------------Textual UI IMPORTS--------------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

#--------------------ABOUT_MD------------------------------
HELP_MD = """
# Help

**Search**
- Type in the box then press **Enter** to filter
- Results grouped by category; ↑/↓ to move, Enter to show details

**Common Keys**
- `/` focus search, `m` menu, `q` quit, `esc` clear search
"""

#--------------------HelpScreen---------------------------
class HelpScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        try:
            yield Markdown(HELP_MD, show_table_of_contents=False)
        except TypeError:
            # Older Textual: Markdown widget doesn’t accept show_table_of_contents
            yield Markdown(HELP_MD)
        yield Button("close", id="help_close")

    def on_button_pressed(self, ev: Button.Pressed):
        if (ev.button.id or "") == "help_close":
            self.dismiss(None)