#=========================================================
# Textual UI, Menu Screen
#=========================================================

from __future__ import annotations

#----------------------Textual UI----------------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Vertical, Center, Middle

#----------------------Local Library----------------------
from ..config import is_admin


#----------------------Menu Screen----------------------
class MenuScreen(ModalScreen[None]):
    """Menu screen - no search bar should appear here."""

    CSS = """
    MenuScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.8);
    }
    
    #menu_container {
        width: 60;
        height: auto;
        border: round $accent;
        padding: 2;
        background: $surface;
    }
    
    #menu_title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 2 0;
    }
    
    .menu_button {
        width: 100%;
        margin: 1 0;
        height: 3;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the menu screen - NO search bar."""
        with Center():
            with Middle():
                with Vertical(id="menu_container"):
                    yield Static("Menu", id="menu_title")
                    yield Button("Help", id="menu_help", classes="menu_button")
                    yield Button("About", id="menu_about", classes="menu_button")
                    if is_admin():
                        # Remove: yield Button("Reload commands", id="menu_reload", classes="menu_button")
                        yield Button("New Command (admin)", id="menu_new", classes="menu_button")
                    yield Button("Close", id="menu_close", classes="menu_button")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        bid = event.button.id
        app = self.app  # type: ignore

        if bid == "menu_close":
            self.dismiss(None)
        elif bid == "menu_help":
            from .help import HelpScreen
            app.push_screen(HelpScreen())
            # Remove: self.dismiss(None)  # Don't dismiss here!
        elif bid == "menu_about":
            from .about import AboutScreen
            app.push_screen(AboutScreen())
            # Remove: self.dismiss(None)  # Don't dismiss here!
        elif bid == "menu_new":
            if app.is_admin:
                from .new_command import NewCommandScreen
                app.push_screen(NewCommandScreen())
                # Remove: self.dismiss(None)  # Don't dismiss here!
