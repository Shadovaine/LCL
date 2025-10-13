#==================================================
# ABOUT_MD, keys_markdown, AboutScreen
#==================================================

from __future__ import annotations

#--------------------Textual UI IMPORTS--------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

#--------------------ABOUT_MD-------------------
ABOUT_MD = """
# Linux Command Library — About

I built *Linux Command Library* to transform a static cheatsheet into a living, interactive way to learn Bash.
I am ShadoVaine, and my goal was to create a TUI (Text User Interface) that runs directly inside a Bash terminal.
The Library contains over 180 Linux commands, all organized by category. Users can search by name, category, description,
 or even by specific options.
As I worked to become more proficient in Linux, I wanted to create a resource that would help others learn alongside me.
My hope is that the Linux Command Library supports you on your own journey.

## What it does
- Curated commands organized by category
- Examples, usage/syntax, options (with meanings)
- Fast fuzzy search
- Add new commands with a form


## Keys
{keys_md}

*Remain curious. Learn daily.*
"""

#-------------------_keys_markdown-------------------
def _keys_markdown(app: "CommandApp") -> str:
    lines = []
    for key, action, desc in app.BINDINGS:
        if key and desc:
            lines.append(f"- `{key}` — {desc}")
    return "\n".join(lines)

#-------------------AboutScreen-------------------
class AboutScreen(ModalScreen[None]):
    def compose(self) -> ComposeResult:
        text = ABOUT_MD.replace("{keys_md}", _keys_markdown(self.app))
        try:
            yield Markdown(text, show_table_of_contents=False)
        except TypeError:
            # Older Textual: Markdown widget doesn’t accept show_table_of_contents
            yield Markdown(text)
        yield Button("close", id="about_close")

    def on_button_pressed(self, ev: Button.Pressed):
        if (ev.button.id or "") == "about_close":
            self.dismiss(None)