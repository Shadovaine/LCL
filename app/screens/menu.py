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
from pathlib import Path
import os
import datetime
import shutil
import subprocess

def is_admin() -> bool:
    """
    Check if current user has admin privileges.
    Admin can be enabled by:
    1. Being user 'shadovaine'
    2. Having ~/.lcl_admin file
    3. Setting LCL_ADMIN=true environment variable
    """
    # Method 1: Check username
    if os.getenv('USER') == 'shadovaine':
        return True
    
    # Method 2: Check for admin config file
    admin_file = Path.home() / '.lcl_admin'
    if admin_file.exists():
        return True
    
    # Method 3: Check environment variable
    if os.getenv('LCL_ADMIN', '').lower() in ['true', '1', 'yes']:
        return True
    
    return False


#----------------------Menu Screen----------------------
class MenuScreen(ModalScreen[None]):
    """Menu screen with options."""

    CSS = """
    MenuScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.8);
    }

    #menu_container {
        width: 50;
        height: 22;
        border: round $accent;  /* Use theme accent instead of hardcoded blue */
        padding: 2;
        background: $surface;
    }

    #menu_title {
        text-align: center;
        text-style: bold;
        color: $accent;  /* Use theme accent */
        margin: 0 0 1 0;
        height: 1;
    }

    .menu_button {
        width: 100%;
        margin: 0 0 1 0;
        border: round $accent;  /* Use theme accent */
        height: 3;
    }

    .menu_button:hover {
        background: $accent 30%;  /* Use theme accent */
    }

    .menu_button:focus {
        border: thick $accent;  /* Use theme accent */
        background: $accent 20%;
    }
    """

    BINDINGS = [
        ("escape", "close", "ESC: close"),
        ("q", "close", "q: close"),
        ("tab", "focus_next", "tab: next"),
        ("shift+tab", "focus_previous", "shift+tab: prev"),
        ("up", "focus_previous", "↑: prev"),     # Add arrow key navigation
        ("down", "focus_next", "↓: next"),       # Add arrow key navigation
    ]

    def __init__(self) -> None:
        super().__init__()
        self._buttons = []  # Track button order for navigation

    def compose(self) -> ComposeResult:
        """Compose the menu screen."""
        with Center():
            with Middle():
                with Vertical(id="menu_container"):
                    yield Static("Menu", id="menu_title")
                    yield Button("Help", id="menu_help", classes="menu_button")
                    yield Button("About", id="menu_about", classes="menu_button")
                    
                    # Debug: Always show the admin button for now
                    admin_check = is_admin()
                    self.log(f"Admin check result: {admin_check}")  # Debug log
                    
                    if admin_check:
                        yield Button("New Command (admin)", id="menu_new", classes="menu_button")
                    
                    yield Button("Close", id="menu_close", classes="menu_button")

    def on_mount(self) -> None:
        """Focus first button when menu opens and collect button references."""
        try:
            # Collect all buttons in order
            self._buttons = [
                self.query_one("#menu_help", Button),
                self.query_one("#menu_about", Button),
            ]
            
            # Add admin button if it exists
            try:
                admin_button = self.query_one("#menu_new", Button)
                self._buttons.append(admin_button)
            except:
                pass  # Admin button doesn't exist
                
            # Add close button
            self._buttons.append(self.query_one("#menu_close", Button))
            
            # Focus first button
            if self._buttons:
                self._buttons[0].focus()
                
        except Exception as e:
            self.log(f"Error in on_mount: {e}")

    def action_focus_next(self) -> None:
        """Custom tab navigation - next button."""
        try:
            current_focus = self.focused
            # Ensure current_focus is a Button before using it with the typed list
            if isinstance(current_focus, Button) and current_focus in self._buttons:
                current_index = self._buttons.index(current_focus)
                next_index = (current_index + 1) % len(self._buttons)
                self._buttons[next_index].focus()
            else:
                # If nothing focused or focus lost, focus first button
                if self._buttons:
                    self._buttons[0].focus()
        except Exception as e:
            self.log(f"Error in focus_next: {e}")
    def action_focus_previous(self) -> None:
        """Custom tab navigation - previous button."""
        try:
            current_focus = self.focused
            # Ensure current_focus is a Button before using it with the typed list
            if isinstance(current_focus, Button) and current_focus in self._buttons:
                current_index = self._buttons.index(current_focus)
                prev_index = (current_index - 1) % len(self._buttons)
                self._buttons[prev_index].focus()
            else:
                # If nothing focused, focus last button
                if self._buttons:
                    self._buttons[-1].focus()
        except Exception as e:
            self.log(f"Error in focus_previous: {e}")
            self.log(f"Error in focus_previous: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        bid = event.button.id
        app = self.app

        if bid == "menu_close":
            self.dismiss(None)
        elif bid == "menu_help":
            from .help import HelpScreen
            app.push_screen(HelpScreen())
        elif bid == "menu_about":
            from .about import AboutScreen
            app.push_screen(AboutScreen())
        elif bid == "menu_new":
            # Use your existing template
            self.dismiss(None)  # Close menu first
            self._open_command_template()

    def _open_command_template(self) -> None:
        """Open the existing command template for editing."""
        try:
            # Path to your existing template
            template_path = Path("templates/command_template.yml")
            
            if not template_path.exists():
                self.app.notify("Template not found at templates/command_template.yml", severity="error")
                return
            
            # Create a copy for new command
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_command_path = Path(f"templates/new_command_{timestamp}.yml")
            
            # Copy template to new file
            shutil.copy2(template_path, new_command_path)
            
            self.app.notify(f"New command template created: {new_command_path}")
            
            # Try to open in editor
            self._open_in_editor(new_command_path)
            
        except Exception as e:
            self.app.notify(f"Error creating command template: {e}", severity="error")

    def _open_in_editor(self, file_path: Path) -> None:
        """Try to open file in available text editor."""
        import os
        import subprocess
        
        # For TUI apps, we need to handle editors differently
        try:
            # First, try GUI editors that won't interfere with our TUI
            gui_editors = ['code', 'gedit', 'kate', 'mousepad', 'leafpad']
            
            for editor in gui_editors:
                try:
                    # Check if GUI editor exists
                    subprocess.run(['which', editor], check=True, capture_output=True)
                    
                    # Open the file in background without blocking TUI
                    subprocess.Popen([editor, str(file_path)], 
                                   stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    
                    self.app.notify(f"Opening template in {editor}")
                    return
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            # If no GUI editor found, suggest terminal editor after closing TUI
            self.app.notify(f"Template created at: {file_path}")
            self.app.notify("Close LCL and edit with: nano " + str(file_path))
            
        except Exception as e:
            self.app.notify(f"Template created at: {file_path}")
            self.app.notify("Please edit the file manually")

    def action_close(self) -> None:
        """Close the menu screen."""
        self.dismiss(None)
