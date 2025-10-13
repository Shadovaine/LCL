#=========================================================
# Command Application (Textual TUI) - Fixed Version
#=========================================================

from __future__ import annotations

# ---------------- Standard Library ----------------
from typing import Any, Dict, List, Optional
import sys
import traceback

# ---------------- Third-Party ----------------
# Textual UI
from textual.app import App, ComposeResult
from textual.widgets import Input, Static, DataTable, Footer, Label
from textual.containers import Horizontal, Vertical

# ---------------- Local Imports ----------------
from .models import STRICT_CATEGORIES, ALLOWED_CATEGORIES
from .screens.menu import MenuScreen

#=========================================================
# Configuration
#=========================================================
SEARCH_PLACEHOLDER = "Search by name, category, description, or option…"

#=========================================================
# Main TUI Application
#=========================================================
class CommandApp(App):
    """Textual application for the Linux Command Library."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #top_bar {
        height: 3;
        padding: 0 1;
        content-align: left middle;
    }
    #search_input {
        width: 1fr;
    }
    #results_section {
        width: 50%;
        layout: vertical;
        border: round $accent;
        padding: 1;
        height: 1fr;
    }
    #results_title {
        height: 1;
        content-align: center middle;
        text-style: bold;
    }
    #results {
        height: 1fr;
    }
    #body {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }
    #details_section {
        width: 50%;
        layout: vertical;
        border: round $accent;
        padding: 1;
        height: 1fr;
    }
    #details_title {
        height: 1;
        content-align: center middle;
        text-style: bold;
    }
    #details_content {
        height: 1fr;
        layout: vertical;
        overflow-y: auto;
    }
    .detail_box {
        border: round $accent;
        padding: 1;
        margin: 0 0 1 0;
    }
    .detail_box_compact {
        border: round $accent;
        padding: 1;
        margin: 0 0 1 0;
        height: 8;  /* Increased from 6 to 8 - much more room for content */
    }
    .detail_box_large {
        border: round $accent;
        padding: 1;
        margin: 0 0 1 0;
        height: 12;  /* Good size for scrollable content */
        overflow-y: auto;  /* Scrollable within the box */
    }
    .detail_header {
        background: $accent;
        color: white;
        text-style: bold;
        height: 1;
        content-align: left middle;
        padding: 0 1;
    }
    .detail_content {
        height: auto;
        padding: 1;
        background: $surface;
    }
    .detail_content_scrollable {
        height: 1fr;
        padding: 1;
        background: $surface;
        overflow-y: auto;
    }
    """

    BINDINGS = [
        ("m", "open_menu", "m: menu"),
        ("r", "reload_data", "r: reload"),
        ("q", "quit", "q: quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.docs: List[Dict[str, Any]] = []
        self.filtered_docs: List[Dict[str, Any]] = []
        self._search_performed: bool = False

    # --------------- Compose UI ---------------
    def compose(self) -> ComposeResult:
        with Horizontal(id="top_bar"):
            search_input = Input(
                placeholder=SEARCH_PLACEHOLDER,
            )
            search_input.id = "search_input"
            yield search_input

        with Horizontal(id="body"):
            with Vertical(id="results_section"):
                yield Label("Commands", id="results_title")
                yield DataTable(id="results")
            
            with Vertical(id="details_section"):
                yield Label("Details", id="details_title")
                with Vertical(id="details_content"):
                    yield Static("Navigate commands with arrow keys to see details.", id="initial_message")

        yield Footer()

    # --------------- Lifecycle ---------------
    def on_mount(self) -> None:
        table = self.query_one("#results", DataTable)
        table.add_columns("Name", "Category", "Description")
        self.query_one("#search_input", Input).focus()
        self.load_data()

    def load_data(self) -> None:
        """Load YAML data"""
        from .yamlio import load_all_commands
        self.docs = load_all_commands()
        
        if self.docs:
            table = self.query_one("#results", DataTable)
            table.clear()
            for doc in self.docs[:100]:  
                table.add_row(
                    doc.get("name", ""),
                    doc.get("category", ""),
                    doc.get("description", "")[:50] + "..." if len(doc.get("description", "")) > 50 else doc.get("description", "")
                )
            self.filtered_docs = self.docs[:100].copy()
        else:
            # If no docs loaded, show empty table
            table = self.query_one("#results", DataTable)
            table.clear()
            self.filtered_docs = []

    # --------------- Events ---------------
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search"""
        if event.input.id == "search_input":
            self._search_performed = True
            self._apply_filters_and_render()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """When row is highlighted with arrow keys"""
        if self.filtered_docs and 0 <= event.cursor_row < len(self.filtered_docs):
            doc = self.filtered_docs[event.cursor_row]
            self._update_details(doc)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """When row is selected with Enter key"""
        table = self.query_one("#results", DataTable)
        row_index = table.cursor_row
        if self.filtered_docs and 0 <= row_index < len(self.filtered_docs):
            doc = self.filtered_docs[row_index]
            self._update_details(doc)

    # Add explicit key handling for Enter
    def on_key(self, event) -> None:
        """Handle key presses"""
        if event.key == "enter":
            # Check if we're focused on the results table
            table = self.query_one("#results", DataTable)
            if self.focused == table and self.filtered_docs:
                row_index = table.cursor_row
                if 0 <= row_index < len(self.filtered_docs):
                    doc = self.filtered_docs[row_index]
                    self._update_details(doc)

    # --------------- Actions ---------------
    def action_open_menu(self) -> None:
        """Open the menu screen"""
        try:
            self.push_screen(MenuScreen())
        except Exception:
            # If menu screen fails, just continue
            pass

    def action_reload_data(self) -> None:
        """Reload data"""
        self.load_data()

    # --------------- Filtering ---------------
    def _apply_filters_and_render(self) -> None:
        """Apply search filters"""
        query = self.query_one("#search_input", Input).value.strip().lower()
        
        if not query:
            self.filtered_docs = self.docs[:100].copy()
        else:
            # Exact match first
            exact_matches = [doc for doc in self.docs if doc.get("name", "").strip().lower() == query]
            if exact_matches:
                self.filtered_docs = exact_matches
            else:
                # Partial matches
                self.filtered_docs = [
                    doc for doc in self.docs
                    if (query in doc.get("name", "").lower() or 
                        query in doc.get("description", "").lower())
                ]
        
        # Update table
        table = self.query_one("#results", DataTable)
        table.clear()
        for doc in self.filtered_docs:
            table.add_row(
                doc.get("name", ""),
                doc.get("category", ""),
                doc.get("description", "")[:50] + "..." if len(doc.get("description", "")) > 50 else doc.get("description", "")
            )

    # --------------- Details ---------------
    def _update_details(self, doc: Dict[str, Any]) -> None:
        """Update the details panel with command info from YAML"""
        try:
            details_content = self.query_one("#details_content")
            details_content.remove_children()
            
            # Extract data
            name = str(doc.get("name", "Unknown Command"))
            category = str(doc.get("category", "Unknown Category"))
            description = str(doc.get("description", "No description available"))
            options = doc.get("options", [])
            examples = doc.get("examples", [])
            
            # Command Name Box (COMPACT but taller)
            name_box = Vertical(
                Static("Command Name", classes="detail_header"),
                Static(name, classes="detail_content"),
                classes="detail_box_compact"
            )
            details_content.mount(name_box)
            
            # Category Box (COMPACT but taller)
            category_box = Vertical(
                Static("Category", classes="detail_header"),
                Static(category, classes="detail_content"),
                classes="detail_box_compact"
            )
            details_content.mount(category_box)
            
            # Description Box (COMPACT but taller)
            desc_box = Vertical(
                Static("Description", classes="detail_header"),
                Static(description, classes="detail_content"),
                classes="detail_box_compact"
            )
            details_content.mount(desc_box)
            
            # Options Box (LARGE with scrolling)
            options_widgets = [Static("Options with Explanations", classes="detail_header")]
            
            if options and isinstance(options, list):
                for option in options:
                    if isinstance(option, dict):
                        flag = option.get("flag", "")
                        explains = option.get("explains", "")
                        if flag and explains:
                            options_widgets.append(Static(f"• {flag}: {explains}", classes="detail_content"))
                        elif flag:
                            options_widgets.append(Static(f"• {flag}", classes="detail_content"))
            
            if len(options_widgets) == 1:  # Only header was added
                options_widgets.append(Static("No options available", classes="detail_content"))
            
            options_box = Vertical(*options_widgets, classes="detail_box_large")
            details_content.mount(options_box)
            
            # Examples Box (LARGE with scrolling)
            examples_widgets = [Static("Examples", classes="detail_header")]
            
            if examples and isinstance(examples, list):
                for example in examples:
                    examples_widgets.append(Static(str(example), classes="detail_content"))  # Removed the '$ ' prefix
            
            if len(examples_widgets) == 1:  # Only header was added
                examples_widgets.append(Static("No examples available", classes="detail_content"))
            
            examples_box = Vertical(*examples_widgets, classes="detail_box_large")
            details_content.mount(examples_box)
            
        except Exception as e:
            details_content = self.query_one("#details_content")
            details_content.remove_children()
            error_box = Vertical(
                Static("ERROR", classes="detail_header"),
                Static(f"Error: {str(e)}", classes="detail_content"),
                classes="detail_box"
            )
            details_content.mount(error_box)


#=========================================================
# Entry Point
#=========================================================
def main() -> None:
    """Main entry point for the application."""
    app = CommandApp()
    app.run()


if __name__ == "__main__":
    main()