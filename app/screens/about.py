#==================================================
# ABOUT_MD, AboutScreen
#==================================================

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen  # Make sure this is ModalScreen, not Screen
from textual.widgets import Static, Button, Markdown
from textual.containers import Vertical, Center, Middle

class AboutScreen(ModalScreen[None]):  # Must be ModalScreen
    """About screen with application information."""

    CSS = """
    AboutScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.8);  # Semi-transparent overlay
    }
    
    #about_container {
        width: 70;
        height: 25;
        border: round $accent;
        padding: 2;
        background: $surface;
    }
    
    #about_title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin: 0 0 1 0;
        height: 1;
    }
    
    #about_content {
        height: 1fr;
        overflow-y: auto;
        padding: 1;
        border: round $primary;
        background: $background;
    }
    
    .close_button {
        width: 20;
        margin: 1 0 0 0;
    }
    """

    BINDINGS = [
        ("escape", "close", "ESC: close"),
        ("q", "close", "q: close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the about screen."""
        about_text = """
# Linux Command Library

**Version:** 2.0  
A comprehensive command reference tool for Linux users

## 🚀 FEATURES
• 500+ Linux commands organized by category
• Detailed explanations and usage examples
• Fast search and navigation interface
• Clean, responsive TUI design

## 📚 CATEGORIES
• File & Directory Management
• System Administration
• Network & Security Tools
• And many more...

## 💡 PURPOSE
Created to help Linux users quickly find command syntax,
options, and real-world examples.

Enjoy exploring Linux commands! 🐧
        """

        with Center():
            with Middle():
                with Vertical(id="about_container"):
                    yield Static("About", id="about_title")
                    yield Markdown(about_text.strip(), id="about_content")
                    yield Button("Close", id="close_btn", classes="close_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "close_btn":
            self.dismiss(None)

    def action_close(self) -> None:
        """Close the about screen."""
        self.dismiss(None)