#=========================================================
# Textual UI, Menu Screen
#=========================================================

from __future__ import annotations

#----------------------Textual UI----------------------
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Vertical
from ..config import is_admin


#----------------------Local Library----------------------
from ..screens.help import HelpScreen
from ..screens.about import AboutScreen
from ..screens.new_command import NewCommandScreen
# from ..screens.suggest import SuggestCommandScreen  # DISABLED for security

#----------------------Menu Screen----------------------
class MenuScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    Screen {
        width: 48;
        align: center middle;
        padding: 1 0;
    }
    .title { width: 100%; content-align: center middle; margin-bottom: 1; }
    #menu_stack { align: center middle; }
    #menu_stack > Button { width: 36; margin: 1 0; content-align: center middle; }
    """

    def compose(self) -> ComposeResult:
        yield Static("Menu", classes="title")
        with Vertical(id="menu_stack"):
            # Suggest feature removed for security reasons
            
            yield Button("Help", id="menu_help")
            yield Button("About", id="menu_about")
            # Admin-only "New Command"
            if is_admin():
                yield Button("Reload commands", id="menu_reload")  # type: ignore
                yield Button("New Command (admin)", id="menu_new")
            yield Button("Close", id="menu_close")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        app: CommandApp = self.app  # type: ignore

        if bid == "menu_close":
            self.dismiss(None)
        elif bid == "menu_reload":
            if not is_admin():
                return
            await app.load_commands()
        elif bid == "menu_help":
            app.push_screen(HelpScreen())
            self.dismiss(None)
        elif bid == "menu_about":
            app.push_screen(AboutScreen())
            self.dismiss(None)
        elif bid == "menu_new":
            if app.is_admin:
                app.push_screen(NewCommandScreen())
                self.dismiss(None)
            else:
                app.status.update("Admin only. Set LCL_ADMIN=1 or provide a valid LCL_ADMIN_TOKEN.")
