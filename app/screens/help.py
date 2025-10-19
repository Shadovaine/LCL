#=================================================
# HELP_MD, HelpScreen
#=================================================

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen  # Change from Screen to ModalScreen
from textual.widgets import Static, Button, Markdown
from textual.containers import Vertical, Center, Middle

# Your help content
HELP_MD = """
# Linux Command Library Help

## NAVIGATION
• Use arrow keys to navigate through commands in the left panel
• Press **Enter** on a command to view detailed information
• Use the scroll bars to browse through options and examples

## SEARCH
• Type in the search box to find commands
• Exact matches appear first, followed by partial matches
• Search works on command names and descriptions

## KEYBOARD SHORTCUTS
• **m**: Open the main menu
• **r**: Reload command data from files
• **q**: Quit the application
• **ESC**: Go back to previous screen

## DETAILS PANEL
The right panel shows comprehensive information:
• **Command Name**: The actual command
• **Category**: Which category the command belongs to
• **Description**: What the command does
• **Options**: Available flags with explanations (scrollable)
• **Examples**: Real usage examples (scrollable)

## TIPS
• Commands are organized by categories like File Management, System Administration, etc.
• Each command includes practical examples you can copy and use
• Use the scroll bars in the Details panel to see all options
"""

class HelpScreen(ModalScreen[None]):  # Change to ModalScreen
    """Help screen with usage instructions."""

    CSS = """
    HelpScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.8);
    }
    
    #help_container {
        width: 80;
        height: 30;
        border: round #0178d4;      /* Blue border */
        padding: 2;
        background: $surface;
    }
    
    #help_title {
        text-align: center;
        text-style: bold;
        color: #0178d4;             /* Blue title */
        margin: 0 0 1 0;
        height: 1;
    }
    
    #help_content {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
        border: round #0178d4;      /* Blue content border */
        background: $background;
    }
    
    .close_button {
        width: 20;
        margin: 1 0 0 0;
        border: round #0178d4;      /* Blue button border */
    }
    
    .close_button:focus {
        border: thick #0178d4;      /* Blue focus */
        background: #0178d4 20%;
    }
    """

    BINDINGS = [
        ("escape", "close", "ESC: close"),
        ("q", "close", "q: close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Center():
            with Middle():
                with Vertical(id="help_container"):
                    yield Static("Help", id="help_title")
                    yield Markdown(HELP_MD, id="help_content")
                    yield Button("Close", id="close_btn", classes="close_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close_btn":
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)